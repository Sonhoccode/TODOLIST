import axios from "axios";

const baseURL = "http://127.0.0.1:8000/api"; 
const client = axios.create({ baseURL });

// --- BỎ COMMENT KHỐI NÀY VÀ SỬA LẠI ---
client.interceptors.request.use((cfg) => {
  // Lấy "token" từ localStorage (vì auth.js lưu là 'token')
  const t = localStorage.getItem("token"); 
  if (t) {
    // API dj-rest-auth (backend) dùng "Token", không phải "Bearer"
    cfg.headers.Authorization = `Token ${t}`; 
  }
  return cfg;
});
// --- KẾT THÚC SỬA ---

export default client;