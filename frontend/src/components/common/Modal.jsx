import React from "react";

/**
 * Reusable Modal component
 */
export default function Modal({ open, onClose, title, children, footer }) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="w-full max-w-xl bg-white rounded-2xl shadow-2xl p-6 mx-4 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 pb-4 border-b">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <button
            onClick={onClose}
            className="px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50 transition text-sm font-medium"
          >
            Đóng
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">{children}</div>

        {/* Footer */}
        {footer && (
          <div className="mt-4 pt-4 border-t flex justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Field wrapper component
 */
export function Field({ label, children, required }) {
  return (
    <label className="block mb-3">
      <div className="text-sm font-medium mb-1.5 text-gray-700">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </div>
      {children}
    </label>
  );
}
