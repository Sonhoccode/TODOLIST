import React from "react";

// (Section và Chip)
function Section({ title, children }) {
  return (
    <div className="bg-white border rounded-2xl p-4">
      <div className="text-xs font-semibold text-gray-500 uppercase mb-3">
        {title}
      </div>
      <div className="flex flex-wrap gap-2">{children}</div>
    </div>
  );
}
function Chip({ active, onClick, onDelete, children }) {
  const handleDelete = (e) => {
    e.stopPropagation(); 
    if (onDelete) onDelete();
  };
  return (
    <button
      onClick={onClick}
      className={
        "group relative flex items-center gap-1.5 px-3 py-1.5 rounded-full border text-sm transition-colors " +
        (active ? "bg-black text-white border-black" : "bg-white hover:bg-gray-50")
      }
    >
      <span className="flex items-center justify-center w-full h-full text-center leading-none">
        {children}
      </span>
      {onDelete && (
        <span
          onClick={handleDelete}
          className={`
            w-4 h-4 rounded-full flex items-center justify-center 
            text-xs font-normal
            opacity-50 group-hover:opacity-100
            ${active 
              ? "text-gray-300 hover:text-white hover:bg-gray-700"
              : "text-gray-500 hover:text-black hover:bg-gray-200"
            }
          `}
          aria-label="Xoá"
        >
          ✕
        </span>
      )}
    </button>
  );
}

// (Hàm đếm ngược)
function formatCountdown(targetTime) {
  const now = new Date();
  const target = new Date(targetTime);
  const diffMs = target.getTime() - now.getTime();
  
  if (diffMs <= 0) return "Bây giờ";

  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  const diffHours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  const timeStr = target.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  const isMidnight = target.getHours() === 0 && target.getMinutes() === 0;

  if (diffDays > 1) {
    return `Ngày ${target.toLocaleDateString()}`;
  }
  const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  if (target.getTime() >= tomorrow.getTime()) {
     return `Ngày mai ${isMidnight ? '' : `lúc ${timeStr}`}`;
  }
  if (diffHours > 0) {
    return `Hôm nay lúc ${timeStr}`;
  }
  if (diffMins > 0) {
    return `Trong ${diffMins} phút`;
  }
  return "Ngay bây giờ";
}


export default function Sidebar({
  status,
  setStatus,
  priority,
  setPriority,
  categories = [],
  category,
  setCategory,
  onAddCategory,
  onDeleteCategory,
  onLogout, // Prop cho Đăng xuất
  selectedTags,
  toggleTag,
  clearAll,
  tags = [],
  nextReminders = [], 
}) {
  return (
    <aside className="w-[280px] shrink-0 space-y-3">
      {/* (Bộ lọc nhanh) */}
      <div className="bg-white border rounded-2xl p-4">
        <div className="text-xs font-semibold text-gray-500 uppercase mb-3">
          Bộ lọc nhanh
        </div>
        <div className="grid grid-cols-2 gap-2 ">
          {[
            ["all","Tất cả"],
            ["active","Đang mở"],
            ["completed","Hoàn thành"],
            ["overdue","Trễ hạn"],
            ["today","Trong ngày"],
          ].map(([key,label]) => (
            <Chip key={key} active={status===key} onClick={()=>setStatus(key)}>{label}</Chip>
          ))}
        </div>
        <div className="mt-3">
          <button onClick={clearAll} className="text-sm underline text-gray-600">Xoá bộ lọc</button>
        </div>
      </div>

      {/* (Category) */}
      <Section title="Danh mục (Category)">
        <Chip active={category==="all"} onClick={()=>setCategory("all")}>Tất cả</Chip>
        {categories.map((c)=>(
          <Chip 
            key={c.id} 
            active={category===c.id} 
            onClick={()=>setCategory(c.id)}
            onDelete={() => onDeleteCategory(c)}
          >
            {c.name}
          </Chip>
        ))}
        <button 
          onClick={onAddCategory} 
          className="px-3 py-1.5 rounded-full border text-sm text-blue-600 border-blue-200 hover:bg-blue-50"
        >
          + Thêm
        </button>
      </Section>

      {/* (Priority) */}
      <Section title="Mức ưu tiên">
        {["Low","Medium","High","Urgent"].map((p)=>(
          <Chip key={p} active={priority===p} onClick={()=>setPriority(p)}>{p}</Chip>
        ))}
        <Chip active={priority==="all"} onClick={()=>setPriority("all")}>All</Chip>
      </Section>

      {/* (Tags) */}
      <Section title="Nhãn (tags)">
        {tags.length===0 ? (
          <div className="text-sm text-gray-500">Chưa có tag</div>
        ) : tags.map((t)=>{
          const act = selectedTags.includes(t);
          return (
            <Chip key={t} active={act} onClick={()=>toggleTag(t)}>{t}</Chip>
          );
        })}
      </Section>
      
      {/* (Nhắc nhở) */}
      <div className="bg-white border rounded-2xl p-4">
        <div className="text-xs font-semibold text-gray-500 uppercase mb-3">
          Nhắc nhở sắp tới
        </div>
        {nextReminders.length===0 ? (
          <div className="text-sm text-gray-500">Không có nhắc nhở.</div>
        ) : (
          <ul className="space-y-2">
            {nextReminders.map((reminder)=>(
              <li key={reminder.task.id} className="text-sm">
                <div className="font-medium">{reminder.task.title}</div>
                <div className="text-gray-500">
                  {reminder.is_daily 
                    ? `Hằng ngày lúc ${reminder.task.daily_reminder_time.slice(0, 5)}`
                    : formatCountdown(reminder.next_remind_iso)
                  }
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* (Đăng xuất) */}
      <div className="bg-white border rounded-2xl p-4">
        <button
          onClick={onLogout}
          className="w-full px-3 py-2 rounded-lg border text-sm text-red-600 border-red-200 hover:bg-red-50"
        >
          Đăng xuất
        </button>
      </div>
    </aside>
  );
}