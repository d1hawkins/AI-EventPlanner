import { useState, useEffect } from 'react';
import { eventsAPI } from '../api/events';

export const useEvents = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await eventsAPI.getEvents();
      setEvents(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching events:', err);
      setError(err.message || 'Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  const createEvent = async (eventData) => {
    try {
      const newEvent = await eventsAPI.createEvent(eventData);
      setEvents([...events, newEvent]);
      return newEvent;
    } catch (err) {
      console.error('Error creating event:', err);
      throw err;
    }
  };

  const updateEvent = async (id, eventData) => {
    try {
      const updatedEvent = await eventsAPI.updateEvent(id, eventData);
      setEvents(events.map((e) => (e.id === id ? updatedEvent : e)));
      return updatedEvent;
    } catch (err) {
      console.error('Error updating event:', err);
      throw err;
    }
  };

  const deleteEvent = async (id) => {
    try {
      await eventsAPI.deleteEvent(id);
      setEvents(events.filter((e) => e.id !== id));
    } catch (err) {
      console.error('Error deleting event:', err);
      throw err;
    }
  };

  return {
    events,
    loading,
    error,
    fetchEvents,
    createEvent,
    updateEvent,
    deleteEvent,
  };
};
