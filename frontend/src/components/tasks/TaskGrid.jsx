import React from "react";

// (Pill và fmt giữ nguyên)
function Pill({ children, tone="gray" }) {
  const toneMap = {
    gray: "bg-gray-100 text-gray-700 border",
    red: "bg-red-100 text-red-700 border border-red-300",
    blue: "bg-blue-100 text-blue-700 border border-blue-300",
    amber: "bg-amber-100 text-amber-700 border border-amber-300",
    green: "bg-green-100 text-green-700 border border-green-300",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full ${toneMap[tone] || toneMap.gray}`}>
      {children}
    </span>
  );
}
function fmt(dt) {
  if (!dt) return "";
  const d = new Date(dt);
  return `${d.toLocaleTimeString([], {hour12:false})} ${d.toLocaleDateString()}`;
}

// Component Card riêng lẻ cho Grid
function TaskCard({ task, onToggle, onEdit, onDelete }) {
  const t = task; 
  const overdue = !t.completed && t.due_at && new Date(t.due_at).getTime() < Date.now();
  const tone =
    t.priority==="Urgent" ? "red" :
    t.priority==="High" ? "amber" :
    t.priority==="Medium" ? "blue" : "gray";

  return (
    <div className="bg-white border rounded-lg shadow-sm p-4 flex flex-col">
      {/* (Checkbox và Tiêu đề giữ nguyên) */}
      <div className="flex items-start gap-3 mb-2">
        <input
          type="checkbox"
          className="h-4 w-4 mt-1 shrink-0"
          checked={!!t.completed}
          onChange={()=>onToggle(t)}
        />
        <div className={`font-medium ${t.completed?"line-through text-gray-400":""}`}>
          {t.title}
        </div>
      </div>
      
      {/* (Mô tả giữ nguyên) */}
      {t.description && (
        <div className="text-sm text-gray-600 mb-3 ml-7">
          {t.description}
        </div>
      )}

      <div className="text-sm mb-3">
        <span className="font-medium text-gray-500">Thời hạn: </span> 
        {t.due_at ? (
          <span className={overdue ? "text-red-600 font-medium" : ""}>
            {fmt(t.due_at)}
          </span>
        ) : <span className="text-gray-400">—</span>}
      </div>

      {/* (Ưu tiên giữ nguyên) */}
      <div className="text-sm mb-3">
        <span className="font-medium text-gray-500">Ưu tiên: </span>
        <Pill tone={tone}>{t.priority || "—"}</Pill>
      </div>

      {/* (Nhãn (Tags) giữ nguyên) */}
      <div className="mb-4">
        <span className="font-medium text-gray-500 text-sm">Nhãn: </span>
        <div className="flex flex-wrap gap-1.5 mt-1.5">
          {(t.tags||[]).length ? (
            t.tags.map((x)=> <Pill key={x}>{x}</Pill>)
          ) : <span className="text-gray-400 text-sm">—</span>}
        </div>
      </div>
      
      {/* (Nút bấm (đẩy xuống dưới cùng) giữ nguyên) */}
      <div className="mt-auto flex justify-end gap-2">
        <button onClick={()=>onEdit(t)} className="px-3 py-1 rounded-full border hover:bg-gray-50 text-sm">Sửa</button>
        <button onClick={()=>onDelete(t)} className="px-3 py-1 rounded-full border hover:bg-gray-50 text-sm">Xoá</button>
      </div>
    </div>
  );
}


// Component Grid chính
function TaskGrid({
  items,
  onToggle,
  onEdit,
  onDelete,
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((t)=> (
        <TaskCard 
          key={t.id}
          task={t}
          onToggle={onToggle}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

export default React.memo(TaskGrid);