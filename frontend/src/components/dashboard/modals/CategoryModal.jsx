import React, { useState } from "react";
import Modal, { Field } from "../../common/Modal";

/**
 * Category Modal - Thêm category mới
 */
export default function CategoryModal({
  open,
  onClose,
  onSave,
  error,
  setError,
}) {
  const [name, setName] = useState("");

  const handleSave = () => {
    onSave(name);
    setName("");
  };

  const handleClose = () => {
    setName("");
    setError("");
    onClose();
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Thêm danh mục mới"
      footer={
        <>
          <button
            onClick={handleClose}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition"
          >
            Hủy
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 transition"
          >
            Lưu
          </button>
        </>
      }
    >
      <div className="py-2">
        <Field label="Tên danh mục" required>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ví dụ: Công việc, Học tập..."
            className="w-full rounded-lg border border-gray-300 px-3 py-2 outline-none focus:border-gray-500 focus:ring-2 focus:ring-gray-200"
            autoFocus
          />
        </Field>

        {error && (
          <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
}
