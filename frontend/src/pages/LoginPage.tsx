import { useState } from "react";
import { apiRequest } from "../api/client";
import { setToken } from "../auth/token";
import { Link, useNavigate } from "react-router-dom";

// backend return type
type LoginResponse = {
  user_id: number;
  email: string;
};

// return JSX
export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await apiRequest<LoginResponse>("/auth/login", "POST", {
        email,
        password,
      });
      // The backend currently returns user info but no token.
      // Use a temporary token derived from user_id so the app
      // can treat the user as "logged in" on the client side.
      setToken(String(res.user_id));
      try {
        localStorage.setItem("tj_user_email", res.email);
      } catch {}
      if (typeof navigate === "function") {
        navigate("/");
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Login failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "64px auto", padding: 24 }}>
      <h1 style={{ marginBottom: 16 }}>Login</h1>
      <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            style={{ padding: "8px 10px" }}
          />
        </label>

        <label style={{ display: "grid", gap: 6 }}>
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
            style={{ padding: "8px 10px" }}
          />
        </label>

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "10px 12px",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      {error ? (
        <p style={{ color: "crimson", marginTop: 12 }}>{error}</p>
      ) : null}
      <p style={{ marginTop: 16 }}>
        Don't have an account?{" "}
        <Link to="/register">Create one</Link>
      </p>
    </div>
  );
}

