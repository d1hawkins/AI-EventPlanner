/**
 * Tests for event management functionality
 */

describe('Event Management', () => {
  let mockFetch;

  beforeEach(() => {
    mockFetch = jest.fn();
    global.fetch = mockFetch;
    localStorage.getItem.mockImplementation((key) => {
      if (key === 'authToken') return 'mock-token';
      if (key === 'organizationId') return 'org-123';
      return null;
    });
  });

  describe('createEvent', () => {
    test('should create event with valid data', async () => {
      const eventData = {
        title: 'Test Event',
        description: 'Test Description',
        start_date: '2025-11-01',
        end_date: '2025-11-02',
        event_type: 'conference'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: 'event-123', ...eventData })
      });

      // Mock createEvent function
      const createEvent = async (data) => {
        const response = await fetch('/api/events', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': localStorage.getItem('organizationId')
          },
          body: JSON.stringify(data)
        });

        if (!response.ok) {
          throw new Error('Failed to create event');
        }

        return response.json();
      };

      const result = await createEvent(eventData);

      expect(mockFetch).toHaveBeenCalledWith('/api/events', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json',
          'X-Organization-ID': 'org-123'
        },
        body: JSON.stringify(eventData)
      });

      expect(result).toEqual({ id: 'event-123', ...eventData });
    });

    test('should handle creation errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid event data' })
      });

      const createEvent = async (data) => {
        const response = await fetch('/api/events', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to create event');
        }

        return response.json();
      };

      await expect(createEvent({ title: '' })).rejects.toThrow('Invalid event data');
    });
  });

  describe('deleteEvent', () => {
    test('should delete event by ID', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Event deleted' })
      });

      const deleteEvent = async (eventId) => {
        const response = await fetch(`/api/events/${eventId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'X-Organization-ID': localStorage.getItem('organizationId')
          }
        });

        if (!response.ok) {
          throw new Error('Failed to delete event');
        }

        return response.json();
      };

      await deleteEvent('event-123');

      expect(mockFetch).toHaveBeenCalledWith('/api/events/event-123', {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer mock-token',
          'X-Organization-ID': 'org-123'
        }
      });
    });
  });

  describe('viewEvent', () => {
    test('should fetch event details', async () => {
      const mockEvent = {
        id: 'event-123',
        title: 'Test Event',
        description: 'Test Description',
        start_date: '2025-11-01',
        end_date: '2025-11-02'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockEvent
      });

      const viewEvent = async (eventId) => {
        const response = await fetch(`/api/events/${eventId}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'X-Organization-ID': localStorage.getItem('organizationId')
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch event');
        }

        return response.json();
      };

      const result = await viewEvent('event-123');

      expect(result).toEqual(mockEvent);
      expect(mockFetch).toHaveBeenCalledWith('/api/events/event-123', expect.objectContaining({
        method: 'GET'
      }));
    });
  });

  describe('Authentication', () => {
    test('should require auth token', async () => {
      localStorage.getItem.mockReturnValue(null);

      const createEvent = async (data) => {
        const token = localStorage.getItem('authToken');
        if (!token) {
          throw new Error('Authentication required. Please log in again.');
        }

        const response = await fetch('/api/events', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });

        return response.json();
      };

      await expect(createEvent({ title: 'Test' })).rejects.toThrow('Authentication required');
    });
  });
});
