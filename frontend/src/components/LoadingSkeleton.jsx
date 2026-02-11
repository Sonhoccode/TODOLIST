import React from "react";

/**
 * Skeleton loader component để hiển thị khi đang load data
 */
export function TaskListSkeleton({ count = 5 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-white border rounded-2xl p-4 animate-pulse"
        >
          <div className="flex items-start gap-3">
            <div className="w-5 h-5 bg-gray-200 rounded"></div>
            <div className="flex-1 space-y-2">
              <div className="h-5 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-100 rounded w-1/2"></div>
            </div>
            <div className="flex gap-2">
              <div className="w-8 h-8 bg-gray-200 rounded"></div>
              <div className="w-8 h-8 bg-gray-200 rounded"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-white border rounded-2xl p-4 animate-pulse"
        >
          <div className="space-y-3">
            <div className="h-6 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-100 rounded w-full"></div>
            <div className="h-4 bg-gray-100 rounded w-2/3"></div>
            <div className="flex gap-2 mt-4">
              <div className="h-6 w-16 bg-gray-200 rounded-full"></div>
              <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function StatsSkeleton() {
  return (
    <div className="bg-white border rounded-2xl p-4 animate-pulse">
      <div className="space-y-3">
        <div className="h-5 bg-gray-200 rounded w-1/2"></div>
        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
        <div className="h-4 bg-gray-100 rounded w-2/3"></div>
      </div>
    </div>
  );
}
