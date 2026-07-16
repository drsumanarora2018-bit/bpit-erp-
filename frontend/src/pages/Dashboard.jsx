import { useEffect, useState } from "react";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

const ROLE_LABELS = {
  ADMIN: "Administrator",
  HOD: "Head of Department",
  FACULTY: "Faculty",
  STUDENT: "Student",
  ACCOUNTS: "Accounts / Admin Staff",
};

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [users, setUsers] = useState([]);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    client
      .get("/departments/")
      .then((res) => setDepartments(res.data))
      .catch(() => {});

    if (user?.role === "ADMIN") {
      client
        .get("/users/")
        .then((res) => setUsers(res.data))
        .catch(() => {})
        .finally(() => setLoadingData(false));
    } else {
      setLoadingData(false);
    }
  }, [user]);

  return (
    <div className="dashboard">
      <header className="topbar">
        <div>
          <h2>BPIT ERP</h2>
          <span className="muted">Core Module</span>
        </div>
        <div className="user-chip">
          <div>
            <strong>{user?.first_name || user?.username}</strong>
            <div className="muted">{ROLE_LABELS[user?.role] || user?.role}</div>
          </div>
          <button onClick={logout}>Log out</button>
        </div>
      </header>

      <section className="card">
        <h3>Departments</h3>
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
      </section>

      {user?.role === "ADMIN" && (
        <section className="card">
          <h3>Users {loadingData && <span className="muted">(loading…)</span>}</h3>
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
                  <td>{`${u.first_name} ${u.last_name}`.trim() || "—"}</td>
                  <td>{ROLE_LABELS[u.role] || u.role}</td>
                  <td>{u.department_code || "—"}</td>
                  <td>{u.is_active ? "Active" : "Disabled"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {user?.role !== "ADMIN" && (
        <section className="card">
          <h3>Your Profile</h3>
          <p>
            <strong>Email:</strong> {user?.email || "—"}
          </p>
          <p>
            <strong>Department:</strong> {user?.department_code || "—"}
          </p>
          {user?.enrollment_no && (
            <p>
              <strong>Enrollment No:</strong> {user.enrollment_no}
            </p>
          )}
        </section>
      )}
    </div>
  );
}
