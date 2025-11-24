// src/api/notifications.js
import client from "./client";

const endpoint = "/notifications/";

// CRUD notification settings
export const listNotifications = (params) =>
  client.get(endpoint, { params }).then((r) => r.data);

export const createNotification = (data) =>
  client.post(endpoint, data).then((r) => r.data);

export const updateNotification = (id, data) =>
  client.put(`${endpoint}${id}/`, data).then((r) => r.data);

export const deleteNotification = (id) =>
  client.delete(`${endpoint}${id}/`).then((r) => r.data);

// Lấy notification theo 1 todo cụ thể
export const getNotificationsByTodo = (todoId) =>
  client
    .get(`${endpoint}by-todo/`, { params: { todo_id: todoId } })
    .then((r) => r.data);
