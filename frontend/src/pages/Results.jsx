import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  fetchDepartments,
  fetchSubjects,
  createSubject,
  bulkImportResults,
  fetchMarksheet,
  fetchClassSummary,
} from "../api/client";

const emptySubjectForm = { code: "", name: "", department: "", semester: 1, credits: 4 };

export default function Results() {
  const { user, logout } = useAuth();
  const [departments, setDepartments] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [showSubjectForm, setShowSubjectForm] = useState(false);
  const [subjectForm, setSubjectForm] = useState(emptySubjectForm);
  const [subjectError, setSubjectError] = useState("");

  const [importSummary, setImportSummary] = useState(null);
  const [importBusy, setImportBusy] = useState(false);

  const [enrollmentNo, setEnrollmentNo] = useState("");
  const [academicYear, setAcademicYear] = useState("2025-26");
  const [marksheet, setMarksheet] = useState(null);
  const [marksheetError, setMarksheetError] = useState("");

  const [summaryDept, setSummaryDept] = useState("");
  const [summaryBatch, setSummaryBatch] = useState("");
  const [summaryYear, setSummaryYear] = useState("2025-26");
  const [summary, setSummary] = useState(null);
  const [summaryError, setSummaryError] = useState("");

  useEffect(() => {
    fetchDepartments().then(setDepartments);
    fetchSubjects().then(setSubjects);
  }, []);

  async function handleAddSubject(e) {
    e.preventDefault();
    setSubjectError("");
    try {
      await createSubject(subjectForm);
      setSubjectForm(emptySubjectForm);
      setShowSubjectForm(false);
      fetchSubjects().then(setSubjects);
    } catch (err) {
      setSubjectError(JSON.stringify(err?.response?.data || "Could not create subject"));
    }
  }

  async function handleImport(e) {
    const file = e.target.files[0];
    if (!file) return;
    setImportBusy(true);
    setImportSummary(null);
    try {
      const result = await bulkImportResults(file);
      setImportSummary(result.summary);
    } catch (err) {
      setImportSummary({ error: err?.response?.data?.detail || "Import failed" });
    } finally {
      setImportBusy(false);
      e.target.value = "";
    }
  }

  async function handleMarksheetLookup(e) {
    e.preventDefault();
    setMarksheetError("");
    setMarksheet(null);
    try {
      const data = await fetchMarksheet(enrollmentNo, academicYear);
      setMarksheet(data);
    } catch (err) {
      setMarksheetError(err?.response?.data?.detail || "Not found");
    }
  }

  async function handleSummaryLookup(e) {
    e.preventDefault();
    setSummaryError("");
    setSummary(null);
    try {
      const data = await fetchClassSummary({
        department: summaryDept || undefined,
        batch: summaryBatch || undefined,
        academic_year: summaryYear || undefined,
      });
      setSummary(data);
    } catch (err) {
      setSummaryError(err?.response?.data?.detail || "Not found");
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>BPIT ERP</h1>
          <span className="subtitle">Results / Exams</span>
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
          <h2>Subjects</h2>
          <div className="form-row">
            <button className="btn-primary" onClick={() => setShowSubjectForm((s) => !s)}>
              {showSubjectForm ? "Cancel" : "+ Add Subject"}
            </button>
          </div>
          {showSubjectForm && (
            <form onSubmit={handleAddSubject} style={{ marginBottom: "1rem" }}>
              {subjectError && <div className="error-banner">{subjectError}</div>}
              <div className="form-row">
                <label>
                  Code
                  <input required value={subjectForm.code}
                    onChange={(e) => setSubjectForm((f) => ({ ...f, code: e.target.value }))} />
                </label>
                <label>
                  Name
                  <input required value={subjectForm.name}
                    onChange={(e) => setSubjectForm((f) => ({ ...f, name: e.target.value }))} />
                </label>
                <label>
                  Department
                  <select required value={subjectForm.department}
                    onChange={(e) => setSubjectForm((f) => ({ ...f, department: e.target.value }))}>
                    <option value="">Select</option>
                    {departments.map((d) => <option key={d.id} value={d.id}>{d.code}</option>)}
                  </select>
                </label>
                <label>
                  Semester
                  <input type="number" min="1" max="8" value={subjectForm.semester}
                    onChange={(e) => setSubjectForm((f) => ({ ...f, semester: e.target.value }))} />
                </label>
                <label>
                  Credits
                  <input type="number" min="1" max="10" value={subjectForm.credits}
                    onChange={(e) => setSubjectForm((f) => ({ ...f, credits: e.target.value }))} />
                </label>
              </div>
              <button className="btn-primary" type="submit">Save Subject</button>
            </form>
          )}
          <table>
            <thead>
              <tr><th>Code</th><th>Name</th><th>Dept</th><th>Sem</th><th>Credits</th></tr>
            </thead>
            <tbody>
              {subjects.map((s) => (
                <tr key={s.id}>
                  <td>{s.code}</td><td>{s.name}</td><td>{s.department_code}</td>
                  <td>{s.semester}</td><td>{s.credits}</td>
                </tr>
              ))}
              {subjects.length === 0 && <tr><td colSpan="5">No subjects yet.</td></tr>}
            </tbody>
          </table>
        </section>

        <section className="card">
          <h2>Bulk Import Results</h2>
          <p className="subtitle" style={{ marginBottom: "0.75rem" }}>
            CSV/Excel columns: enrollment_no, subject_code, academic_year, exam_type, marks_obtained, max_marks
          </p>
          <label className="btn-secondary" style={{ cursor: "pointer", display: "inline-block" }}>
            {importBusy ? "Importing..." : "Upload Results File"}
            <input type="file" accept=".csv,.xlsx,.xls" style={{ display: "none" }}
              onChange={handleImport} disabled={importBusy} />
          </label>
          {importSummary && (
            <div className="import-summary">
              {importSummary.error
                ? `Error: ${importSummary.error}`
                : `Imported: ${importSummary.created} created, ${importSummary.updated} updated, ${importSummary.failed} failed (of ${importSummary.total_rows} rows)`}
            </div>
          )}
        </section>

        <section className="card">
          <h2>Student Marksheet</h2>
          <form onSubmit={handleMarksheetLookup} className="filters">
            <input placeholder="Enrollment No" value={enrollmentNo}
              onChange={(e) => setEnrollmentNo(e.target.value)} required />
            <input placeholder="Academic Year (e.g. 2025-26)" value={academicYear}
              onChange={(e) => setAcademicYear(e.target.value)} />
            <button className="btn-primary" type="submit">Lookup</button>
          </form>
          {marksheetError && <div className="error-banner">{marksheetError}</div>}
          {marksheet && (
            <div>
              <p><strong>{marksheet.student_name}</strong> ({marksheet.student_enrollment_no}) — {marksheet.department_code}, Batch {marksheet.batch}</p>
              <table>
                <thead>
                  <tr><th>Subject</th><th>Type</th><th>Marks</th><th>Grade</th></tr>
                </thead>
                <tbody>
                  {marksheet.subjects.map((s, i) => (
                    <tr key={i}>
                      <td>{s.subject_code} - {s.subject_name}</td>
                      <td>{s.exam_type}</td>
                      <td>{s.marks_obtained} / {s.max_marks}</td>
                      <td>{s.grade}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p style={{ marginTop: "0.75rem" }}>
                Total: <strong>{marksheet.total_obtained} / {marksheet.total_max}</strong> ({marksheet.percentage}%) — Overall Grade: <strong>{marksheet.overall_grade}</strong>
              </p>
            </div>
          )}
        </section>

        <section className="card">
          <h2>Class-wise Summary</h2>
          <form onSubmit={handleSummaryLookup} className="filters">
            <select value={summaryDept} onChange={(e) => setSummaryDept(e.target.value)}>
              <option value="">All Departments</option>
              {departments.map((d) => <option key={d.id} value={d.code}>{d.code}</option>)}
            </select>
            <input placeholder="Batch (e.g. 2024-28)" value={summaryBatch}
              onChange={(e) => setSummaryBatch(e.target.value)} />
            <input placeholder="Academic Year" value={summaryYear}
              onChange={(e) => setSummaryYear(e.target.value)} />
            <button className="btn-primary" type="submit">Get Summary</button>
          </form>
          {summaryError && <div className="error-banner">{summaryError}</div>}
          {summary && (
            <div className="import-summary">
              Total entries: {summary.total_entries} | Pass: {summary.pass_count} | Fail: {summary.fail_count} |
              Pass %: {summary.pass_percentage}% | Avg %: {summary.average_percentage}%
              <br />
              Grade distribution: {Object.entries(summary.grade_distribution).map(([g, c]) => `${g}:${c}`).join(", ")}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
