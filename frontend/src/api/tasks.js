// src/api/tasks.js
import client from "./client";

const endpoint = "/todos/";

// ==== CORE CRUD ====
export const listTasks = (params) =>
  client.get(endpoint, { params }).then((r) => {
    // Handle pagination response
    if (r.data.results) {
      return r.data.results; // DRF pagination format
    }
    return r.data; // Non-paginated format
  });

export const createTask = (data) =>
  client.post(endpoint, data).then((r) => r.data);

export const updateTask = (id, data) =>
  client.put(`${endpoint}${id}/`, data).then((r) => r.data);

export const deleteTask = (id) =>
  client.delete(`${endpoint}${id}/`).then((r) => r.data);

export const toggleTaskStatus = (id) =>
  client.patch(`${endpoint}${id}/toggle-status/`).then((r) => r.data);

// ==== CATEGORY ====
export const listCategories = () =>
  client.get("/categories/").then((r) => r.data);

export const createCategory = (data) =>
  client.post("/categories/", data).then((r) => r.data);

export const deleteCategory = (id) =>
  client.delete(`/categories/${id}/`).then((r) => r.data);

// ==== SHARE TASK ====
export const shareTask = (payload) =>
  // payload: { todo_id, shared_to_username, permission }
  client.post(`${endpoint}share/`, payload).then((r) => r.data);

export const listSharedWithMe = () =>
  client.get(`${endpoint}shared-with-me/`).then((r) => r.data);

export const listSharedByMe = () =>
  client.get(`${endpoint}shared-by-me/`).then((r) => r.data);

// Public share link
export const getTaskByShareLink = (shareLink) =>
  client.get(`/todos/share-link/${shareLink}/`).then((r) => r.data);

// ==== CSV IMPORT / EXPORT ====

// Export CSV: trả về blob để tải file
export const exportTasksCsv = (params) =>
  client
    .get(`${endpoint}export-csv/`, {
      params,
      responseType: "blob",
    })
    .then((r) => r.data);

// Import CSV: gửi file multipart/form-data
export const importTasksCsv = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return client
    .post(`${endpoint}import-csv/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((r) => r.data);
};

// ==== CALENDAR ====

export const fetchCalendar = (params) =>
  // params: { start_date, end_date } tùy theo backend bạn đang dùng
  client.get(`${endpoint}calendar/`, { params }).then((r) => r.data);

export const fetchTasksByDate = (date) =>
  client
    .get(`${endpoint}tasks-by-date/`, { params: { date } })
    .then((r) => r.data);
