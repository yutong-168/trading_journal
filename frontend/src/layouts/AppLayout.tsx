import { Link, Outlet, useNavigate } from "react-router-dom";
import { clearToken, getToken } from "../auth/token";

export default function AppLayout() {
  const navigate = useNavigate();
  const userId = getToken();

  function handleLogout() {
    clearToken();
    navigate("/login");
  }

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "16px 20px" }}>
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <nav style={{ display: "flex", gap: 12 }}>
          <Link to="/">Home</Link>
          <Link to="/stats">Stats</Link>
        </nav>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span style={{ color: "#555" }}>UID: {userId}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </header>
      <Outlet />
    </div>
  );
}

