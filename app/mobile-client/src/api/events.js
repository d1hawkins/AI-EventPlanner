import apiClient from './client';

export const eventsAPI = {
  // Get all events for the current organization
  getEvents: async () => {
    const response = await apiClient.get('/events');
    return response.data;
  },

  // Get single event by ID
  getEvent: async (id) => {
    const response = await apiClient.get(`/events/${id}`);
    return response.data;
  },

  // Create new event
  createEvent: async (eventData) => {
    const response = await apiClient.post('/events', eventData);
    return response.data;
  },

  // Update event
  updateEvent: async (id, eventData) => {
    const response = await apiClient.put(`/events/${id}`, eventData);
    return response.data;
  },

  // Delete event
  deleteEvent: async (id) => {
    const response = await apiClient.delete(`/events/${id}`);
    return response.data;
  },

  // Get event tasks
  getTasks: async (eventId) => {
    const response = await apiClient.get(`/events/${eventId}/tasks`);
    return response.data;
  },

  // Update task status
  updateTask: async (eventId, taskId, completed) => {
    const response = await apiClient.patch(`/events/${eventId}/tasks/${taskId}`, {
      completed,
    });
    return response.data;
  },
};
