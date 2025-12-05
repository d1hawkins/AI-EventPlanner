import apiClient from './client';

export const chatAPI = {
  // Get conversation history
  getConversation: async (conversationId) => {
    const response = await apiClient.get(`/agents/conversations/${conversationId}`);
    return response.data;
  },

  // Send message to AI
  sendMessage: async (conversationId, message) => {
    const response = await apiClient.post(`/agents/conversations/${conversationId}/messages`, {
      content: message,
      role: 'user',
    });
    return response.data;
  },

  // Create new conversation
  createConversation: async (eventId) => {
    const response = await apiClient.post('/agents/conversations', {
      event_id: eventId,
      title: 'Event Planning Chat',
    });
    return response.data;
  },

  // Get all conversations
  getConversations: async () => {
    const response = await apiClient.get('/agents/conversations');
    return response.data;
  },
};
