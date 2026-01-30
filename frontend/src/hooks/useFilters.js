import { useState, useMemo } from "react";

/**
 * Custom hook để quản lý filters và search
 */
export function useFilters(tasks = []) {
  // Filter states
  const [status, setStatus] = useState("all");
  const [priority, setPriority] = useState("all");
  const [category, setCategory] = useState("all");
  const [selectedTags, setSelectedTags] = useState([]);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState("default");
  const [viewMode, setViewMode] = useState("list");

  /**
   * Toggle tag selection
   */
  const toggleTag = (tag) => {
    setSelectedTags((current) =>
      current.includes(tag)
        ? current.filter((t) => t !== tag)
        : [...current, tag]
    );
  };

  /**
   * Clear all filters
   */
  const clearAll = () => {
    setStatus("all");
    setPriority("all");
    setCategory("all");
    setSelectedTags([]);
    setSearch("");
  };

  /**
   * Get available tags from tasks
   */
  const availableTags = useMemo(() => {
    const tagSet = new Set();
    (tasks || []).forEach((t) =>
      (t.tags || []).forEach((tag) => tagSet.add(tag))
    );
    return Array.from(tagSet).sort((a, b) => a.localeCompare(b));
  }, [tasks]);

  /**
   * Filter and sort tasks
   */
  const filteredTasks = useMemo(() => {
    let data = tasks || [];

    // Filter by tags
    if (selectedTags.length > 0) {
      data = data.filter((t) =>
        selectedTags.every((tag) => (t.tags || []).includes(tag))
      );
    }

    // Filter by search
    if (search.trim()) {
      const query = search.trim().toLowerCase();
      data = data.filter(
        (t) =>
          t.title?.toLowerCase().includes(query) ||
          t.description?.toLowerCase().includes(query) ||
          (t.tags || []).some((tag) => tag.toLowerCase().includes(query))
      );
    }

    // Sort
    if (sortBy === "due_at") {
      data = [...data].sort((a, b) =>
        (a.due_at || "").localeCompare(b.due_at || "")
      );
    } else if (sortBy === "priority") {
      const weights = { Urgent: 3, High: 2, Medium: 1, Low: 0 };
      data = [...data].sort(
        (a, b) => (weights[b.priority] || 0) - (weights[a.priority] || 0)
      );
    } else if (sortBy === "created_at") {
      data = [...data].sort((a, b) =>
        (a.created_at || "").localeCompare(b.created_at || "")
      );
    }

    return data;
  }, [tasks, search, sortBy, selectedTags]);

  return {
    // States
    status,
    priority,
    category,
    selectedTags,
    search,
    sortBy,
    viewMode,

    // Setters
    setStatus,
    setPriority,
    setCategory,
    setSelectedTags,
    setSearch,
    setSortBy,
    setViewMode,

    // Actions
    toggleTag,
    clearAll,

    // Computed
    availableTags,
    filteredTasks,
  };
}
