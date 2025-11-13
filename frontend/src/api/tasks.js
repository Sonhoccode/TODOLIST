import client from "./client";

const endpoint = "/todos/";

export const listTasks = (params) =>
  client.get(endpoint, { params }).then((r) => r.data);

export const createTask = (data) =>
  client.post(endpoint, data).then((r) => r.data);

export const updateTask = (id, data) =>
  client.put(`${endpoint}${id}/`, data).then((r) => r.data);

export const deleteTask = (id) =>
  client.delete(`${endpoint}${id}/`).then((r) => r.data);

export const toggleTaskStatus = (id) =>
  client.patch(`${endpoint}${id}/toggle-status/`);

export const listCategories = () =>
  client.get("/categories/").then((r) => r.data);

export const createCategory = (data) =>
  client.post("/categories/", data).then((r) => r.data);

export const deleteCategory = (id) =>
  client.delete(`/categories/${id}/`);