import React, { useState } from "react";
import Modal, { Field } from "../../common/Modal";

/**
 * Share Task Modal
 */
export default function ShareModal({
  open,
  onClose,
  onShare,
  task,
  error,
  setError,
}) {
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState("view");

  const handleShare = () => {
    onShare(email, permission);
  };

  const handleClose = () => {
    setEmail("");
    setPermission("view");
    setError("");
    onClose();
  };

  if (!task) return null;

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Chia sẻ công việc"
      footer={
        <>
          <button
            onClick={handleClose}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition"
          >
            Hủy
          </button>
          <button
            onClick={handleShare}
            className="px-4 py-2 rounded-lg bg-black text-white hover:bg-gray-800 transition"
          >
            Chia sẻ
          </button>
        </>
      }
    >
      <div className="py-2 space-y-4">
        {/* Task info */}
        <div className="p-3 bg-gray-50 rounded-lg border">
          <div className="text-sm text-gray-600 mb-1">Công việc:</div>
          <div className="font-medium text-gray-900">{task.title}</div>
        </div>

        {/* Email input */}
        <Field label="Email người nhận" required>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="example@email.com"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 outline-none focus:border-gray-500 focus:ring-2 focus:ring-gray-200"
            autoFocus
          />
        </Field>

        {/* Permission select */}
        <Field label="Quyền truy cập">
          <select
            value={permission}
            onChange={(e) => setPermission(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 bg-white outline-none focus:border-gray-500 focus:ring-2 focus:ring-gray-200"
          >
            <option value="view">Chỉ xem</option>
            <option value="edit">Chỉnh sửa</option>
          </select>
        </Field>

        {/* Error message */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
}
