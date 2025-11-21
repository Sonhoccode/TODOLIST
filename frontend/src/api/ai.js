import client from './client';

/**
 * Dự đoán xem task có hoàn thành đúng hạn không
 * @param {Object} taskData - Thông tin task
 * @param {string} taskData.priority - Mức độ ưu tiên (Low, Medium, High, Urgent)
 * @param {number} taskData.estimated_duration_min - Thời lượng ước tính (phút)
 * @param {number} taskData.start_hour - Giờ bắt đầu (0-23)
 * @param {number} taskData.day_of_week - Thứ trong tuần (1-7)
 * @param {number} taskData.task_id - (Optional) ID của task có sẵn
 * @returns {Promise<{on_time_prediction: number, confidence: number}>}
 */
export const predictTaskCompletion = async (taskData) => {
  try {
    const response = await client.post('/api/predict/', taskData);
    return response.data;
  } catch (error) {
    console.error('Error predicting task completion:', error);
    throw error;
  }
};

/**
 * Tính toán thông tin cần thiết cho AI prediction từ form data
 * @param {Object} formData - Dữ liệu từ form
 * @returns {Object} Data cho AI prediction
 */
export const prepareAIPredictionData = (formData) => {
  const now = new Date();
  
  // Lấy giờ bắt đầu
  let startHour = now.getHours();
  if (formData.planned_start_at) {
    const startDate = new Date(formData.planned_start_at);
    startHour = startDate.getHours();
  }
  
  // Lấy thứ trong tuần (1=Monday, 7=Sunday)
  let dayOfWeek = now.getDay();
  if (dayOfWeek === 0) dayOfWeek = 7; // Chuyển Sunday từ 0 thành 7
  if (formData.planned_start_at) {
    const startDate = new Date(formData.planned_start_at);
    dayOfWeek = startDate.getDay();
    if (dayOfWeek === 0) dayOfWeek = 7;
  }
  
  // Tính thời lượng ước tính
  let estimatedDuration = formData.estimated_duration_min || 60;
  if (!formData.estimated_duration_min && formData.due_at && formData.planned_start_at) {
    const start = new Date(formData.planned_start_at);
    const end = new Date(formData.due_at);
    estimatedDuration = Math.max(1, Math.floor((end - start) / (1000 * 60)));
  }
  
  return {
    priority: formData.priority || 'Medium',
    estimated_duration_min: estimatedDuration,
    start_hour: startHour,
    day_of_week: dayOfWeek,
    task_id: formData.id
  };
};
