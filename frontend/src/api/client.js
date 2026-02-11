import axios from "axios";


const API_ROOT =
  process.env.REACT_APP_API_BASE_URL;

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
      // console.log(`[API Request] ${cfg.method.toUpperCase()} ${cfg.url} - Đã đính kèm token`);
    } else {
      console.warn(`[API Request] ${cfg.method.toUpperCase()} ${cfg.url} - Không tìm thấy token trong localStorage`);
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
      console.error("[Lỗi API] 401 Unauthorized từ:", error.config?.url);
      console.log("Đang xóa token và chuyển hướng về trang đăng nhập...");
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    
    // Log errors cho debugging
    if (process.env.NODE_ENV === "development") {
      console.error("Lỗi API:", {
        url: error.config?.url,
        method: error.config?.method,
        status: error.response?.status,
        data: error.response?.data,
      });
      console.log("Chi tiết lỗi:", error);
    }
    
    return Promise.reject(error);
  }
);

export default client;
