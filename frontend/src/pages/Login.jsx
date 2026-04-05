import { useState } from "react";
import "./Login.css";
import { useNavigate } from "react-router-dom"

export default function Login() {
  const navigate = useNavigate();

  const [tab, setTab] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", password: "" });

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async () => {
    if (tab === "login") {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });
      if (!res.ok) { alert("Login failed"); return; }
      const data = await res.json();
      localStorage.setItem("user_id", data.user_id);
      localStorage.setItem("username", data.username);
      localStorage.setItem("pet_name", data.pet_name);
      navigate("/dashboard");
    } else {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: form.username, email: form.email, password: form.password }),
      });
      if (!res.ok) { alert("Registration failed"); return; }
      const data = await res.json();
      localStorage.setItem("user_id", data.id);
      localStorage.setItem("username", data.username);
      localStorage.setItem("pet_name", data.pet_name);
      navigate("/dashboard");
    }
  };

  return (
    <div className="login-screen">
      <div className="login-card">

        <div className="pet-wrap">
          <div className="pet-bubble">🐣</div>
          <div className="app-name">Tamagotchi Health</div>
          <div className="app-tagline">Your morning check-in companion</div>
        </div>

        <div className="tabs">
          <button
            className={`tab ${tab === "login" ? "active" : ""}`}
            onClick={() => setTab("login")}
          >
            Sign in
          </button>
          <button
            className={`tab ${tab === "signup" ? "active" : ""}`}
            onClick={() => setTab("signup")}
          >
            Create account
          </button>
        </div>

        {tab === "login" && (
          <>
            <div className="field">
              <label>Email</label>
              <input
                name="email"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>Password</label>
              <input
                name="password"
                type="password"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
              />
            </div>
          </>
        )}

        {tab === "signup" && (
          <>
            <div className="field">
              <label>Username</label>
              <input
                name="username"
                type="text"
                placeholder="choose a username"
                value={form.username}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>Email</label>
              <input
                name="email"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={handleChange}
              />
            </div>
            <div className="field">
              <label>Password</label>
              <input
                name="password"
                type="password"
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
              />
            </div>
          </>
        )}

        <button className="login-btn" onClick={handleSubmit}>
          {tab === "login" ? "Sign in" : "Create account"}
        </button>

        <div className="divider"><span>or</span></div>

        <button className="guest-btn"
          onClick={() => navigate("/dashboard")}
        >
          Continue as guest
        </button>

      </div>
    </div>
  );
}
