import { useState, useEffect, useCallback, useMemo } from 'react';
import eventsService from '../services/eventsService';
import { getErrorMessage } from '../api/client';

/**
 * useEvents - Custom hook for events data management
 *
 * Features:
 * - Fetch all events with filters
 * - Create, update, delete events
 * - Loading and error states
 * - Automatic refetch after mutations
 *
 * Usage:
 * const { events, loading, error, createEvent, updateEvent, deleteEvent, refetch } = useEvents();
 */

export const useEvents = (filters = {}) => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Stabilize filters object to prevent infinite loops when using default empty object
  const stableFilters = useMemo(() => filters, [JSON.stringify(filters)]);

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await eventsService.getAll(stableFilters);
      setEvents(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [stableFilters]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const createEvent = useCallback(async (eventData) => {
    try {
      const newEvent = await eventsService.create(eventData);
      setEvents((prev) => [newEvent, ...prev]);
      return newEvent;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, []);

  const updateEvent = useCallback(async (id, eventData) => {
    try {
      const updatedEvent = await eventsService.update(id, eventData);
      setEvents((prev) =>
        prev.map((event) => (event.id === id ? updatedEvent : event))
      );
      return updatedEvent;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, []);

  const deleteEvent = useCallback(async (id) => {
    try {
      await eventsService.delete(id);
      setEvents((prev) => prev.filter((event) => event.id !== id));
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, []);

  return {
    events,
    loading,
    error,
    createEvent,
    updateEvent,
    deleteEvent,
    refetch: fetchEvents,
  };
};

/**
 * useEvent - Custom hook for single event data
 *
 * Usage:
 * const { event, loading, error, update, refetch } = useEvent(eventId);
 */

export const useEvent = (eventId) => {
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchEvent = useCallback(async () => {
    if (!eventId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await eventsService.getById(eventId);
      setEvent(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    fetchEvent();
  }, [fetchEvent]);

  const update = useCallback(async (eventData) => {
    try {
      const updatedEvent = await eventsService.update(eventId, eventData);
      setEvent(updatedEvent);
      return updatedEvent;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  return {
    event,
    loading,
    error,
    update,
    refetch: fetchEvent,
  };
};

/**
 * useEventTasks - Custom hook for event tasks management
 *
 * Usage:
 * const { tasks, loading, createTask, updateTask, deleteTask, toggleComplete } = useEventTasks(eventId);
 */

export const useEventTasks = (eventId) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTasks = useCallback(async () => {
    if (!eventId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await eventsService.getTasks(eventId);
      setTasks(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = useCallback(async (taskData) => {
    try {
      const newTask = await eventsService.createTask(eventId, taskData);
      setTasks((prev) => [...prev, newTask]);
      return newTask;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const updateTask = useCallback(async (taskId, taskData) => {
    try {
      const updatedTask = await eventsService.updateTask(eventId, taskId, taskData);
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      return updatedTask;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const deleteTask = useCallback(async (taskId) => {
    try {
      await eventsService.deleteTask(eventId, taskId);
      setTasks((prev) => prev.filter((task) => task.id !== taskId));
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const toggleComplete = useCallback(async (taskId, completed) => {
    try {
      const updatedTask = await eventsService.toggleTaskComplete(eventId, taskId, completed);
      setTasks((prev) =>
        prev.map((task) => (task.id === taskId ? updatedTask : task))
      );
      return updatedTask;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  return {
    tasks,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    refetch: fetchTasks,
  };
};

/**
 * useEventGuests - Custom hook for event guests management
 *
 * Usage:
 * const { guests, loading, addGuest, updateGuest, removeGuest } = useEventGuests(eventId);
 */

export const useEventGuests = (eventId) => {
  const [guests, setGuests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGuests = useCallback(async () => {
    if (!eventId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await eventsService.getGuests(eventId);
      setGuests(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    fetchGuests();
  }, [fetchGuests]);

  const addGuest = useCallback(async (guestData) => {
    try {
      const newGuest = await eventsService.addGuest(eventId, guestData);
      setGuests((prev) => [...prev, newGuest]);
      return newGuest;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const updateGuest = useCallback(async (guestId, guestData) => {
    try {
      const updatedGuest = await eventsService.updateGuest(eventId, guestId, guestData);
      setGuests((prev) =>
        prev.map((guest) => (guest.id === guestId ? updatedGuest : guest))
      );
      return updatedGuest;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const removeGuest = useCallback(async (guestId) => {
    try {
      await eventsService.removeGuest(eventId, guestId);
      setGuests((prev) => prev.filter((guest) => guest.id !== guestId));
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  return {
    guests,
    loading,
    error,
    addGuest,
    updateGuest,
    removeGuest,
    refetch: fetchGuests,
  };
};

/**
 * useEventBudget - Custom hook for event budget management
 *
 * Usage:
 * const { budget, expenses, loading, updateBudget, addExpense } = useEventBudget(eventId);
 */

export const useEventBudget = (eventId) => {
  const [budget, setBudget] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBudgetAndExpenses = useCallback(async () => {
    if (!eventId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const [budgetData, expensesData] = await Promise.all([
        eventsService.getBudget(eventId),
        eventsService.getExpenses(eventId),
      ]);
      setBudget(budgetData);
      setExpenses(expensesData);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    fetchBudgetAndExpenses();
  }, [fetchBudgetAndExpenses]);

  const updateBudget = useCallback(async (budgetData) => {
    try {
      const updatedBudget = await eventsService.updateBudget(eventId, budgetData);
      setBudget(updatedBudget);
      return updatedBudget;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const addExpense = useCallback(async (expenseData) => {
    try {
      const newExpense = await eventsService.addExpense(eventId, expenseData);
      setExpenses((prev) => [...prev, newExpense]);
      // Refetch budget to get updated spent amount
      const updatedBudget = await eventsService.getBudget(eventId);
      setBudget(updatedBudget);
      return newExpense;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const updateExpense = useCallback(async (expenseId, expenseData) => {
    try {
      const updatedExpense = await eventsService.updateExpense(eventId, expenseId, expenseData);
      setExpenses((prev) =>
        prev.map((expense) => (expense.id === expenseId ? updatedExpense : expense))
      );
      // Refetch budget to get updated spent amount
      const updatedBudget = await eventsService.getBudget(eventId);
      setBudget(updatedBudget);
      return updatedExpense;
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  const deleteExpense = useCallback(async (expenseId) => {
    try {
      await eventsService.deleteExpense(eventId, expenseId);
      setExpenses((prev) => prev.filter((expense) => expense.id !== expenseId));
      // Refetch budget to get updated spent amount
      const updatedBudget = await eventsService.getBudget(eventId);
      setBudget(updatedBudget);
    } catch (err) {
      throw new Error(getErrorMessage(err));
    }
  }, [eventId]);

  return {
    budget,
    expenses,
    loading,
    error,
    updateBudget,
    addExpense,
    updateExpense,
    deleteExpense,
    refetch: fetchBudgetAndExpenses,
  };
};
