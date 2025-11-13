import client from "./client";

/**
 * Đăng nhập
 * API (dj-rest-auth) yêu cầu: username, password
 * Trả về: { "key": "..." } (đây là Token)
 */
export const login = (username, password) => {
  return client.post("/auth/login/", { username, password }).then((res) => {
    if (res.data.key) {
      // Lưu token vào localStorage để dùng cho các request sau
      localStorage.setItem("token", res.data.key);
      return res.data;
    }
    throw new Error("Login response did not contain a token key.");
  });
};

/**
 * Đăng ký
 * API (dj-rest-auth) yêu cầu: username, email, password, password2
 */
export const register = ({ username, email, password1, password2 }) => {
  return client.post("/auth/registration/", {
    username,
    email,
    password1,
    password2,
  });
};

/**
 * Đăng xuất
 * API yêu cầu gửi POST rỗng (client.js sẽ tự đính kèm Token)
 */
export const logout = () => {
  return client.post("/auth/logout/").finally(() => {
    // Dù thành công hay thất bại, luôn xoá token ở frontend
    localStorage.removeItem("token");
  });
};