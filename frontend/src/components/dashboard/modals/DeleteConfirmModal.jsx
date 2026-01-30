import React from "react";
import Modal from "../../common/Modal";

/**
 * Delete Confirmation Modal
 * Reusable cho cả task và category
 */
export default function DeleteConfirmModal({
  open,
  onClose,
  onConfirm,
  title = "Xác nhận xóa",
  message,
  itemName,
}) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title={title}
      footer={
        <>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition"
          >
            Hủy
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition"
          >
            Xóa
          </button>
        </>
      }
    >
      <div className="py-4">
        <p className="text-gray-700 mb-2">
          {message || "Bạn có chắc chắn muốn xóa?"}
        </p>
        {itemName && (
          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg border">
            <span className="font-medium">Tên:</span> {itemName}
          </p>
        )}
      </div>
    </Modal>
  );
}
