import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const token = localStorage.getItem('token');

  if (!token) {
    // Nếu không có token, chuyển hướng về /login
    // 'replace' để không lưu trang /home vào lịch sử
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Nếu có token, hiển thị trang (TodoDashboard)
  return children;
}