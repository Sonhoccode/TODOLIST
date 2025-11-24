// src/api/reports.js
import client from "./client";

// Tổng quan tiến độ (completed / total)
export const getProgressReport = () =>
  client.get("/reports/progress/").then((r) => r.data);

// Timeline (để vẽ chart theo ngày)
export const getTimelineReport = (params) =>
  // params có thể là { start_date, end_date } nếu backend có filter
  client.get("/reports/timeline/", { params }).then((r) => r.data);

// Thống kê theo priority
export const getPriorityReport = () =>
  client.get("/reports/by-priority/").then((r) => r.data);
