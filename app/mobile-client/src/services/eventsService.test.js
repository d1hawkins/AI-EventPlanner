import { describe, it, expect, beforeEach, vi } from 'vitest';
import eventsService from './eventsService';
import apiClient from '../api/client';
import { mockEvent, mockEvents, mockTasks, mockGuests, mockBudget } from '../test/mockData';

// Mock the API client
vi.mock('../api/client', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('eventsService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('should fetch all events without filters', async () => {
      apiClient.get.mockResolvedValue({ data: mockEvents });

      const result = await eventsService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith('/events', { params: {} });
      expect(result).toEqual(mockEvents);
    });

    it('should fetch events with filters', async () => {
      apiClient.get.mockResolvedValue({ data: mockEvents });

      const filters = { status: 'active', search: 'birthday' };
      const result = await eventsService.getAll(filters);

      expect(apiClient.get).toHaveBeenCalledWith('/events', { params: filters });
      expect(result).toEqual(mockEvents);
    });
  });

  describe('getById', () => {
    it('should fetch a single event', async () => {
      apiClient.get.mockResolvedValue({ data: mockEvent });

      const result = await eventsService.getById('1');

      expect(apiClient.get).toHaveBeenCalledWith('/events/1');
      expect(result).toEqual(mockEvent);
    });
  });

  describe('create', () => {
    it('should create a new event', async () => {
      const newEvent = { name: 'New Event', date: '2024-12-25' };
      apiClient.post.mockResolvedValue({ data: mockEvent });

      const result = await eventsService.create(newEvent);

      expect(apiClient.post).toHaveBeenCalledWith('/events', newEvent);
      expect(result).toEqual(mockEvent);
    });
  });

  describe('update', () => {
    it('should update an event', async () => {
      const updates = { name: 'Updated Event' };
      apiClient.put.mockResolvedValue({ data: { ...mockEvent, ...updates } });

      const result = await eventsService.update('1', updates);

      expect(apiClient.put).toHaveBeenCalledWith('/events/1', updates);
      expect(result.name).toBe('Updated Event');
    });
  });

  describe('delete', () => {
    it('should delete an event', async () => {
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      const result = await eventsService.delete('1');

      expect(apiClient.delete).toHaveBeenCalledWith('/events/1');
      expect(result.success).toBe(true);
    });
  });

  describe('getTasks', () => {
    it('should fetch tasks for an event', async () => {
      apiClient.get.mockResolvedValue({ data: mockTasks });

      const result = await eventsService.getTasks('1');

      expect(apiClient.get).toHaveBeenCalledWith('/events/1/tasks');
      expect(result).toEqual(mockTasks);
    });
  });

  describe('createTask', () => {
    it('should create a task for an event', async () => {
      const newTask = { title: 'New Task' };
      apiClient.post.mockResolvedValue({ data: { ...newTask, id: '1' } });

      const result = await eventsService.createTask('1', newTask);

      expect(apiClient.post).toHaveBeenCalledWith('/events/1/tasks', newTask);
      expect(result.title).toBe('New Task');
    });
  });

  describe('updateTask', () => {
    it('should update a task', async () => {
      const updates = { status: 'completed' };
      apiClient.put.mockResolvedValue({ data: { ...mockTasks[0], ...updates } });

      const result = await eventsService.updateTask('1', '1', updates);

      expect(apiClient.put).toHaveBeenCalledWith('/events/1/tasks/1', updates);
      expect(result.status).toBe('completed');
    });
  });

  describe('deleteTask', () => {
    it('should delete a task', async () => {
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      const result = await eventsService.deleteTask('1', '1');

      expect(apiClient.delete).toHaveBeenCalledWith('/events/1/tasks/1');
      expect(result.success).toBe(true);
    });
  });

  describe('getGuests', () => {
    it('should fetch guests for an event', async () => {
      apiClient.get.mockResolvedValue({ data: mockGuests });

      const result = await eventsService.getGuests('1');

      expect(apiClient.get).toHaveBeenCalledWith('/events/1/guests');
      expect(result).toEqual(mockGuests);
    });
  });

  describe('addGuest', () => {
    it('should add a guest to an event', async () => {
      const newGuest = { name: 'New Guest', email: 'guest@example.com' };
      apiClient.post.mockResolvedValue({ data: { ...newGuest, id: '1' } });

      const result = await eventsService.addGuest('1', newGuest);

      expect(apiClient.post).toHaveBeenCalledWith('/events/1/guests', newGuest);
      expect(result.name).toBe('New Guest');
    });
  });

  describe('updateGuest', () => {
    it('should update a guest', async () => {
      const updates = { rsvp: 'accepted' };
      apiClient.put.mockResolvedValue({ data: { ...mockGuests[0], ...updates } });

      const result = await eventsService.updateGuest('1', '1', updates);

      expect(apiClient.put).toHaveBeenCalledWith('/events/1/guests/1', updates);
      expect(result.rsvp).toBe('accepted');
    });
  });

  describe('removeGuest', () => {
    it('should remove a guest', async () => {
      apiClient.delete.mockResolvedValue({ data: { success: true } });

      const result = await eventsService.removeGuest('1', '1');

      expect(apiClient.delete).toHaveBeenCalledWith('/events/1/guests/1');
      expect(result.success).toBe(true);
    });
  });

  describe('getBudget', () => {
    it('should fetch budget for an event', async () => {
      apiClient.get.mockResolvedValue({ data: mockBudget });

      const result = await eventsService.getBudget('1');

      expect(apiClient.get).toHaveBeenCalledWith('/events/1/budget');
      expect(result).toEqual(mockBudget);
    });
  });

  describe('addExpense', () => {
    it('should add an expense to budget', async () => {
      const expense = { category: 'Venue', amount: 1500 };
      apiClient.post.mockResolvedValue({ data: { ...expense, id: '1' } });

      const result = await eventsService.addExpense('1', expense);

      expect(apiClient.post).toHaveBeenCalledWith('/events/1/budget/expenses', expense);
      expect(result.amount).toBe(1500);
    });
  });

  describe('updateBudget', () => {
    it('should update budget', async () => {
      const updates = { total: 6000 };
      apiClient.put.mockResolvedValue({ data: { ...mockBudget, ...updates } });

      const result = await eventsService.updateBudget('1', updates);

      expect(apiClient.put).toHaveBeenCalledWith('/events/1/budget', updates);
      expect(result.total).toBe(6000);
    });
  });
});
