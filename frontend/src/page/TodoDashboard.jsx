import React, { useEffect, useMemo, useState, useCallback } from "react";
// --- THÊM CÁC IMPORT NÀY ---
import { useNavigate } from "react-router-dom";
import Header from "../components/layout/Header";
import Sidebar from "../components/layout/Sidebar";
import TaskList from "../components/tasks/TaskList";
import TaskGrid from "../components/tasks/TaskGrid"; 
import { 
  listTasks, createTask, updateTask, deleteTask, 
  listCategories, toggleTaskStatus, createCategory, deleteCategory 
} from "../api/tasks";
import { logout } from "../api/auth"; // Import logout từ file auth

// (emptyForm)
const emptyForm = {
  title: "", description: "", due_date: "", due_time: "",
  priority: "Medium", tags: "", is_daily: false, remind_date: "", remind_time: "", 
  completed: false, category: "",
};

// (Các hàm helper 'toLocalInputString', 'splitDateTime', 'Field', 'Modal' giữ nguyên)
function toLocalInputString(isoString) {
  if (!isoString) return "";
  const d = new Date(isoString);
  if (isNaN(d.getTime())) return "";
  const year = d.getFullYear();
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const day = d.getDate().toString().padStart(2, '0');
  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}
function splitDateTime(isoString) {
  if (!isoString) return { date: "", time: "" };
  const localString = toLocalInputString(isoString);
  if (!localString) return { date: "", time: "" };
  return {
    date: localString.slice(0, 10),
    time: localString.slice(11, 16),
  };
}
function Field({ label, children }) {
  return (
    <label className="block mb-3">
      <div className="text-sm font-medium mb-1">{label}</div>
      {children}
    </label>
  );
}
function Modal({ open, onClose, title, children, footer }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="px-3 py-1 rounded-md border hover:bg-gray-50"
          >
            Đóng
          </button>
        </div>
        <div className="max-h-[70vh] overflow-auto">{children}</div>
        <div className="mt-4 flex justify-end gap-2">{footer}</div>
      </div>
    </div>
  );
}
// ... (Kết thúc các hàm helper)


