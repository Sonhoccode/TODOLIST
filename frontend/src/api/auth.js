import client from "./client";

/**
 * Đăng nhập thường (username/password)
 * Backend: POST /api/auth/login/
 * Trả về: { key: "..." }
 */
export const login = async (username, password) => {
  const res = await client.post("/auth/login/", { username, password });

  if (!res.data || !res.data.key) {
    throw new Error("Login response did not contain a token key.");
  }

  // Lưu token dùng chung cho:
  // - login thường
  // - login Google
  // - login GitHub
  console.log("Đăng nhập thành công, đang lưu token:", res.data.key);
  localStorage.setItem("token", res.data.key);
  return res.data;
};

/**
 * Đăng ký tài khoản
 * Backend: POST /api/auth/registration/
 * Body: { username, email, password1, password2 }
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
 * Dùng chung cho:
 * - user đăng nhập thường
 * - user đăng nhập Google
 * - user đăng nhập GitHub
 *
 * Backend: POST /api/auth/logout/
 * (dj-rest-auth lo phần xoá token server,
 *  frontend chỉ cần clear localStorage)
 */
export const logout = async () => {
  try {
    await client.post("/auth/logout/");
  } catch (err) {
    // Nếu request fail (mất mạng, token hết hạn, v.v.) thì vẫn cứ xoá token local
    console.error("Logout error (ignored):", err);
  } finally {
    // Dù login kiểu gì cũng xài chung 1 token
    localStorage.removeItem("token");
    localStorage.removeItem("user");      // nếu sau này m có lưu
    localStorage.removeItem("provider");  // nếu m có lưu 'google' | 'github'
  }
};
