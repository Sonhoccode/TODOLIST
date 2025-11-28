import React from "react";

function Pill({ children, tone = "gray" }) {
  const toneMap = {
    gray: "bg-gray-100 text-gray-700 border",
    red: "bg-red-100 text-red-700 border border-red-300",
    blue: "bg-blue-100 text-blue-700 border border-blue-300",
    amber: "bg-amber-100 text-amber-700 border border-amber-300",
    green: "bg-green-100 text-green-700 border border-green-300",
  };
  return (
    <span
      className={`text-xs px-2 py-0.5 rounded-full ${
        toneMap[tone] || toneMap.gray
      }`}
    >
      {children}
    </span>
  );
}

function fmt(dt) {
  if (!dt) return "";
  const d = new Date(dt);
  return `${d.toLocaleTimeString([], { hour12: false })} ${d.toLocaleDateString()}`;
}

function TaskList({ items, onToggle, onEdit, onDelete, onShare }) {
  return (
    <div className="bg-white border rounded-2xl overflow-x-auto">
      {/* grid theo tỉ lệ, không fix px nữa */}
      <div className="px-5 py-3 grid grid-cols-[28px_minmax(0,2fr)_minmax(0,1.4fr)_minmax(0,1fr)_minmax(0,0.9fr)_minmax(0,1.3fr)] text-xs text-gray-500">
        <div></div>
        <div>CÔNG VIỆC</div>
        <div className="text-center">THỜI HẠN</div>
        <div className="text-center">MỨC ƯU TIÊN</div>
        <div>NHÃN</div>
        <div className="text-center">THAO TÁC</div>
      </div>

      <ul className="divide-y">
        {items.map((t) => {
          const overdue =
            !t.completed && t.due_at && new Date(t.due_at).getTime() < Date.now();
          const tone =
            t.priority === "Urgent"
              ? "red"
              : t.priority === "High"
              ? "amber"
              : t.priority === "Medium"
              ? "blue"
              : "gray";

          return (
            <li
              key={t.id}
              className="px-5 py-3 grid grid-cols-[28px_minmax(0,2fr)_minmax(0,1.4fr)_minmax(0,1fr)_minmax(0,0.9fr)_minmax(0,1.3fr)] items-start"
            >
              {/* Checkbox */}
              <div className="pt-1">
                <input
                  type="checkbox"
                  className="h-4 w-4"
                  checked={!!t.completed}
                  onChange={() => onToggle(t)}
                />
              </div>

              {/* Công việc */}
              <div>
                <div
                  className={`font-medium ${
                    t.completed ? "line-through text-gray-400" : ""
                  }`}
                >
                  <span className={overdue ? "text-red-600" : ""}>{t.title}</span>
                </div>
                {t.description && (
                  <div className="text-sm text-gray-600">{t.description}</div>
                )}
              </div>

              {/* Thời hạn */}
              <div className="text-sm mx-2">
                {t.due_at ? (
                  <div className="flex items-center justify-center">
                    <span className={overdue ? "text-red-600" : ""}>
                      {fmt(t.due_at)}
                    </span>
                  </div>
                ) : (
                  <span className="text-gray-400">—</span>
                )}
              </div>

              {/* Priority */}
              <div className="flex items-center justify-center">
                <Pill tone={tone}>{t.priority || "—"}</Pill>
              </div>

              {/* Tags – cột hẹp, text gọn */}
              <div className="flex flex-wrap gap-1 max-w-[120px]">
                {(t.tags || []).length ? (
                  t.tags.map((x) => <Pill key={x}>{x}</Pill>)
                ) : (
                  <span className="text-gray-400 text-sm">—</span>
                )}
              </div>

              {/* Thao tác – 3 nút ngang, không wrap */}
              <div className="text-right">
                <div className="inline-flex gap-2">
                  <button
                    onClick={() => onEdit(t)}
                    className="px-2.5 py-1 rounded-full border hover:bg-gray-50 text-xs"
                  >
                    Sửa
                  </button>
                  <button
                    onClick={() => onDelete(t)}
                    className="px-2.5 py-1 rounded-full border hover:bg-gray-50 text-xs"
                  >
                    Xoá
                  </button>
                  {onShare && (
                    <button
                      onClick={() => onShare(t)}
                      className="px-2.5 py-1 rounded-full border hover:bg-gray-50 text-xs"
                    >
                      Chia sẻ
                    </button>
                  )}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default React.memo(TaskList);
