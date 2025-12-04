import React, { useState } from "react";
import { scheduleToday, scheduleWeek, applySchedule } from "../api/scheduler";

export default function AIScheduler({ onScheduleApplied }) {
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState(null);
  const [viewMode, setViewMode] = useState("today"); // today | week
  const [availableHours, setAvailableHours] = useState(8);
  const [startHour, setStartHour] = useState(9);

  const handleScheduleToday = async () => {
    setLoading(true);
    try {
      const result = await scheduleToday(availableHours, startHour);
      setSchedule(result);
      setViewMode("today");
    } catch (error) {
      alert("Lỗi khi tạo lịch: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleWeek = async () => {
    setLoading(true);
    try {
      const result = await scheduleWeek(6);
      setSchedule(result);
      setViewMode("week");
    } catch (error) {
      alert("Lỗi khi tạo lịch tuần: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleApplySchedule = async () => {
    if (!schedule || !schedule.schedule) return;

    setLoading(true);
    try {
      await applySchedule(schedule.schedule);
      alert("Đã áp dụng lịch thành công!");
      if (onScheduleApplied) onScheduleApplied();
      setSchedule(null);
    } catch (error) {
      alert("Lỗi khi áp dụng lịch: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getPriorityColor = (priority) => {
    const colors = {
      Urgent: "bg-red-100 text-red-800",
      High: "bg-orange-100 text-orange-800",
      Medium: "bg-yellow-100 text-yellow-800",
      Low: "bg-green-100 text-green-800",
    };
    return colors[priority] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="mb-6">
        <h2 className="text-lg font-bold mb-1">AI Task Scheduler</h2>
        <p className="text-sm text-gray-600">
          AI tự động xếp lịch công việc tối ưu
        </p>
      </div>

      {!schedule ? (
        <div className="space-y-4">
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1.5">
                Số giờ rảnh hôm nay
              </label>
              <input
                type="number"
                min="1"
                max="16"
                value={availableHours}
                onChange={(e) => setAvailableHours(Number(e.target.value))}
                className="w-full rounded-lg border px-3 py-2.5 text-sm"
                placeholder="Ví dụ: 6"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">
                Bắt đầu lúc (giờ)
              </label>
              <input
                type="number"
                min="0"
                max="23"
                value={startHour}
                onChange={(e) => setStartHour(Number(e.target.value))}
                className="w-full rounded-lg border px-3 py-2.5 text-sm"
                placeholder="Ví dụ: 9"
              />
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <button
              onClick={handleScheduleToday}
              disabled={loading}
              className="w-full px-4 py-3 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Đang xử lý..." : "Xếp lịch hôm nay"}
            </button>
            <button
              onClick={handleScheduleWeek}
              disabled={loading}
              className="w-full px-4 py-3 rounded-lg bg-purple-600 text-white font-medium hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Đang xử lý..." : "Xếp lịch cả tuần"}
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {viewMode === "today" && schedule.schedule && (
            <>
              <div className="p-4 bg-blue-50 rounded-lg mb-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <div className="font-semibold text-base">
                      Lịch làm việc hôm nay
                    </div>
                    <div className="text-sm text-gray-700 mt-0.5">
                      {schedule.schedule.length} công việc - Tổng{" "}
                      {schedule.total_hours.toFixed(1)} giờ /{" "}
                      {schedule.available_hours} giờ
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSchedule(null)}
                    className="flex-1 px-4 py-2 rounded-lg border bg-white hover:bg-gray-50 font-medium"
                  >
                    Hủy
                  </button>
                  <button
                    onClick={handleApplySchedule}
                    disabled={loading}
                    className="flex-1 px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 disabled:opacity-50 font-medium"
                  >
                    {loading ? "Đang áp dụng..." : "Áp dụng lịch"}
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {schedule.schedule.map((item, index) => (
                  <div
                    key={index}
                    className="border rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="font-semibold text-base mb-1">
                          {item.title}
                        </div>
                        <div className="text-sm text-gray-600">
                          {item.reason}
                        </div>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(
                          item.priority
                        )}`}
                      >
                        {item.priority}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-700">
                      <div className="font-medium">
                        {formatTime(item.start_time)} - {formatTime(item.end_time)}
                      </div>
                      <div className="text-gray-500">
                        ({item.duration_hours} giờ)
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {viewMode === "week" && schedule.weekly_schedule && (
            <>
              <div className="p-4 bg-purple-50 rounded-lg mb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-base">
                      Lịch làm việc cả tuần
                    </div>
                    <div className="text-sm text-gray-700 mt-0.5">
                      Đã xếp {schedule.total_tasks_scheduled} / {schedule.total_tasks} công việc
                    </div>
                  </div>
                  <button
                    onClick={() => setSchedule(null)}
                    className="px-4 py-2 rounded-lg border bg-white hover:bg-gray-50 font-medium"
                  >
                    Đóng
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {schedule.weekly_schedule.map((day, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3 pb-2 border-b">
                      <h3 className="font-bold text-base">{day.day}</h3>
                      <span className="text-sm text-gray-600 font-medium">
                        Tổng: {day.total_hours} giờ
                      </span>
                    </div>
                    {day.tasks.length > 0 ? (
                      <div className="space-y-2">
                        {day.tasks.map((task, taskIndex) => (
                          <div
                            key={taskIndex}
                            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                          >
                            <span className="text-sm font-medium flex-1">
                              {task.title}
                            </span>
                            <div className="flex items-center gap-3">
                              <span
                                className={`px-2.5 py-1 rounded-full text-xs font-medium ${getPriorityColor(
                                  task.priority
                                )}`}
                              >
                                {task.priority}
                              </span>
                              <span className="text-sm text-gray-600 font-medium min-w-[3rem] text-right">
                                {task.duration_hours} giờ
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-gray-500 text-center py-2">
                        Không có công việc
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
