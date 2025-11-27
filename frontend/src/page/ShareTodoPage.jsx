// frontend/src/page/ShareTodoPage.jsx
import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import Header from "../components/layout/Header";
import { getTaskByShareLink } from "../api/share";

export default function ShareTodoPage() {
  const { shareLink } = useParams();
  const navigate = useNavigate();

  const [state, setState] = useState({
    loading: true,
    error: null,
    data: null,
  });

  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const res = await getTaskByShareLink(shareLink);
        if (!cancelled) {
          setState({
            loading: false,
            error: null,
            data: res,
          });
        }
      } catch (err) {
        console.error("Error load share link:", err);
        const msg =
          err?.response?.data?.error ||
          "Link chia sẻ không hợp lệ hoặc đã hết hạn.";
        if (!cancelled) {
          setState({
            loading: false,
            error: msg,
            data: null,
          });
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [shareLink]);

  const { loading, error, data } = state;

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-3xl mx-auto px-6 py-10">
        {loading && (
          <p className="text-gray-600 text-sm">Đang tải thông tin chia sẻ...</p>
        )}

        {!loading && error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-4 text-sm">
            {error}
          </div>
        )}

        {!loading && !error && data && (
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
            <h1 className="text-2xl font-semibold mb-4">
              Task được chia sẻ cho bạn
            </h1>

            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-1">
                Người chia sẻ: <span className="font-semibold">{data.shared_by}</span>
              </p>
              <p className="text-xs text-gray-500">
                Quyền: <span className="font-semibold uppercase">{data.permission}</span>
              </p>
            </div>

            <div className="border rounded-lg px-4 py-3 bg-gray-50 mb-4">
              <h2 className="text-lg font-bold mb-2">{data.task_title}</h2>
              <p className="text-sm text-gray-700 whitespace-pre-line">
                {data.task_description || "Không có mô tả."}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                className="px-4 py-2 text-sm rounded-lg border border-gray-300"
                onClick={() => navigate("/login")}
              >
                Đăng nhập để vào app
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
