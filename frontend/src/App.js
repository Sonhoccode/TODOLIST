import React, { lazy, Suspense } from "react";
import "./index.css";
import "./styles/globals.css";
import { Routes, Route } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";

// Lazy load các pages để tối ưu performance
const LandingPage = lazy(() => import("./page/landing_page"));
const TodoDashboard = lazy(() => import("./page/TodoDashboard"));
const Login = lazy(() => import("./page/login"));
const Register = lazy(() => import("./page/register"));
const ShareTodoPage = lazy(() => import("./page/ShareTodoPage"));

// Loading component
const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
      <p className="text-gray-600">Đang tải...</p>
    </div>
  </div>
);

export default function App() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/share/:shareLink" element={<ShareTodoPage />} />

        <Route 
          path="/home" 
          element={
            <ProtectedRoute>
              <TodoDashboard />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Suspense>
  );
}
