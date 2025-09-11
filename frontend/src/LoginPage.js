import React, { useState, useEffect } from "react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  useEffect(() => {
    if (token) {
      onLogin && onLogin();
    }
  }, [token, onLogin]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);
    try {
      const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString()
      });
      if (res.ok) {
        const data = await res.json();
        if (data.access_token) {
          localStorage.setItem("token", data.access_token);
          setToken(data.access_token);
        } else {
          setError("No token received");
        }
      } else {
        setError("Login failed");
      }
    } catch {
      setError("Login error");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
    setUsername("");
    setPassword("");
  };

  if (token) {
    return (
      <div>
        <h2>Logged in</h2>
        <button onClick={handleLogout}>Logout</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      />
      <button type="submit">Login</button>
      {error && <div style={{color: 'red'}}>{error}</div>}
    </form>
  );
}

export default LoginPage;
