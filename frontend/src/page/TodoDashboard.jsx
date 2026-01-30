/**
 * TodoDashboard - Refactored version
 * Sử dụng custom hooks và components nhỏ để dễ maintain
 */
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

// Layout components
import Header from "../components/layout/Header";
import Sidebar from "../components/layout/Sidebar";
import TaskList from "../components/tasks/TaskList";
import TaskGrid from "../components/tasks/TaskGrid";

// Dashboard components
import ChatbotPanel from "../components/dashboard/ai/ChatbotPanel";
import CategoryModal from "../components/dashboard/modals/CategoryModal";
import ShareModal from "../components/dashboard/modals/ShareModal";
import DeleteConfirmModal from "../components/dashboard/modals/DeleteConfirmModal";

// Custom hooks
import { useTaskManager } from "../hooks/useTaskManager";
import { useCategories } from "../hooks/useCategories";
import { useFilters } from "../hooks/useFilters";

// APIs
import { logout } from "../api/auth";
import { shareTask } from "../api/share";

// ============== Main Component ==============

export default function TodoDashboard() {
  const navigate = useNavigate();

  // Custom hooks
  const taskManager = useTaskManager();
  const categoryManager = useCategories();
  const filters = useFilters(taskManager.tasks);

  // Modal states
  const [openAddCategory, setOpenAddCategory] = useState(false);
  const [sharingTask, setSharingTask] = useState(null);
  const [shareError, setShareError] = useState("");
  const [deletingTask, setDeletingTask] = useState(null);
  const [deletingCategory, setDeletingCategory] = useState(null);

  // ============== Load Data ==============

  useEffect(() => {
    categoryManager.loadCategories();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    taskManager.loadTasks({
      status: filters.status,
      priority: filters.priority,
      category: filters.category,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters.status, filters.priority, filters.category]);

  // ============== Handlers ==============

  const handleLogout = async () => {
    if (!window.confirm("Bạn có chắc muốn đăng xuất?")) return;
    try {
      await logout();
      navigate("/login");
    } catch (err) {
      console.error("Lỗi đăng xuất:", err);
      localStorage.removeItem("token");
      navigate("/login");
    }
  };

  const handleDeleteTask = async () => {
    if (!deletingTask) return;
    try {
      await taskManager.deleteTask(deletingTask.id);
      setDeletingTask(null);
      await taskManager.loadTasks({
        status: filters.status,
        priority: filters.priority,
        category: filters.category,
      });
    } catch (err) {
      console.error("Lỗi khi xóa:", err);
      alert("Đã xảy ra lỗi khi xóa.");
      setDeletingTask(null);
    }
  };

  const handleDeleteCategory = async () => {
    if (!deletingCategory) return;
    try {
      await categoryManager.deleteCategory(deletingCategory.id);
      setDeletingCategory(null);
      if (filters.category === deletingCategory.id) {
        filters.setCategory("all");
      }
      await taskManager.loadTasks({
        status: filters.status,
        priority: filters.priority,
        category: filters.category,
      });
    } catch (err) {
      alert(err.message);
      setDeletingCategory(null);
    }
  };

  const handleSaveCategory = async (name) => {
    const success = await categoryManager.createCategory(name);
    if (success) {
      setOpenAddCategory(false);
    }
  };

  const handleShare = async (email, permission) => {
    if (!sharingTask) return;
    if (!email.trim()) {
      setShareError("Email không được để trống.");
      return;
    }

    try {
      const res = await shareTask(sharingTask.id, email, permission);
      if (res.warning) {
        alert(`Đã chia sẻ công việc, nhưng có cảnh báo: ${res.warning}`);
      } else {
        alert("Đã chia sẻ công việc thành công.");
      }
      setSharingTask(null);
      setShareError("");
    } catch (err) {
      console.error("Lỗi chia sẻ task:", err);
      setShareError(
        err.response?.data?.error || "Không thể chia sẻ, thử lại sau."
      );
    }
  };

  const handleTaskCreated = () => {
    taskManager.loadTasks({
      status: filters.status,
      priority: filters.priority,
      category: filters.category,
    });
  };

  // ============== Render ==============

  return (
    <div className="min-h-screen bg-gray-50">
      <Header onCreate={() => alert("Tính năng tạo task sẽ được thêm sau")} />

      <div className="layout-container mx-auto px-6 py-16 flex gap-6">
        {/* Sidebar */}
        <Sidebar
          status={filters.status}
          setStatus={filters.setStatus}
          priority={filters.priority}
          setPriority={filters.setPriority}
          categories={categoryManager.categories}
          category={filters.category}
          setCategory={filters.setCategory}
          onAddCategory={() => setOpenAddCategory(true)}
          onDeleteCategory={setDeletingCategory}
          onLogout={handleLogout}
          selectedTags={filters.selectedTags}
          toggleTag={filters.toggleTag}
          clearAll={filters.clearAll}
          tags={filters.availableTags}
          nextReminders={[]}
        />

        {/* Main content */}
        <div className="flex-1 flex gap-6">
          {/* Task list section */}
          <section className="flex-1 space-y-4">
            {/* View mode & sort controls */}
            <div className="bg-white border rounded-2xl p-3 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => filters.setViewMode("list")}
                  className={`px-3 py-1.5 rounded-lg text-sm ${
                    filters.viewMode === "list"
                      ? "bg-gray-100 font-medium"
                      : "hover:bg-gray-50"
                  }`}
                >
                  List
                </button>
                <button
                  onClick={() => filters.setViewMode("grid")}
                  className={`px-3 py-1.5 rounded-lg text-sm ${
                    filters.viewMode === "grid"
                      ? "bg-gray-100 font-medium"
                      : "hover:bg-gray-50"
                  }`}
                >
                  Grid
                </button>
              </div>

              <div className="flex items-center gap-3">
                <label className="text-sm text-gray-600">Sắp xếp</label>
                <select
                  className="rounded-lg border px-3 py-2 bg-white text-sm"
                  value={filters.sortBy}
                  onChange={(e) => filters.setSortBy(e.target.value)}
                >
                  <option value="default">Mặc định</option>
                  <option value="due_at">Thời hạn</option>
                  <option value="priority">Mức ưu tiên</option>
                  <option value="created_at">Ngày tạo</option>
                </select>
              </div>
            </div>

            {/* Task list/grid */}
            {taskManager.loading ? (
              <div className="p-6 bg-white border rounded-2xl text-center text-gray-600">
                Đang tải…
              </div>
            ) : filters.viewMode === "list" ? (
              <TaskList
                items={filters.filteredTasks}
                onToggle={taskManager.toggleTask}
                onEdit={() => alert("Tính năng sửa task sẽ được thêm sau")}
                onDelete={setDeletingTask}
                onShare={setSharingTask}
              />
            ) : (
              <TaskGrid
                items={filters.filteredTasks}
                onToggle={taskManager.toggleTask}
                onEdit={() => alert("Tính năng sửa task sẽ được thêm sau")}
                onDelete={setDeletingTask}
                onShare={setSharingTask}
              />
            )}
          </section>

          {/* Right sidebar - AI Chatbot */}
          <aside className="w-[340px] shrink-0">
            <ChatbotPanel onTaskCreated={handleTaskCreated} />
          </aside>
        </div>
      </div>

      {/* Modals */}
      <CategoryModal
        open={openAddCategory}
        onClose={() => setOpenAddCategory(false)}
        onSave={handleSaveCategory}
        error={categoryManager.categoryError}
        setError={categoryManager.setCategoryError}
      />

      <ShareModal
        open={!!sharingTask}
        onClose={() => {
          setSharingTask(null);
          setShareError("");
        }}
        onShare={handleShare}
        task={sharingTask}
        error={shareError}
        setError={setShareError}
      />

      <DeleteConfirmModal
        open={!!deletingTask}
        onClose={() => setDeletingTask(null)}
        onConfirm={handleDeleteTask}
        title="Xóa công việc"
        message="Bạn có chắc chắn muốn xóa công việc này?"
        itemName={deletingTask?.title}
      />

      <DeleteConfirmModal
        open={!!deletingCategory}
        onClose={() => setDeletingCategory(null)}
        onConfirm={handleDeleteCategory}
        title="Xóa danh mục"
        message="Bạn có chắc chắn muốn xóa danh mục này?"
        itemName={deletingCategory?.name}
      />
    </div>
  );
}
