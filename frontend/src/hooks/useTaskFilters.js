import { useMemo } from "react";

/**
 * Custom hook để xử lý filter và sort tasks
 */
export function useTaskFilters(tasks, { search, selectedTags, sortBy }) {
  return useMemo(() => {
    let data = tasks || [];

    // Filter by tags
    if (selectedTags.length > 0) {
      data = data.filter((t) =>
        selectedTags.every((tag) => (t.tags || []).includes(tag))
      );
    }

    // Filter by search
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      data = data.filter(
        (t) =>
          t.title?.toLowerCase().includes(q) ||
          t.description?.toLowerCase().includes(q) ||
          (t.tags || []).some((x) => x.toLowerCase().includes(q))
      );
    }

    // Sort
    if (sortBy === "due_at") {
      data = [...data].sort((a, b) =>
        (a.due_at || "").localeCompare(b.due_at || "")
      );
    } else if (sortBy === "priority") {
      const w = { Urgent: 3, High: 2, Medium: 1, Low: 0 };
      data = [...data].sort(
        (a, b) => (w[b.priority] || 0) - (w[a.priority] || 0)
      );
    } else if (sortBy === "created_at") {
      data = [...data].sort((a, b) =>
        (a.created_at || "").localeCompare(b.created_at || "")
      );
    }

    return data;
  }, [tasks, search, sortBy, selectedTags]);
}
