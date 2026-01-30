import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  listTasks,
  createTask as apiCreateTask,
  updateTask as apiUpdateTask,
  deleteTask as apiDeleteTask,
  toggleTaskStatus,
  listSharedWithMe,
} from "../api/tasks";

/**
 * Custom hook để quản lý tasks
 * Handles CRUD operations và state management
 */
export function useTaskManager() {
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  /**
   * Load tasks với filters
   */
  const loadTasks = useCallback(
    async (filters = {}) => {
      setLoading(true);
      try {
        const { status, priority, category } = filters;

        if (status === "shared") {
          const sharedData = await listSharedWithMe();
          const mappedTasks = sharedData.map((item) => ({
            ...item.task_details,
            permission: item.permission,
            shared_by: item.shared_by,
            is_shared: true,
          }));
          setTasks(mappedTasks);
        } else {
          const params = {};
          if (status === "completed") params.completed = true;
          if (status === "active") params.completed = false;
          if (priority !== "all") params.priority = priority;
          if (category !== "all") params.category = category;

          const taskData = await listTasks(params);
          const tasks = Array.isArray(taskData)
            ? taskData
            : taskData.results || [];
          setTasks(tasks);
        }
      } catch (err) {
        console.error("Lỗi khi tải tasks:", err);
        if (err.response && err.response.status === 401) {
          localStorage.removeItem("token");
          navigate("/login");
        }
      } finally {
        setLoading(false);
      }
    },
    [navigate]
  );

  /**
   * Tạo task mới
   */
  const createTask = async (payload) => {
    const savedTask = await apiCreateTask(payload);
    return savedTask;
  };

  /**
   * Cập nhật task
   */
  const updateTask = async (id, payload) => {
    const savedTask = await apiUpdateTask(id, payload);
    return savedTask;
  };

  /**
   * Xóa task
   */
  const deleteTask = async (id) => {
    await apiDeleteTask(id);
  };

  /**
   * Toggle task status (optimistic update)
   */
  const toggleTask = async (task) => {
    // Optimistic update
    setTasks((currentTasks) =>
      currentTasks.map((t) =>
        t.id === task.id ? { ...t, completed: !task.completed } : t
      )
    );

    try {
      await toggleTaskStatus(task.id);
    } catch (err) {
      console.error("Lỗi khi toggle, hoàn tác lại:", err);
      // Revert on error
      setTasks((currentTasks) =>
        currentTasks.map((t) =>
          t.id === task.id ? { ...t, completed: !t.completed } : t
        )
      );
    }
  };

  return {
    tasks,
    loading,
    setTasks,
    loadTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
  };
}
