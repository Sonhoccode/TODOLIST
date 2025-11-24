import client from './client';

/**
 * Gửi message tới chatbot để tạo task
 * @param {string} message - Message từ user
 * @returns {Promise<{task: Object, response: string, prediction: Object}>}
 */
export const sendChatMessage = async (message) => {
  try {
    const response = await client.post('/todos/chatbot/', { message });
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};
