import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { fetchDepartments, fetchUsers } from "../api/client";

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchDepartments(), fetchUsers()])
      .then(([depts, usrs]) => {
        setDepartments(depts);
        setUsers(usrs);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>BPIT ERP</h1>
          <span className="subtitle">Core Module</span>
        </div>
        <nav className="module-nav">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/students">Students</Link>
        </nav>
        <div className="user-box">
          <div>
            <strong>{user?.username}</strong>
            <div className="subtitle">{user?.role === "ADMIN" ? "Administrator" : user?.role}</div>
          </div>
          <button onClick={logout}>Log out</button>
        </div>
      </header>

      <main className="content">
        <section className="card">
          <h2>Departments</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>HOD</th>
                  <th>Members</th>
                </tr>
              </thead>
              <tbody>
                {departments.map((d) => (
                  <tr key={d.id}>
                    <td>{d.code}</td>
                    <td>{d.name}</td>
                    <td>{d.hod_name || "—"}</td>
                    <td>{d.member_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className="card">
          <h2>Users</h2>
          {loading ? (
            <p>Loading...</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.username}</td>
                    <td>{[u.first_name, u.last_name].filter(Boolean).join(" ") || "—"}</td>
                    <td>{u.role}</td>
                    <td>{u.department_code || "—"}</td>
                    <td>{u.is_active_member ? "Active" : "Inactive"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}
