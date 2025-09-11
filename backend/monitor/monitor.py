# monitor/monitor.py
import time
import threading
from dataclasses import dataclass
from typing import Dict, List, Optional
import requests
import yaml

from prometheus_client import Gauge, Counter, Summary, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from .emailer import send_email

@dataclass
class ServiceConfig:
    name: str
    url: str
    failure_threshold: int = 3
    recovery_threshold: int = 1
    timeout_seconds: int = 3

@dataclass
class EmailConfig:
    smtp_host: str
    smtp_port: int
    use_tls: bool
    username: str
    password: str
    from_email: str
    to_emails: List[str]

class HealthMonitor:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._stop = threading.Event()
        self.interval_seconds = 10
        self.services: List[ServiceConfig] = []
        self.email_cfg: Optional[EmailConfig] = None

        # Prometheus metrics (default registry)
        self.g_service_up = Gauge("service_up", "1=up, 0=down", ["service"])
        self.g_last_check_ts = Gauge("service_last_check_timestamp", "Epoch timestamp of last check", ["service"])
        self.c_failures_total = Counter("service_failures_total", "Total failures per service", ["service"])
        self.s_latency = Summary("service_check_latency_seconds", "Latency of health checks", ["service"])

        # State trackers for alert de-dup
        self._state: Dict[str, Dict[str, int | bool]] = {}
        self._load_config()

    def _load_config(self):
        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)

        self.interval_seconds = int(data.get("interval_seconds", 10))

        email = data.get("email", {})
        if email:
            self.email_cfg = EmailConfig(
                smtp_host=email["smtp_host"],
                smtp_port=int(email["smtp_port"]),
                use_tls=bool(email.get("use_tls", True)),
                username=email["username"],
                password=email["password"],
                from_email=email["from_email"],
                to_emails=list(email["to_emails"]),
            )

        self.services = []
        for s in data.get("services", []):
            self.services.append(ServiceConfig(
                name=s["name"],
                url=s["url"],
                failure_threshold=int(s.get("failure_threshold", 3)),
                recovery_threshold=int(s.get("recovery_threshold", 1)),
                timeout_seconds=int(s.get("timeout_seconds", 3)),
            ))
            # init tracking
            self._state[s["name"]] = {
                "up": True,                 # assume up until proven otherwise
                "consec_fail": 0,
                "consec_ok": 0,
            }
            # set initial metrics
            self.g_service_up.labels(service=s["name"]).set(1)
            self.g_last_check_ts.labels(service=s["name"]).set(time.time())

    def _alert(self, subject: str, body: str):
        if not self.email_cfg:
            return
        send_email(
            smtp_host=self.email_cfg.smtp_host,
            smtp_port=self.email_cfg.smtp_port,
            use_tls=self.email_cfg.use_tls,
            username=self.email_cfg.username,
            password=self.email_cfg.password,
            from_email=self.email_cfg.from_email,
            to_emails=self.email_cfg.to_emails,
            subject=subject,
            body=body,
        )

    def _check_once(self, svc: ServiceConfig):
        start = time.time()
        ok = False
        try:
            resp = requests.get(svc.url, timeout=svc.timeout_seconds)
            ok = resp.status_code < 500
        except requests.RequestException:
            ok = False
        finally:
            latency = time.time() - start
            self.s_latency.labels(service=svc.name).observe(latency)
            self.g_last_check_ts.labels(service=svc.name).set(time.time())

        st = self._state[svc.name]
        if ok:
            st["consec_ok"] = st.get("consec_ok", 0) + 1
            st["consec_fail"] = 0
            # Recovery alert?
            if st["up"] is False and st["consec_ok"] >= svc.recovery_threshold:
                st["up"] = True
                self.g_service_up.labels(service=svc.name).set(1)
                self._alert(
                    subject=f"[RECOVERED] {svc.name} is UP",
                    body=f"Service {svc.name} recovered. URL: {svc.url}"
                )
        else:
            st["consec_fail"] = st.get("consec_fail", 0) + 1
            st["consec_ok"] = 0
            self.c_failures_total.labels(service=svc.name).inc()
            # Down alert?
            if st["up"] is True and st["consec_fail"] >= svc.failure_threshold:
                st["up"] = False
                self.g_service_up.labels(service=svc.name).set(0)
                self._alert(
                    subject=f"[DOWN] {svc.name} is UNHEALTHY",
                    body=f"Service {svc.name} appears DOWN.\nURL: {svc.url}\nConsecutive failures: {st['consec_fail']}"
                )

    def start(self):
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    def stop(self):
        self._stop.set()

    def _loop(self):
        # simple loop that checks all services every interval
        while not self._stop.is_set():
            for svc in self.services:
                self._check_once(svc)
            time.sleep(self.interval_seconds)

# FastAPI integration helpers
from fastapi import APIRouter, Response

router = APIRouter()
_MONITOR: Optional[HealthMonitor] = None

@router.on_event("startup")
def _startup_monitor():
    global _MONITOR
    if _MONITOR is None:
        _MONITOR = HealthMonitor(config_path="monitor/config.yaml")
        _MONITOR.start()

@router.on_event("shutdown")
def _shutdown_monitor():
    if _MONITOR:
        _MONITOR.stop()

@router.get("/")
def metrics():
    data = generate_latest()  # default registry
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
