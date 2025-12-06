import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import {
  useEvents,
  useEvent,
  useEventTasks,
  useEventGuests,
  useEventBudget,
} from './useEvents';
import eventsService from '../services/eventsService';
import { mockEvents, mockEvent, mockTasks, mockGuests, mockBudget } from '../test/mockData';

// Mock the events service
vi.mock('../services/eventsService');

describe('useEvents', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useEvents());

      expect(result.current.events).toEqual([]);
      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();
    });
  });

  describe('Fetching Events', () => {
    it('should fetch all events on mount', async () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getAll).toHaveBeenCalledWith({});
      expect(result.current.events).toEqual(mockEvents);
      expect(result.current.error).toBeNull();
    });

    it('should fetch events with filters', async () => {
      const filters = { status: 'active' };
      eventsService.getAll.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useEvents(filters));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getAll).toHaveBeenCalledWith(filters);
      expect(result.current.events).toEqual(mockEvents);
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Failed to fetch events');
      eventsService.getAll.mockRejectedValue(error);
      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.events).toEqual([]);
      expect(result.current.error).toBe('Failed to fetch events');
    });
  });

  describe('Creating Events', () => {
    it('should create a new event', async () => {
      eventsService.getAll.mockResolvedValue([]);
      const newEvent = mockEvent;
      eventsService.create.mockResolvedValue(newEvent);

      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      let createdEvent;
      await act(async () => {
        createdEvent = await result.current.createEvent({ name: 'New Event' });
      });

      expect(eventsService.create).toHaveBeenCalledWith({ name: 'New Event' });
      expect(createdEvent).toEqual(newEvent);
      expect(result.current.events).toContainEqual(newEvent);
    });

    it('should throw error on create failure', async () => {
      eventsService.getAll.mockResolvedValue([]);
      const error = new Error('Create failed');
      eventsService.create.mockRejectedValue(error);

      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.createEvent({ name: 'New Event' });
        });
      }).rejects.toThrow('Create failed');
    });
  });

  describe('Updating Events', () => {
    it('should update an event', async () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      const updatedEvent = { ...mockEvent, name: 'Updated Event' };
      eventsService.update.mockResolvedValue(updatedEvent);

      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.updateEvent(mockEvent.id, { name: 'Updated Event' });
      });

      expect(eventsService.update).toHaveBeenCalledWith(mockEvent.id, { name: 'Updated Event' });
      expect(result.current.events).toContainEqual(updatedEvent);
    });

    it('should throw error on update failure', async () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      const error = new Error('Update failed');
      eventsService.update.mockRejectedValue(error);

      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.updateEvent(mockEvent.id, { name: 'Updated' });
        });
      }).rejects.toThrow('Update failed');
    });
  });

  describe('Deleting Events', () => {
    it('should delete an event', async () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      eventsService.delete.mockResolvedValue({});

      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const initialCount = result.current.events.length;

      await act(async () => {
        await result.current.deleteEvent(mockEvent.id);
      });

      expect(eventsService.delete).toHaveBeenCalledWith(mockEvent.id);
      expect(result.current.events).toHaveLength(initialCount - 1);
      expect(result.current.events.find(e => e.id === mockEvent.id)).toBeUndefined();
    });

    it('should throw error on delete failure', async () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      const error = new Error('Delete failed');
      eventsService.delete.mockRejectedValue(error);

      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.deleteEvent(mockEvent.id);
        });
      }).rejects.toThrow('Delete failed');
    });
  });

  describe('Refetch', () => {
    it('should refetch events', async () => {
      eventsService.getAll.mockResolvedValue(mockEvents);
      const { result } = renderHook(() => useEvents());

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      eventsService.getAll.mockClear();
      eventsService.getAll.mockResolvedValue([...mockEvents, mockEvent]);

      await act(async () => {
        await result.current.refetch();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getAll).toHaveBeenCalledTimes(1);
    });
  });
});

