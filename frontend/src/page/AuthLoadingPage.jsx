import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function AuthLoadingPage() {
  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication immediately without delay
    const token = localStorage.getItem("token");
    
    if (token) {
      // User is logged in, redirect to dashboard
      navigate("/home", { replace: true });
    } else {
      // User not logged in, redirect to login
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  // Simple loading fallback (will be very brief)
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
        <p className="text-gray-600">Đang tải...</p>
      </div>
    </div>
  );
}
