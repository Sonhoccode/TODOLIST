import axios from "axios";


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
