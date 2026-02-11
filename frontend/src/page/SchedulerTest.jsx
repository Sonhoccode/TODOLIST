import React from "react";
import AIScheduler from "../components/AIScheduler";

export default function SchedulerTest() {
  const handleScheduleApplied = () => {
    alert("Schedule applied! Reload page to see changes.");
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">AI Task Scheduler Test</h1>
        <AIScheduler onScheduleApplied={handleScheduleApplied} />
      </div>
    </div>
  );
}
