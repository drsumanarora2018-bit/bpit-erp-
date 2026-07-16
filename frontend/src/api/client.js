import axios from "axios";

const API_BASE = "http://localhost:8000/api";

const client = axios.create({ baseURL: API_BASE });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function loginRequest(username, password) {
  const res = await axios.post(`${API_BASE}/auth/login/`, { username, password });
  return res.data;
}

export async function fetchMe() {
  const res = await client.get("/auth/me/");
  return res.data;
}

export async function fetchDepartments() {
  const res = await client.get("/departments/");
  return res.data;
}

export async function fetchUsers() {
  const res = await client.get("/users/");
  return res.data;
}

export default client;

export async function fetchStudents(params = {}) {
  const res = await client.get("/students/", { params });
  return res.data;
}

export async function createStudent(payload) {
  const res = await client.post("/students/", payload);
  return res.data;
}

export async function updateStudent(id, payload) {
  const res = await client.patch(`/students/${id}/`, payload);
  return res.data;
}

export async function deleteStudent(id) {
  await client.delete(`/students/${id}/`);
}

export async function bulkImportStudents(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await client.post("/students/bulk-import/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
