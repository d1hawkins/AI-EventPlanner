import apiClient from '../api/client';

/**
 * Events Service
 *
 * Handles all event-related API calls including:
 * - CRUD operations for events
 * - Task management
 * - Guest management
 * - Budget tracking
 */

const eventsService = {
  /**
   * Get all events
   * @param {Object} filters - Optional filters (status, search, sort)
   * @returns {Promise<Array>} List of events
   */
  async getAll(filters = {}) {
    const params = new URLSearchParams();

    if (filters.status) params.append('status', filters.status);
    if (filters.search) params.append('search', filters.search);
    if (filters.sort) params.append('sort', filters.sort);
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const response = await apiClient.get(`/events?${params.toString()}`);
    return response.data;
  },

  /**
   * Get event by ID
   * @param {number} id - Event ID
   * @returns {Promise<Object>} Event details
   */
  async getById(id) {
    const response = await apiClient.get(`/events/${id}`);
    return response.data;
  },

  /**
   * Create new event
   * @param {Object} eventData - Event data
   * @returns {Promise<Object>} Created event
   */
  async create(eventData) {
    const response = await apiClient.post('/events', eventData);
    return response.data;
  },

  /**
   * Update event
   * @param {number} id - Event ID
   * @param {Object} eventData - Updated event data
   * @returns {Promise<Object>} Updated event
   */
  async update(id, eventData) {
    const response = await apiClient.put(`/events/${id}`, eventData);
    return response.data;
  },

  /**
   * Delete event
   * @param {number} id - Event ID
   * @returns {Promise<void>}
   */
  async delete(id) {
    await apiClient.delete(`/events/${id}`);
  },

  // ========== Task Management ==========

  /**
   * Get tasks for an event
   * @param {number} eventId - Event ID
   * @returns {Promise<Array>} List of tasks
   */
  async getTasks(eventId) {
    const response = await apiClient.get(`/events/${eventId}/tasks`);
    return response.data;
  },

  /**
   * Create task for event
   * @param {number} eventId - Event ID
   * @param {Object} taskData - Task data
   * @returns {Promise<Object>} Created task
   */
  async createTask(eventId, taskData) {
    const response = await apiClient.post(`/events/${eventId}/tasks`, taskData);
    return response.data;
  },

  /**
   * Update task
   * @param {number} eventId - Event ID
   * @param {number} taskId - Task ID
   * @param {Object} taskData - Updated task data
   * @returns {Promise<Object>} Updated task
   */
  async updateTask(eventId, taskId, taskData) {
    const response = await apiClient.put(`/events/${eventId}/tasks/${taskId}`, taskData);
    return response.data;
  },

  /**
   * Delete task
   * @param {number} eventId - Event ID
   * @param {number} taskId - Task ID
   * @returns {Promise<void>}
   */
  async deleteTask(eventId, taskId) {
    await apiClient.delete(`/events/${eventId}/tasks/${taskId}`);
  },

  /**
   * Toggle task completion
   * @param {number} eventId - Event ID
   * @param {number} taskId - Task ID
   * @param {boolean} completed - Completion status
   * @returns {Promise<Object>} Updated task
   */
  async toggleTaskComplete(eventId, taskId, completed) {
    const response = await apiClient.patch(`/events/${eventId}/tasks/${taskId}`, { completed });
    return response.data;
  },

  // ========== Guest Management ==========

  /**
   * Get guests for an event
   * @param {number} eventId - Event ID
   * @returns {Promise<Array>} List of guests
   */
  async getGuests(eventId) {
    const response = await apiClient.get(`/events/${eventId}/guests`);
    return response.data;
  },

  /**
   * Add guest to event
   * @param {number} eventId - Event ID
   * @param {Object} guestData - Guest data (name, email, rsvp_status)
   * @returns {Promise<Object>} Created guest
   */
  async addGuest(eventId, guestData) {
    const response = await apiClient.post(`/events/${eventId}/guests`, guestData);
    return response.data;
  },

  /**
   * Update guest
   * @param {number} eventId - Event ID
   * @param {number} guestId - Guest ID
   * @param {Object} guestData - Updated guest data
   * @returns {Promise<Object>} Updated guest
   */
  async updateGuest(eventId, guestId, guestData) {
    const response = await apiClient.put(`/events/${eventId}/guests/${guestId}`, guestData);
    return response.data;
  },

  /**
   * Remove guest from event
   * @param {number} eventId - Event ID
   * @param {number} guestId - Guest ID
   * @returns {Promise<void>}
   */
  async removeGuest(eventId, guestId) {
    await apiClient.delete(`/events/${eventId}/guests/${guestId}`);
  },

  // ========== Budget Management ==========

  /**
   * Get budget details for event
   * @param {number} eventId - Event ID
   * @returns {Promise<Object>} Budget details
   */
  async getBudget(eventId) {
    const response = await apiClient.get(`/events/${eventId}/budget`);
    return response.data;
  },

  /**
   * Update event budget
   * @param {number} eventId - Event ID
   * @param {Object} budgetData - Budget data (total_budget)
   * @returns {Promise<Object>} Updated budget
   */
  async updateBudget(eventId, budgetData) {
    const response = await apiClient.put(`/events/${eventId}/budget`, budgetData);
    return response.data;
  },

  /**
   * Get expenses for event
   * @param {number} eventId - Event ID
   * @returns {Promise<Array>} List of expenses
   */
  async getExpenses(eventId) {
    const response = await apiClient.get(`/events/${eventId}/expenses`);
    return response.data;
  },

  /**
   * Add expense to event
   * @param {number} eventId - Event ID
   * @param {Object} expenseData - Expense data (category, amount, description)
   * @returns {Promise<Object>} Created expense
   */
  async addExpense(eventId, expenseData) {
    const response = await apiClient.post(`/events/${eventId}/expenses`, expenseData);
    return response.data;
  },

  /**
   * Update expense
   * @param {number} eventId - Event ID
   * @param {number} expenseId - Expense ID
   * @param {Object} expenseData - Updated expense data
   * @returns {Promise<Object>} Updated expense
   */
  async updateExpense(eventId, expenseId, expenseData) {
    const response = await apiClient.put(`/events/${eventId}/expenses/${expenseId}`, expenseData);
    return response.data;
  },

  /**
   * Delete expense
   * @param {number} eventId - Event ID
   * @param {number} expenseId - Expense ID
   * @returns {Promise<void>}
   */
  async deleteExpense(eventId, expenseId) {
    await apiClient.delete(`/events/${eventId}/expenses/${expenseId}`);
  },
};

export default eventsService;
