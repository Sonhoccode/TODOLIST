import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api/auth";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await login(username, password);
      navigate("/home");
    } catch (err) {
      setError("Tên đăng nhập hoặc mật khẩu sai.");
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
            Welcome back. Let’s get things done.
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

          <h2 className="text-3xl font-bold mb-2 text-center text-gray-900">Sign In</h2>
          <p className="text-center text-gray-500 mb-8">
            Log in to your TODO workspace
          </p>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Tên đăng nhập (Username)"
              autoComplete="username"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-black focus:border-black"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              type="password"
              placeholder="Password"
              autoComplete="current-password"
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-black focus:border-black"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            {error && (
              <p className="text-sm text-red-600 text-center">{error}</p>
            )}

            <button
              type="submit"
              className="w-full mt-2 py-3 rounded-lg bg-gray-900 text-white font-medium hover:bg-black active:scale-[.99] transition border border-transparent hover:border-gray-900"
            >
              Login
            </button>
          </form>

          {/* Social login */}
          <div className="mt-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="h-px flex-1 bg-gray-200" />
              <span className="text-xs text-gray-400 uppercase tracking-wide">
                Or continue with
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

          <p className="text-sm text-center mt-6 text-gray-600">
            Don’t have an account?{" "}
            <Link
              to="/register"
              className="font-semibold text-gray-900 hover:underline underline-offset-4"
            >
              Sign Up
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
