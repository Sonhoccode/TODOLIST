import axios from "axios";

// REACT_APP_API_BASE_URL: root của backend, KHÔNG có /api ở cuối
// vd local:  http://127.0.0.1:8000
// vd prod:   https://<railway>.up.railway.app  hoặc https://api.hsonspace.id.vn
const API_ROOT =
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

// /api là prefix trong Django urls
const baseURL = `${API_ROOT}/api`;

const client = axios.create({ 
  baseURL,
  timeout: 10000, // 10s timeout
});

// Request interceptor - thêm token
client.interceptors.request.use(
  (cfg) => {
    const t = localStorage.getItem("token");
    if (t) {
      cfg.headers.Authorization = `Token ${t}`;
    }
    return cfg;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - xử lý errors
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Auto logout nếu 401
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    
    // Log errors cho debugging
    if (process.env.NODE_ENV === "development") {
      console.error("API Error:", {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
      });
    }
    
    return Promise.reject(error);
  }
);

export default client;
