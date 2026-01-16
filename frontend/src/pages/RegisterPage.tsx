import { useState } from "react";
import { apiRequest } from "../api/client";
import { Link, useNavigate } from "react-router-dom";

type RegisterResponse = {
  message: string;
};

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);
    try {
      const res = await apiRequest<RegisterResponse>("/auth/register", "POST", {
        email,
        password,
      });
      setSuccess(res.message || "Registered successfully!");
      // Navigate to login after a short delay so user can see success
      setTimeout(() => navigate("/login"), 600);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Register failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 360, margin: "64px auto", padding: 24 }}>
      <h1 style={{ marginBottom: 16 }}>Register</h1>
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
          {loading ? "Creating account..." : "Create account"}
        </button>
      </form>
      {error ? <p style={{ color: "crimson", marginTop: 12 }}>{error}</p> : null}
      {success ? <p style={{ color: "seagreen", marginTop: 12 }}>{success}</p> : null}
      <p style={{ marginTop: 16 }}>
        Already have an account?{" "}
        <Link to="/login">Login</Link>
      </p>
    </div>
  );
}

