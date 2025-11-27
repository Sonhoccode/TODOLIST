import axios from "axios";

// REACT_APP_API_BASE_URL: root của backend, KHÔNG có /api ở cuối
// vd local:  http://127.0.0.1:8000
// vd prod:   https://<railway>.up.railway.app  hoặc https://api.hsonspace.id.vn
const API_ROOT =
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

// /api là prefix trong Django urls
const baseURL = `${API_ROOT}/api`;

const client = axios.create({ baseURL });

client.interceptors.request.use((cfg) => {
  const t = localStorage.getItem("token");
  if (t) {
    cfg.headers.Authorization = `Token ${t}`;
  }
  return cfg;
});

export default client;
