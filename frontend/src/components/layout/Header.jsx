import React from "react";

export default function Header({ onCreate }) {
  return (
    <header className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="inline-block px-3 py-1 rounded-full bg-gray-900 text-white text-sm font-bold">
            TODO
          </span>
        </div>

        <div className="flex items-center gap-3">
          <input
            className="w-[340px] rounded-full border px-4 py-2 text-sm"
            placeholder="Tìm theo tiêu đề/mô tả..."
            onChange={(e) => {
              const ev = new CustomEvent("global-search", { detail: e.target.value });
              window.dispatchEvent(ev);
            }}
          />
          <button
            onClick={onCreate}
            className="px-4 py-2 rounded-full bg-gray-900 text-white text-sm"
          >
            + Tạo công việc
          </button>
        </div>
      </div>
    </header>
  );
}
