import { useCallback } from "react";
import {
  createTask,
  updateTask,
  deleteTask,
  toggleTaskStatus,
} from "../api/tasks";
import { saveNotificationForTodo } from "../api/notifications";

/**
 * Custom hook để xử lý các actions của tasks
 */
export function useTaskActions(load) {
  const handleToggle = useCallback(
    async (taskId, currentCompleted, setTasks) => {
      // Optimistic update
      setTasks((currentTasks) =>
        currentTasks.map((task) =>
          task.id === taskId ? { ...task, completed: !currentCompleted } : task
        )
      );

      try {
        await toggleTaskStatus(taskId);
      } catch (err) {
        console.error("Lỗi khi toggle, hoàn tác lại:", err);
        // Rollback
        setTasks((currentTasks) =>
          currentTasks.map((task) =>
            task.id === taskId ? { ...task, completed: currentCompleted } : task
          )
        );
      }
    },
    []
  );

  const handleSave = useCallback(
    async (payload, editingId, notificationSettings) => {
      let taskId = editingId;
      let savedTask = null;

      if (editingId == null) {
        savedTask = await createTask(payload);
        taskId = savedTask.id;
      } else {
        savedTask = await updateTask(editingId, payload);
      }

      // Save notification settings
      if (notificationSettings) {
        try {
          await saveNotificationForTodo(
            taskId,
            notificationSettings.enabled,
            notificationSettings.minutes
          );
        } catch (err) {
          console.error("Lỗi lưu notification:", err);
        }
      }

      await load();
      return savedTask;
    },
    [load]
  );

  const handleDelete = useCallback(
    async (taskId) => {
      await deleteTask(taskId);
      await load();
    },
    [load]
  );

  return {
    handleToggle,
    handleSave,
    handleDelete,
  };
}
