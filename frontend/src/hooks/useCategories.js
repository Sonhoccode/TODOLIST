import { useState, useCallback } from "react";
import {
  listCategories,
  createCategory as apiCreateCategory,
  deleteCategory as apiDeleteCategory,
} from "../api/tasks";

/**
 * Custom hook để quản lý categories
 */
export function useCategories() {
  const [categories, setCategories] = useState([]);
  const [categoryError, setCategoryError] = useState("");

  /**
   * Load categories
   */
  const loadCategories = useCallback(async () => {
    try {
      const catData = await listCategories();
      const categories = Array.isArray(catData)
        ? catData
        : catData.results || [];
      setCategories(categories);
    } catch (err) {
      console.error("Lỗi khi tải categories:", err);
    }
  }, []);

  /**
   * Tạo category mới
   */
  const createCategory = async (name) => {
    setCategoryError("");

    if (!name.trim()) {
      setCategoryError("Tên danh mục không được để trống.");
      return false;
    }

    const existed = categories.some(
      (c) => c.name.trim().toLowerCase() === name.trim().toLowerCase()
    );
    if (existed) {
      setCategoryError("Danh mục này đã tồn tại. Vui lòng dùng tên khác.");
      return false;
    }

    try {
      await apiCreateCategory({ name: name.trim() });
      await loadCategories();
      return true;
    } catch (err) {
      console.error("Lỗi khi tạo category:", err);
      if (err.response && err.response.data && err.response.data.name) {
        setCategoryError(err.response.data.name[0]);
      } else {
        setCategoryError("Không thể tạo danh mục. Vui lòng thử lại.");
      }
      return false;
    }
  };

  /**
   * Xóa category
   */
  const deleteCategory = async (id) => {
    try {
      await apiDeleteCategory(id);
      await loadCategories();
      return true;
    } catch (err) {
      console.error("Lỗi khi xóa category:", err);
      throw new Error(
        "Đã xảy ra lỗi khi xóa danh mục. (Có thể do vẫn còn công việc liên quan?)"
      );
    }
  };

  return {
    categories,
    setCategories,
    categoryError,
    setCategoryError,
    loadCategories,
    createCategory,
    deleteCategory,
  };
}
