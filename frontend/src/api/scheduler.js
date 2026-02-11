import client from "./client";

/**
 * AI Task Scheduler API
 */

// Schedule tasks for today
export const scheduleToday = async (availableHours = 8, startHour = 9) => {
  try {
    const response = await client.post("/schedule/today/", {
      available_hours: availableHours,
      start_hour: startHour,
    });
    return response.data;
  } catch (error) {
    console.error("Error scheduling today:", error);
    throw error;
  }
};

// Schedule tasks for the week
export const scheduleWeek = async (hoursPerDay = 6) => {
  try {
    const response = await client.post("/schedule/week/", {
      hours_per_day: hoursPerDay,
    });
    return response.data;
  } catch (error) {
    console.error("Error scheduling week:", error);
    throw error;
  }
};

// Apply schedule to tasks
export const applySchedule = async (schedule) => {
  try {
    const response = await client.post("/schedule/apply/", {
      schedule,
    });
    return response.data;
  } catch (error) {
    console.error("Error applying schedule:", error);
    throw error;
  }
};