export default function TodoDashboard() {
  const navigate = useNavigate(); // Dùng để chuyển trang
  
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [viewMode, setViewMode] = useState("list"); 

  // (filters state)
  const [status, setStatus] = useState("all");
  const [priority, setPriority] = useState("all");
  const [category, setCategory] = useState("all");
  const [selectedTags, setSelectedTags] = useState([]);
  
  const toggleTag = (t) =>
    setSelectedTags((cur) => (cur.includes(t) ? cur.filter((x) => x !== t) : [...cur, t]));
  const clearAll = () => {
    setStatus("all"); setPriority("all"); setCategory("all"); setSelectedTags([]); setSearch("");
  };

  // (search state)
  const [search, setSearch] = useState("");
  useEffect(() => {
    const h = (e) => setSearch(e.detail || "");
    window.addEventListener("global-search", h);
    return () => window.removeEventListener("global-search", h);
  }, []);

  // (sort state)
  const [sortBy, setSortBy] = useState("default");

  // (modal state cho Task)
  const [openEdit, setOpenEdit] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);

  const [categoryError, setCategoryError] = useState("");

  // (modal state cho Category)
  const [openAddCategory, setOpenAddCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState("");

  // (modal state cho Xoá Task)
  const [deletingTask, setDeletingTask] = useState(null);
  
  // (modal state cho Xoá Category)
  const [deletingCategory, setDeletingCategory] = useState(null);
  

  // (Hàm load)
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (status === "completed") params.completed = true;
      if (status === "active") params.completed = false;
      if (priority !== "all") params.priority = priority;
      if (category !== "all") params.category = category;
      
      const [taskData, catData] = await Promise.all([
        listTasks(params),
        listCategories()
      ]);
      setTasks(taskData);
      setCategories(catData);
    } catch (err) {
      console.error("Lỗi khi tải dữ liệu:", err);
      // NẾU LỖI LÀ 401 (Token hết hạn) -> ĐÁ VỀ LOGIN
      if (err.response && err.response.status === 401) {
        localStorage.removeItem("token");
        navigate("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [status, priority, category, navigate]); // Thêm navigate

  // (Hàm loadCategories riêng biệt)
  const loadCategories = async () => {
    try {
      const catData = await listCategories();
      setCategories(catData);
    } catch (err) {
      console.error("Lỗi khi tải categories:", err);
    }
  };

  useEffect(() => {
    load();
  }, [load]);

  // --- HÀM 'openCreate' NẰM Ở ĐÂY ---
  function openCreate() { 
    setEditingId(null); 
    setForm(emptyForm); 
    setOpenEdit(true); 
  }
  
  function openUpdate(t) {
    setEditingId(t.id);
    const { date: due_date, time: due_time } = splitDateTime(t.due_at);
    
    const isDaily = !!t.daily_reminder_time;
    const remindISO = isDaily ? null : t.remind_at;
    const { date: remind_date, time: remind_time } = splitDateTime(remindISO);
    
    setForm({
      title: t.title || "",
      description: t.description || "",
      due_date: due_date,
      due_time: due_time,
      is_daily: isDaily,
      remind_date: remind_date,
      remind_time: isDaily ? (t.daily_reminder_time || "").slice(0, 5) : remind_time,
      priority: t.priority || "Medium",
      tags: (t.tags||[]).join(", "),
      completed: !!t.completed,
      category: t.category || "", 
    });
    setOpenEdit(true);
  }
  
  function toPayload(f) {
    let due_at_payload = null;
    if (f.due_date && f.due_time) {
      due_at_payload = new Date(`${f.due_date}T${f.due_time}`).toISOString();
    } else if (f.due_date) {
      due_at_payload = new Date(f.due_date).toISOString();
    }
    let remind_at_payload = null;
    let daily_reminder_time_payload = null;
    if (f.is_daily) {
      daily_reminder_time_payload = f.remind_time || null;
    } else {
      if (f.remind_date && f.remind_time) {
        remind_at_payload = new Date(`${f.remind_date}T${f.remind_time}`).toISOString();
      } else if (f.remind_date) {
        remind_at_payload = new Date(f.remind_date).toISOString();
      }
    }
    const payload = {
      title: f.title.trim(),
      description: f.description.trim(),
      priority: f.priority,
      completed: !!f.completed,
      tags: f.tags ? f.tags.split(",").map(x=>x.trim()).filter(Boolean) : [],
      due_at: due_at_payload,
      remind_at: remind_at_payload,
      daily_reminder_time: daily_reminder_time_payload,
      category: f.category ? Number(f.category) : null,
    };
    return payload;
  }
  
  async function onSave() {
    const payload = toPayload(form);
    if (!payload.title) return alert("Tiêu đề không được trống.");
    if (editingId == null) await createTask(payload); else await updateTask(editingId, payload);
    setOpenEdit(false); 
    await load(); 
  }
  
  async function onToggle(t) {
    setTasks(currentTasks => 
      currentTasks.map(task => 
        task.id === t.id ? { ...task, completed: !t.completed } : task
      )
    );
    try {
      await toggleTaskStatus(t.id);
    } catch (err) {
      console.error("Lỗi khi toggle, hoàn tác lại:", err);
      setTasks(currentTasks => 
        currentTasks.map(task => 
          task.id === t.id ? { ...task, completed: !task.completed } : task
        )
      );
    }
  }
  
  async function onDelete(t) { 
    setDeletingTask(t);
  }

  async function handleConfirmDelete() {
    if (!deletingTask) return;
    try {
      await deleteTask(deletingTask.id);
      setDeletingTask(null);
      await load(); 
    } catch (err) {
      console.error("Lỗi khi xoá:", err);
      alert("Đã xảy ra lỗi khi xoá.");
      setDeletingTask(null);
    }
  }

  async function onSaveCategory() {
    const name = newCategoryName.trim();
    setCategoryError(""); // reset lỗi trước mỗi lần lưu

    if (!name) {
      setCategoryError("Tên danh mục không được để trống.");
      return;
    }

    const existed = categories.some(
      (c) => c.name.trim().toLowerCase() === name.toLowerCase()
    );
    if (existed) {
      setCategoryError("Danh mục này đã tồn tại. Vui lòng dùng tên khác.");
      return;
    }

    try {
      await createCategory({ name });
      setNewCategoryName("");
      setCategoryError("");
      setOpenAddCategory(false);
      await loadCategories();
    } catch (err) {
      console.error("Lỗi khi tạo category:", err);

      if (err.response && err.response.data && err.response.data.name) {
        setCategoryError(err.response.data.name[0]);
      } else {
        setCategoryError("Không thể tạo danh mục. Vui lòng thử lại.");
      }
    }
  }



  async function handleConfirmDeleteCategory() {
    if (!deletingCategory) return;
    try {
      await deleteCategory(deletingCategory.id);
      setDeletingCategory(null);
      if (category === deletingCategory.id) {
        setCategory("all");
      }
      await load(); 
    } catch (err) {
      console.error("Lỗi khi xoá category:", err);
      alert("Đã xảy ra lỗi khi xoá danh mục. (Có thể do vẫn còn công việc liên quan?)");
      setDeletingCategory(null);
    }
  }

  // --- HÀM ĐĂNG XUẤT ---
  const handleLogout = async () => {
    if (!window.confirm("Bạn có chắc muốn đăng xuất?")) return;
    try {
      await logout(); // Gọi API để xoá token ở backend (trong auth.js)
      navigate("/login"); // Chuyển về trang login
    } catch (err) {
      console.error("Lỗi đăng xuất:", err);
      // Dù sao cũng xoá token ở local và chuyển hướng
      localStorage.removeItem("token");
      navigate("/login");
    }
  };

  // (useMemo: availableTags, nextReminders, view)
  const availableTags = useMemo(() => {
    const s = new Set(); (tasks || []).forEach(t => (t.tags||[]).forEach(x=>s.add(x)));
    return Array.from(s).sort((a,b)=>a.localeCompare(b));
  }, [tasks]);
  const nextReminders = useMemo(() => {
    const now = new Date();
    const nowTime = now.getTime();
    const reminders = [];
    (tasks || []).forEach(t => {
      if (t.completed) return; 
      let nextRemindISO = null;
      let isDaily = false;
      if (t.daily_reminder_time) {
        isDaily = true;
        const [hours, minutes] = t.daily_reminder_time.split(':').map(Number);
        const reminderToday = new Date();
        reminderToday.setHours(hours, minutes, 0, 0);
        if (reminderToday.getTime() > nowTime) {
          nextRemindISO = reminderToday.toISOString();
        } else {
          const reminderTomorrow = new Date(reminderToday.getTime() + 24 * 60 * 60 * 1000);
          nextRemindISO = reminderTomorrow.toISOString();
        }
      } 
      else if (t.remind_at) {
        const remindTime = new Date(t.remind_at).getTime();
        if (remindTime > nowTime) {
          nextRemindISO = t.remind_at;
        }
      }
      if (nextRemindISO) {
        reminders.push({ 
          task: t, 
          next_remind_iso: nextRemindISO,
          is_daily: isDaily 
        });
      }
    });
    return reminders
      .sort((a, b) => new Date(a.next_remind_iso).getTime() - new Date(b.next_remind_iso).getTime())
      .slice(0, 3);
  }, [tasks]);
  const view = useMemo(() => {
    let data = tasks || []; 
    if (selectedTags.length > 0) {
      data = data.filter(t => selectedTags.every(tag => (t.tags || []).includes(tag)));
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      data = data.filter(t =>
        t.title?.toLowerCase().includes(q) ||
        t.description?.toLowerCase().includes(q) ||
        (t.tags||[]).some(x => x.toLowerCase().includes(q))
      );
    }
    if (sortBy === "due_at") data = [...data].sort((a,b)=>(a.due_at||"").localeCompare(b.due_at||""));
    else if (sortBy === "priority") {
      const w = { Urgent:3, High:2, Medium:1, Low:0 };
      data = [...data].sort((a,b)=>(w[b.priority]||0)-(w[a.priority]||0));
    } else if (sortBy === "created_at") data = [...data].sort((a,b)=>(a.created_at||"").localeCompare(b.created_at||""));
    return data;
  }, [tasks, search, sortBy, selectedTags]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onCreate={openCreate} />
      <div className="max-w-7xl mx-auto px-6 py-6 flex gap-6">
        <Sidebar
          status={status} setStatus={setStatus}
          priority={priority} setPriority={setPriority}
          categories={categories}
          category={category}
          setCategory={setCategory}
          onAddCategory={() => setOpenAddCategory(true)}
          onDeleteCategory={setDeletingCategory} 
          onLogout={handleLogout} // <-- TRUYỀN HÀM XUỐNG
          selectedTags={selectedTags} toggleTag={toggleTag}
          clearAll={clearAll}
          tags={availableTags}
          nextReminders={nextReminders}
        />

        <section className="flex-1 space-y-4">
          <div className="bg-white border rounded-2xl p-3 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setViewMode('list')}
                className={`px-3 py-1.5 rounded-lg text-sm ${viewMode === 'list' ? 'bg-gray-100 font-medium' : 'hover:bg-gray-50'}`}
              >
                List
              </button>
              <button 
                onClick={() => setViewMode('grid')}
                className={`px-3 py-1.5 rounded-lg text-sm ${viewMode === 'grid' ? 'bg-gray-100 font-medium' : 'hover:bg-gray-50'}`}
              >
                Grid
              </button>
            </div>
            
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-600">Sắp xếp</label>
              <select
                className="rounded-lg border px-3 py-2 bg-white text-sm"
                value={sortBy}
                onChange={(e)=>setSortBy(e.target.value)}
              >
                <option value="default">Mặc định</option>
                <option value="due_at">Thời hạn</option>
                <option value="priority">Mức ưu tiên</option>
                <option value="created_at">Ngày tạo</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="p-6 bg-white border rounded-2xl">Đang tải…</div>
          ) : (
            viewMode === 'list' ? (
              <TaskList
                items={view}
                onToggle={onToggle}
                onEdit={openUpdate}
                onDelete={onDelete}
              />
            ) : (
              <TaskGrid
                items={view}
                onToggle={onToggle}
                onEdit={openUpdate}
                onDelete={onDelete}
              />
            )
          )}
        </section>
      </div>

      {/* Modal Thêm/Sửa Task */}
      <Modal
        open={openEdit}
        onClose={()=>setOpenEdit(false)}
        title={editingId==null ? "Thêm công việc" : "Cập nhật công việc"}
        footer={
          <>
            <button onClick={()=>setOpenEdit(false)} className="px-3 py-2 rounded-lg border hover:bg-gray-50">Huỷ</button>
            <button onClick={onSave} className="px-3 py-2 rounded-lg bg-black text-white">Lưu</button>
          </>
        }
      >
        <div className="grid grid-cols-1 gap-3">
          <Field label="Tiêu đề">
            <input
              className="w-full rounded-lg border px-3 py-2"
              value={form.title}
              onChange={(e)=>setForm({...form, title:e.target.value})}
              placeholder="Nhập tiêu đề"
            />
          </Field>
          <Field label="Mô tả">
            <textarea
              className="w-full rounded-lg border px-3 py-2"
              rows={3}
              value={form.description}
              onChange={(e)=>setForm({...form, description:e.target.value})}
              placeholder="Mô tả chi tiết"
            />
          </Field>
          
          <div className="grid grid-cols-2 gap-3">
            <Field label="Thời hạn (Ngày)">
              <input
                type="date"
                className="w-full rounded-lg border px-3 py-2"
                value={form.due_date}
                onChange={(e)=>setForm({...form, due_date:e.target.value})}
              />
            </Field>
            <Field label="Thời hạn (Giờ)">
              <input
                type="time"
                className="w-full rounded-lg border px-3 py-2"
                value={form.due_time}
                onChange={(e)=>setForm({...form, due_time:e.target.value})}
              />
            </Field>
          </div>

          <div className={`grid ${form.is_daily ? 'grid-cols-1' : 'grid-cols-2'} gap-3`}>
            {!form.is_daily && (
              <Field label="Nhắc lúc (Ngày)">
                <input
                  type="date"
                  className="w-full rounded-lg border px-3 py-2"
                  value={form.remind_date}
                  onChange={(e) => setForm({ ...form, remind_date: e.target.value })}
                />
              </Field>
            )}
            <Field label={form.is_daily ? "Giờ nhắc hằng ngày" : "Nhắc lúc (Giờ)"}>
              <input
                type="time"
                className="w-full rounded-lg border px-3 py-2"
                value={form.remind_time}
                onChange={(e) => setForm({ ...form, remind_time: e.target.value })}
              />
            </Field>
          </div>
          
          <label className="inline-flex items-center gap-2 -mt-2 mb-2">
            <input
              type="checkbox"
              checked={form.is_daily}
              onChange={(e) => setForm({ ...form, is_daily: e.target.checked, remind_date: "" })}
// Reset ngày nếu chọn
            />
            <span>Nhắc hằng ngày (chỉ dùng giờ)</span>
          </label>

          <div className="grid md:grid-cols-2 gap-3">
            <Field label="Ưu tiên">
              <select
                className="w-full rounded-lg border px-3 py-2"
                value={form.priority}
                onChange={(e)=>setForm({...form, priority:e.target.value})}
              >
                <option>Low</option><option>Medium</option><option>High</option><option>Urgent</option>
              </select>
            </Field>
            <Field label="Danh mục">
              <div className="flex items-center gap-2">
                <select
                  className="w-full flex-1 rounded-lg border px-3 py-2"
                  value={form.category}
                  onChange={(e)=>setForm({...form, category:e.target.value})}
                >
                  <option value="">(Không có)</option>
                  {categories.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                <button 
                  type="button" 
                  onClick={() => {
                    setNewCategoryName("");
                    setCategoryError("");
                    setOpenAddCategory(true);
                  }}
                  className="px-3 py-2 rounded-lg border hover:bg-gray-50 text-sm"
                  aria-label="Thêm danh mục mới"
                  title="Thêm danh mục mới"
                >
                  +
                </button>

              </div>
            </Field>
          </div>
          
          <Field label="Tags (phân tách bằng dấu phẩy)">
            <input
              className="w-full rounded-lg border px-3 py-2"
              value={form.tags}
              onChange={(e)=>setForm({...form, tags:e.target.value})}
              placeholder="api, backend, feature"
            />
          </Field>
          <label className="inline-flex items-center gap-2 mt-1">
            <input
              type="checkbox"
              checked={form.completed}
              onChange={(e)=>setForm({...form, completed:e.target.checked})}
            />
            <span>Đánh dấu hoàn thành</span>
          </label>
        </div>
      </Modal>

      {/* (Modal Xác nhận Xoá Task) */}
      <Modal
        open={!!deletingTask} 
        onClose={() => setDeletingTask(null)}
        title="Xác nhận xoá"
        footer={
          <>
            <button onClick={() => setDeletingTask(null)} className="px-3 py-2 rounded-lg border hover:bg-gray-50">Huỷ</button>
            <button onClick={handleConfirmDelete} className="px-3 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white">Xoá</button>
          </>
        }
      >
        <p>Bạn có chắc muốn xoá công việc này không?</p>
        <p className="font-semibold text-lg mt-2">{deletingTask?.title}</p>
      </Modal>

      {/* (Modal Thêm Category) */}
      <Modal
        open={openAddCategory}
        onClose={() => {
          setOpenAddCategory(false);
          setCategoryError("");
        }}
        title="Thêm danh mục mới"
        footer={
          <>
            <button
              onClick={() => {
                setOpenAddCategory(false);
                setCategoryError("");
              }}
              className="px-3 py-2 rounded-lg border hover:bg-gray-50"
            >
              Huỷ
            </button>
            <button onClick={onSaveCategory} className="px-3 py-2 rounded-lg bg-black text-white">
              Lưu
            </button>
          </>
        }
      >
        <Field label="Tên danh mục">
          <input
            className={
              "w-full rounded-lg border px-3 py-2 " +
              (categoryError ? "border-red-500 focus:ring-1 focus:ring-red-500" : "")
            }
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            placeholder="Ví dụ: Việc cá nhân"
          />
        </Field>

        {categoryError && (
          <p className="mt-1 text-sm text-red-600">
            {categoryError}
          </p>
        )}
      </Modal>

      {/* (Modal Xác nhận Xoá Category) */}
      <Modal
        open={!!deletingCategory} 
        onClose={() => setDeletingCategory(null)}
        title="Xác nhận xoá danh mục"
        footer={
          <>
            <button onClick={() => setDeletingCategory(null)} className="px-3 py-2 rounded-lg border hover:bg-gray-50">Huỷ</button>
            <button onClick={handleConfirmDeleteCategory} className="px-3 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white">Xoá</button>
          </>
        }
      >
        <p>Bạn có chắc muốn xoá danh mục <b>"{deletingCategory?.name}"</b>?</p>
        <p className="text-sm text-gray-600 mt-2">
          Lưu ý: Các công việc thuộc danh mục này sẽ không bị xoá, nhưng sẽ bị mất liên kết danh mục.
        </p>
      </Modal>

    </div>
  );
}