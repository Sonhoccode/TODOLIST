import { Navigate, useLocation } from "react-router-dom";

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const tokenFromUrl = params.get("token");

  let token = localStorage.getItem("token");
  console.log("ProtectedRoute kiểm tra token:", token ? "Có" : "Không có");

  if (tokenFromUrl) {
    console.log("Tìm thấy token trong URL, đang lưu vào localStorage:", tokenFromUrl);
    localStorage.setItem("token", tokenFromUrl);
    token = tokenFromUrl;

    // Xóa token khỏi URL để nhìn cho đẹp
    const url = new URL(window.location.href);
    url.searchParams.delete("token");
    window.history.replaceState({}, "", url.toString());
  }

  if (!token) {
    console.warn("Không có token trong ProtectedRoute, chuyển hướng về đăng nhập");
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return children;
}
