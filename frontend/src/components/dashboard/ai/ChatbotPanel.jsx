import React, { useState } from "react";

/**
 * AI Chatbot Panel - Tạo task bằng natural language
 */
export default function ChatbotPanel({ onTaskCreated }) {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const { sendChatMessage } = await import("../../../api/chatbot");
      const res = await sendChatMessage(message.trim());
      setResult(res);
      
      if (res.task && onTaskCreated) {
        onTaskCreated();
      }
    } catch (err) {
      console.error("Lỗi chatbot:", err);
      alert("Chatbot tạo task thất bại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border rounded-2xl p-4 space-y-3">
      {/* Header */}
      <div>
        <h2 className="text-base font-semibold text-gray-900">
          Trợ lý AI tạo công việc
        </h2>
        <p className="text-xs text-gray-600 mt-1">
          Ví dụ: "Nhắc học Python 2 tiếng tối mai", AI sẽ tự phân tích và tạo task.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-2">
        <textarea
          rows={6}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Nhập yêu cầu của bạn..."
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm outline-none focus:border-gray-500 focus:ring-2 focus:ring-gray-200 resize-none"
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-black text-white text-sm font-medium hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "AI đang xử lý..." : "Gửi cho AI"}
          </button>
        </div>
      </form>

      {/* Result */}
      {result && (
        <div className="mt-2 rounded-lg border border-gray-200 bg-gray-50 px-3 py-3 text-xs space-y-2">
          {result.response && (
            <p className="text-gray-700">{result.response}</p>
          )}

          {result.task && (
            <div className="space-y-1 pt-2 border-t">
              <div className="font-medium text-gray-900">Task vừa tạo:</div>
              <div className="text-gray-700">
                <span className="font-medium">Tiêu đề:</span> {result.task.title}
              </div>
              {result.task.description && (
                <div className="text-gray-700">
                  <span className="font-medium">Mô tả:</span> {result.task.description}
                </div>
              )}
              <div className="text-gray-700">
                <span className="font-medium">Ưu tiên:</span> {result.task.priority}
              </div>
              {result.task.due_at && (
                <div className="text-gray-700">
                  <span className="font-medium">Đến hạn:</span>{" "}
                  {new Date(result.task.due_at).toLocaleString("vi-VN")}
                </div>
              )}
            </div>
          )}

          {result.prediction && (
            <div className="mt-2 rounded-md border border-emerald-200 bg-emerald-50 px-2 py-1.5 text-[11px] text-emerald-900">
              <span className="font-medium">AI Dự đoán:</span> Xác suất hoàn thành đúng hạn{" "}
              {(result.prediction.on_time_prediction * 100).toFixed(1)}%
              {result.prediction.confidence && (
                <span className="opacity-75">
                  {" "}(độ tin cậy {(result.prediction.confidence * 100).toFixed(1)}%)
                </span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
