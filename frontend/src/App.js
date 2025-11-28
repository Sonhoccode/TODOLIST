import "./index.css";
import "./styles/globals.css";
import { Routes, Route } from "react-router-dom";

import LandingPage from "./page/landing_page"; 
import TodoDashboard from "./page/TodoDashboard"; 
import Login from "./page/login";
import Register from "./page/register";
import ProtectedRoute from "./components/ProtectedRoute";
import ShareTodoPage from "./page/ShareTodoPage";

export default function App() {
  return (
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
  );
}
