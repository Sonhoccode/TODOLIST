import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../api/auth";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    password2: "",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (form.password !== form.password2) {
      setError("Mật khẩu không khớp.");
      return;
    }
    setError("");
    try {
      await register({
        username: form.username,
        email: form.email,
        password1: form.password,
        password2: form.password2,
      });
      navigate("/login");
    } catch (err) {
      if (err.response && err.response.data) {
        const apiErrors = err.response.data;
        if (apiErrors.username) setError(apiErrors.username[0]);
        else if (apiErrors.email) setError(apiErrors.email[0]);
        else if (apiErrors.password1) setError(apiErrors.password1[0]);
        else setError("Đã xảy ra lỗi, vui lòng thử lại.");
      } else {
        setError("Lỗi kết nối máy chủ.");
      }
      console.error(err);
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/accounts/google/login/`;
  };

  const handleGithubLogin = () => {
    window.location.href = `${API_BASE_URL}/accounts/github/login/`;
  };
  
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="bg-white/80 backdrop-blur border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-5xl mx-auto h-[72px] px-6 flex items-center justify-between">
          <Link
            to="/"
            className="px-4 py-2 rounded-full bg-gray-900 text-white text-xl font-bold tracking-tight shadow-sm"
          >
            TODO
          </Link>
          <p className="text-sm md:text-base text-gray-700 font-medium">
            Join us and start achieving more today.
          </p>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center px-4">
        <div className="relative w-full max-w-md bg-white rounded-2xl shadow-xl ring-1 ring-black/10 p-8 md:p-10">
          <button
            onClick={() => navigate(-1)}
            className="absolute top-4 left-4 p-2 rounded-full border border-gray-200 text-gray-600 hover:text-black hover:border-gray-400 transition"
            aria-label="Go back"
          >
            <svg
              xmlns="https://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              className="w-5 h-5"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 18l-6-6 6-6" />
            </svg>
          </button>

          <h2 className="text-3xl font-bold mb-2 text-center text-gray-900">
            Create Account
          </h2>
          <p className="text-center text-gray-500 mb-4">
            Let’s get you started with your personal TODO app
          </p>

          {/* Social register/login */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-gray-200" />
              <span className="text-xs text-gray-400 uppercase tracking-wide">
                Continue with
              </span>
              <div className="h-px flex-1 bg-gray-200" />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleGoogleLogin}
                className="w-full py-2.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-800 hover:bg-gray-50 transition"
              >
                Google
              </button>
              <button
                type="button"
                onClick={handleGithubLogin}
                className="w-full py-2.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-800 hover:bg-gray-50 transition"
              >
                GitHub
              </button>
            </div>
          </div>

          {/* Form register chuẩn */}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <input
              name="username"
              type="text"
              placeholder="Tên đăng nhập (Username)"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-black focus:border-black outline-none"
              value={form.username}
              onChange={handleChange}
            />
            <input
              name="email"
              type="email"
              placeholder="Email"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-black focus:border-black outline-none"
              value={form.email}
              onChange={handleChange}
            />
            <input
              name="password"
              type="password"
              placeholder="Mật khẩu"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-black focus:border-black outline-none"
              value={form.password}
              onChange={handleChange}
            />
            <input
              name="password2"
              type="password"
              placeholder="Xác nhận mật khẩu"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-black focus:border-black outline-none"
              value={form.password2}
              onChange={handleChange}
            />
            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            <button
              type="submit"
              className="w-full mt-2 py-3 rounded-lg bg-gray-900 text-white font-medium hover:bg-black active:scale-[.99] transition"
            >
              Register
            </button>
          </form>

          <p className="text-sm text-center mt-6 text-gray-600">
            Already have an account?{" "}
            <Link
              to="/login"
              className="font-semibold text-gray-900 hover:underline underline-offset-4"
            >
              Sign In
            </Link>
          </p>
        </div>
      </main>

      <footer className="text-center text-gray-400 text-sm py-4">
        © 2025 Group 10 - Python Programming Course
      </footer>
    </div>
  );
}
