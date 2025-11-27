// src/api/share.js
import client from "./client";

// Chia sẻ task cho 1 username (backend nhận shared_to_username)
export async function shareTask(todoId, email, permission = "view") {
  const res = await client.post("/todos/share/", {
    todo_id: todoId,
    shared_to_email: email,
    permission,
  });
  return res.data;
}

export async function listSharedWithMe() {
  const res = await client.get("/todos/shared-with-me/");
  return res.data;
}

export async function listSharedByMe() {
  const res = await client.get("/todos/shared-by-me/");
  return res.data;
}

// Lấy thông tin task qua share link public
export async function getTaskByShareLink(shareLink) {
  const res = await client.get(`/todos/share-link/${shareLink}/`);
  return res.data;
}
