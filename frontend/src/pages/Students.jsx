import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  fetchStudents,
  fetchDepartments,
  createStudent,
  deleteStudent,
  bulkImportStudents,
} from "../api/client";

const emptyForm = {
  enrollment_no: "", name: "", department: "", batch: "",
  semester: 1, section: "", phone: "", email: "",
};

export default function Students() {
  const { user, logout } = useAuth();
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ department: "", batch: "", section: "", search: "" });
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [importSummary, setImportSummary] = useState(null);
  const [importBusy, setImportBusy] = useState(false);

  const loadStudents = useCallback(() => {
    setLoading(true);
    const params = {};
    if (filters.department) params.department = filters.department;
    if (filters.batch) params.batch = filters.batch;
    if (filters.section) params.section = filters.section;
    if (filters.search) params.search = filters.search;
    fetchStudents(params)
      .then(setStudents)
      .finally(() => setLoading(false));
  }, [filters]);

  useEffect(() => {
    fetchDepartments().then(setDepartments);
  }, []);

  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  async function handleAddStudent(e) {
    e.preventDefault();
    setFormError("");
    try {
      await createStudent(form);
      setForm(emptyForm);
      setShowForm(false);
      loadStudents();
    } catch (err) {
      const data = err?.response?.data;
      setFormError(data ? JSON.stringify(data) : "Could not create student");
    }
  }

  async function handleDelete(id) {
    if (!window.confirm("Delete this student?")) return;
    await deleteStudent(id);
    loadStudents();
  }

  async function handleImport(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImportBusy(true);
    setImportSummary(null);
    try {
      const result = await bulkImportStudents(file);
      setImportSummary(result.summary);
      loadStudents();
    } catch (err) {
      setImportSummary({ error: err?.response?.data?.detail || "Import failed" });
    } finally {
      setImportBusy(false);
      e.target.value = "";
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>BPIT ERP</h1>
          <span className="subtitle">Student Records</span>
        </div>
        <nav className="module-nav">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/students">Students</Link>
          <Link to="/results">Results</Link>
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
          <h2>Students</h2>

          <div className="filters">
            <select
              value={filters.department}
              onChange={(e) => setFilters((f) => ({ ...f, department: e.target.value }))}
            >
              <option value="">All Departments</option>
              {departments.map((d) => (
                <option key={d.id} value={d.code}>{d.code}</option>
              ))}
            </select>
            <input
              placeholder="Batch (e.g. 2024-28)"
              value={filters.batch}
              onChange={(e) => setFilters((f) => ({ ...f, batch: e.target.value }))}
            />
            <input
              placeholder="Section"
              value={filters.section}
              onChange={(e) => setFilters((f) => ({ ...f, section: e.target.value }))}
            />
            <input
              placeholder="Search name / enrollment / email"
              value={filters.search}
              onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
            />
          </div>

          <div className="form-row">
            <button className="btn-primary" onClick={() => setShowForm((s) => !s)}>
              {showForm ? "Cancel" : "+ Add Student"}
            </button>
            <label className="btn-secondary" style={{ cursor: "pointer" }}>
              {importBusy ? "Importing..." : "Bulk Import (CSV/Excel)"}
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                style={{ display: "none" }}
                onChange={handleImport}
                disabled={importBusy}
              />
            </label>
          </div>

          {importSummary && (
            <div className="import-summary">
              {importSummary.error
                ? `Error: ${importSummary.error}`
                : `Imported: ${importSummary.created} created, ${importSummary.updated} updated, ${importSummary.failed} failed (of ${importSummary.total_rows} rows)`}
            </div>
          )}

          {showForm && (
            <form onSubmit={handleAddStudent} style={{ marginBottom: "1rem" }}>
              {formError && <div className="error-banner">{formError}</div>}
              <div className="form-row">
                <label>
                  Enrollment No
                  <input
                    required
                    value={form.enrollment_no}
                    onChange={(e) => setForm((f) => ({ ...f, enrollment_no: e.target.value }))}
                  />
                </label>
                <label>
                  Name
                  <input
                    required
                    value={form.name}
                    onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                  />
                </label>
                <label>
                  Department
                  <select
                    required
                    value={form.department}
                    onChange={(e) => setForm((f) => ({ ...f, department: e.target.value }))}
                  >
                    <option value="">Select</option>
                    {departments.map((d) => (
                      <option key={d.id} value={d.id}>{d.code}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Batch
                  <input
                    required
                    placeholder="2024-28"
                    value={form.batch}
                    onChange={(e) => setForm((f) => ({ ...f, batch: e.target.value }))}
                  />
                </label>
              </div>
              <div className="form-row">
                <label>
                  Semester
                  <input
                    type="number"
                    min="1"
                    max="8"
                    value={form.semester}
                    onChange={(e) => setForm((f) => ({ ...f, semester: e.target.value }))}
                  />
                </label>
                <label>
                  Section
                  <input
                    value={form.section}
                    onChange={(e) => setForm((f) => ({ ...f, section: e.target.value }))}
                  />
                </label>
                <label>
                  Phone
                  <input
                    value={form.phone}
                    onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                  />
                </label>
                <label>
                  Email
                  <input
                    type="email"
                    value={form.email}
                    onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                  />
                </label>
              </div>
              <button className="btn-primary" type="submit">Save Student</button>
            </form>
          )}

          {loading ? (
            <p>Loading...</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Enrollment No</th>
                  <th>Name</th>
                  <th>Dept</th>
                  <th>Batch</th>
                  <th>Sem</th>
                  <th>Section</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id}>
                    <td>{s.enrollment_no}</td>
                    <td>{s.name}</td>
                    <td>{s.department_code}</td>
                    <td>{s.batch}</td>
                    <td>{s.semester}</td>
                    <td>{s.section}</td>
                    <td>{s.phone}</td>
                    <td>{s.email}</td>
                    <td>
                      <button className="btn-secondary" onClick={() => handleDelete(s.id)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
                {students.length === 0 && (
                  <tr><td colSpan="9">No students found.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}
