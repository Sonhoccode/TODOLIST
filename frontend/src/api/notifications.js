// src/api/notifications.js
import client from "./client";

// Lấy notification của 1 task
export async function getNotificationByTodo(todoId) {
  const res = await client.get("/notifications/", {
    params: { todo: todoId },
  });

  if (Array.isArray(res.data) && res.data.length > 0) {
    return res.data[0];
  }
  return null;
}

// Lưu cấu hình nhắc email cho 1 task
export async function saveNotificationForTodo(todoId, enabled, minutes) {
  const current = await getNotificationByTodo(todoId);

  if (!enabled) {
    if (current) {
      const res = await client.patch(`/notifications/${current.id}/`, {
        enabled: false,
      });
      return res.data;
    }
    return null;
  }

  const payload = {
    todo: todoId,
    reminder_minutes: Number(minutes) || 0,
    channels: "email",
    enabled: true,
  };

  if (!current) {
    const res = await client.post("/notifications/", payload);
    return res.data;
  } else {
    const res = await client.patch(`/notifications/${current.id}/`, payload);
    return res.data;
  }
}