describe('useEvent', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      eventsService.getById.mockResolvedValue(mockEvent);
      const { result } = renderHook(() => useEvent('1'));

      expect(result.current.event).toBeNull();
      expect(result.current.loading).toBe(true);
      expect(result.current.error).toBeNull();
    });

    it('should not fetch if eventId is not provided', async () => {
      const { result } = renderHook(() => useEvent(null));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getById).not.toHaveBeenCalled();
      expect(result.current.event).toBeNull();
    });
  });

  describe('Fetching Event', () => {
    it('should fetch event by ID', async () => {
      eventsService.getById.mockResolvedValue(mockEvent);
      const { result } = renderHook(() => useEvent('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getById).toHaveBeenCalledWith('1');
      expect(result.current.event).toEqual(mockEvent);
      expect(result.current.error).toBeNull();
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Event not found');
      eventsService.getById.mockRejectedValue(error);
      const { result } = renderHook(() => useEvent('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.event).toBeNull();
      expect(result.current.error).toBe('Event not found');
    });

    it('should refetch when eventId changes', async () => {
      eventsService.getById.mockResolvedValue(mockEvent);
      const { result, rerender } = renderHook(
        ({ id }) => useEvent(id),
        { initialProps: { id: '1' } }
      );

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getById).toHaveBeenCalledWith('1');

      eventsService.getById.mockClear();
      eventsService.getById.mockResolvedValue({ ...mockEvent, id: '2' });

      rerender({ id: '2' });

      await waitFor(() => {
        expect(eventsService.getById).toHaveBeenCalledWith('2');
      });
    });
  });

  describe('Updating Event', () => {
    it('should update event', async () => {
      eventsService.getById.mockResolvedValue(mockEvent);
      const updatedEvent = { ...mockEvent, name: 'Updated' };
      eventsService.update.mockResolvedValue(updatedEvent);

      const { result } = renderHook(() => useEvent('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.update({ name: 'Updated' });
      });

      expect(eventsService.update).toHaveBeenCalledWith('1', { name: 'Updated' });
      expect(result.current.event).toEqual(updatedEvent);
    });

    it('should throw error on update failure', async () => {
      eventsService.getById.mockResolvedValue(mockEvent);
      const error = new Error('Update failed');
      eventsService.update.mockRejectedValue(error);

      const { result } = renderHook(() => useEvent('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await expect(async () => {
        await act(async () => {
          await result.current.update({ name: 'Updated' });
        });
      }).rejects.toThrow('Update failed');
    });
  });
});

describe('useEventTasks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Tasks', () => {
    it('should fetch tasks for an event', async () => {
      eventsService.getTasks.mockResolvedValue(mockTasks);
      const { result } = renderHook(() => useEventTasks('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getTasks).toHaveBeenCalledWith('1');
      expect(result.current.tasks).toEqual(mockTasks);
    });

    it('should not fetch if eventId is not provided', async () => {
      const { result } = renderHook(() => useEventTasks(null));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getTasks).not.toHaveBeenCalled();
    });

    it('should handle fetch errors', async () => {
      const error = new Error('Fetch failed');
      eventsService.getTasks.mockRejectedValue(error);
      const { result } = renderHook(() => useEventTasks('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.error).toBe('Fetch failed');
    });
  });

  describe('Creating Tasks', () => {
    it('should create a new task', async () => {
      eventsService.getTasks.mockResolvedValue([]);
      const newTask = mockTasks[0];
      eventsService.createTask.mockResolvedValue(newTask);

      const { result } = renderHook(() => useEventTasks('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.createTask({ title: 'New Task' });
      });

      expect(eventsService.createTask).toHaveBeenCalledWith('1', { title: 'New Task' });
      expect(result.current.tasks).toContainEqual(newTask);
    });
  });

  describe('Updating Tasks', () => {
    it('should update a task', async () => {
      eventsService.getTasks.mockResolvedValue(mockTasks);
      const updatedTask = { ...mockTasks[0], title: 'Updated Task' };
      eventsService.updateTask.mockResolvedValue(updatedTask);

      const { result } = renderHook(() => useEventTasks('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.updateTask(mockTasks[0].id, { title: 'Updated Task' });
      });

      expect(eventsService.updateTask).toHaveBeenCalledWith('1', mockTasks[0].id, {
        title: 'Updated Task',
      });
    });
  });

  describe('Deleting Tasks', () => {
    it('should delete a task', async () => {
      eventsService.getTasks.mockResolvedValue(mockTasks);
      eventsService.deleteTask.mockResolvedValue({});

      const { result } = renderHook(() => useEventTasks('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const initialCount = result.current.tasks.length;

      await act(async () => {
        await result.current.deleteTask(mockTasks[0].id);
      });

      expect(eventsService.deleteTask).toHaveBeenCalledWith('1', mockTasks[0].id);
      expect(result.current.tasks).toHaveLength(initialCount - 1);
    });
  });
});

describe('useEventGuests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Guests', () => {
    it('should fetch guests for an event', async () => {
      eventsService.getGuests.mockResolvedValue(mockGuests);
      const { result } = renderHook(() => useEventGuests('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getGuests).toHaveBeenCalledWith('1');
      expect(result.current.guests).toEqual(mockGuests);
    });

    it('should not fetch if eventId is not provided', async () => {
      const { result } = renderHook(() => useEventGuests(null));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getGuests).not.toHaveBeenCalled();
    });
  });

  describe('Managing Guests', () => {
    it('should add a guest', async () => {
      eventsService.getGuests.mockResolvedValue([]);
      const newGuest = mockGuests[0];
      eventsService.addGuest.mockResolvedValue(newGuest);

      const { result } = renderHook(() => useEventGuests('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.addGuest({ name: 'New Guest' });
      });

      expect(eventsService.addGuest).toHaveBeenCalledWith('1', { name: 'New Guest' });
      expect(result.current.guests).toContainEqual(newGuest);
    });

    it('should update a guest', async () => {
      eventsService.getGuests.mockResolvedValue(mockGuests);
      const updatedGuest = { ...mockGuests[0], rsvp: 'accepted' };
      eventsService.updateGuest.mockResolvedValue(updatedGuest);

      const { result } = renderHook(() => useEventGuests('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.updateGuest(mockGuests[0].id, { rsvp: 'accepted' });
      });

      expect(eventsService.updateGuest).toHaveBeenCalledWith('1', mockGuests[0].id, {
        rsvp: 'accepted',
      });
    });

    it('should remove a guest', async () => {
      eventsService.getGuests.mockResolvedValue(mockGuests);
      eventsService.removeGuest.mockResolvedValue({});

      const { result } = renderHook(() => useEventGuests('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      const initialCount = result.current.guests.length;

      await act(async () => {
        await result.current.removeGuest(mockGuests[0].id);
      });

      expect(eventsService.removeGuest).toHaveBeenCalledWith('1', mockGuests[0].id);
      expect(result.current.guests).toHaveLength(initialCount - 1);
    });
  });
});

describe('useEventBudget', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Fetching Budget', () => {
    it('should fetch budget and expenses', async () => {
      const mockExpenses = [{ id: '1', amount: 100 }];
      eventsService.getBudget.mockResolvedValue(mockBudget);
      eventsService.getExpenses.mockResolvedValue(mockExpenses);

      const { result } = renderHook(() => useEventBudget('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getBudget).toHaveBeenCalledWith('1');
      expect(eventsService.getExpenses).toHaveBeenCalledWith('1');
      expect(result.current.budget).toEqual(mockBudget);
      expect(result.current.expenses).toEqual(mockExpenses);
    });

    it('should not fetch if eventId is not provided', async () => {
      const { result } = renderHook(() => useEventBudget(null));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(eventsService.getBudget).not.toHaveBeenCalled();
      expect(eventsService.getExpenses).not.toHaveBeenCalled();
    });
  });

  describe('Updating Budget', () => {
    it('should update budget', async () => {
      eventsService.getBudget.mockResolvedValue(mockBudget);
      eventsService.getExpenses.mockResolvedValue([]);
      const updatedBudget = { ...mockBudget, total: 6000 };
      eventsService.updateBudget.mockResolvedValue(updatedBudget);

      const { result } = renderHook(() => useEventBudget('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      await act(async () => {
        await result.current.updateBudget({ total: 6000 });
      });

      expect(eventsService.updateBudget).toHaveBeenCalledWith('1', { total: 6000 });
      expect(result.current.budget).toEqual(updatedBudget);
    });
  });

  describe('Managing Expenses', () => {
    it('should add an expense and refetch budget', async () => {
      eventsService.getBudget.mockResolvedValue(mockBudget);
      eventsService.getExpenses.mockResolvedValue([]);
      const newExpense = { id: '1', amount: 100 };
      eventsService.addExpense.mockResolvedValue(newExpense);

      const { result } = renderHook(() => useEventBudget('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      eventsService.getBudget.mockResolvedValue({ ...mockBudget, spent: 100 });

      await act(async () => {
        await result.current.addExpense({ amount: 100 });
      });

      expect(eventsService.addExpense).toHaveBeenCalledWith('1', { amount: 100 });
      expect(eventsService.getBudget).toHaveBeenCalledTimes(2); // Initial + after add
    });

    it('should update an expense and refetch budget', async () => {
      const expense = { id: '1', amount: 100 };
      eventsService.getBudget.mockResolvedValue(mockBudget);
      eventsService.getExpenses.mockResolvedValue([expense]);
      const updatedExpense = { ...expense, amount: 150 };
      eventsService.updateExpense.mockResolvedValue(updatedExpense);

      const { result } = renderHook(() => useEventBudget('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      eventsService.getBudget.mockResolvedValue({ ...mockBudget, spent: 150 });

      await act(async () => {
        await result.current.updateExpense('1', { amount: 150 });
      });

      expect(eventsService.updateExpense).toHaveBeenCalledWith('1', '1', { amount: 150 });
      expect(eventsService.getBudget).toHaveBeenCalledTimes(2);
    });

    it('should delete an expense and refetch budget', async () => {
      const expense = { id: '1', amount: 100 };
      eventsService.getBudget.mockResolvedValue(mockBudget);
      eventsService.getExpenses.mockResolvedValue([expense]);
      eventsService.deleteExpense.mockResolvedValue({});

      const { result } = renderHook(() => useEventBudget('1'));

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      eventsService.getBudget.mockResolvedValue({ ...mockBudget, spent: 0 });

      await act(async () => {
        await result.current.deleteExpense('1');
      });

      expect(eventsService.deleteExpense).toHaveBeenCalledWith('1', '1');
      expect(eventsService.getBudget).toHaveBeenCalledTimes(2);
      expect(result.current.expenses).toHaveLength(0);
    });
  });
});
