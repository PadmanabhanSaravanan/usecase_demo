import React, { useEffect, useState } from "react";
import TodoPage from "./TodoPage";
import LoginPage from "./LoginPage";
import RegisterPage from "./RegisterPage";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [flags, setFlags] = useState({});
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState("home");
  const [loggedIn, setLoggedIn] = useState(!!localStorage.getItem("token"));
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  useEffect(() => {
    fetch(`${BACKEND_URL}/feature-flags/`)
      .then((res) => res.json())
      .then((data) => {
        setFlags(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    setLoggedIn(!!token);
  }, [token]);

  const handleLogin = () => {
    setToken(localStorage.getItem("token") || "");
    setLoggedIn(true);
    setPage("todos");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
    setLoggedIn(false);
    setPage("login");
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: 24 }}>
      <h1>Feature Flag Demo (React + FastAPI)</h1>
      <nav>
        <button onClick={() => setPage("home")}>Home</button>
        <button onClick={() => setPage("todos")}>Todos</button>
        <button onClick={() => setPage("login")}>Login</button>
        <button onClick={() => setPage("register")}>Register</button>
        {loggedIn && <button onClick={handleLogout}>Logout</button>}
      </nav>
      <hr />
      {page === "home" && (
        <>
          <pre>{JSON.stringify(flags, null, 2)}</pre>
          {flags["feature-login"] && <button onClick={() => setPage("login")}>Login</button>}
          {!flags["feature-login"] && <div>Login feature is disabled.</div>}
        </>
      )}
      {page === "todos" && <TodoPage token={token} onLogout={handleLogout} />}
      {page === "login" && flags["feature-login"] && <LoginPage onLogin={handleLogin} />}
      {page === "login" && !flags["feature-login"] && <div>Login feature is disabled.</div>}
      {page === "register" && <RegisterPage onRegister={() => setPage("login")} />}
      {/* Uncomment below if you have a DarkModeToggle component */}
      {/* {flags["feature-darkmode"] && <DarkModeToggle />} */}
    </div>
  );
}

export default App;
