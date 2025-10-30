/**
 * Tests for notifications functionality
 */

describe('Notifications', () => {
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

  describe('loadNotifications', () => {
    test('should fetch notifications from API', async () => {
      const mockNotifications = {
        notifications: [
          {
            id: 'notif-1',
            type: 'event',
            message: 'New event created',
            is_read: false,
            created_at: '2025-10-30T10:00:00Z'
          },
          {
            id: 'notif-2',
            type: 'team',
            message: 'New team member added',
            is_read: true,
            created_at: '2025-10-29T15:30:00Z'
          }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

      const loadNotifications = async () => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const response = await fetch('/api/notifications', {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Failed to load notifications');
        }

        const data = await response.json();
        return data.notifications || [];
      };

      const notifications = await loadNotifications();

      expect(notifications).toHaveLength(2);
      expect(notifications[0].type).toBe('event');
      expect(mockFetch).toHaveBeenCalledWith('/api/notifications', {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json',
          'X-Organization-ID': 'org-123'
        }
      });
    });

    test('should handle empty notifications', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ notifications: [] })
      });

      const loadNotifications = async () => {
        const response = await fetch('/api/notifications', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
            'Content-Type': 'application/json'
          }
        });

        const data = await response.json();
        return data.notifications || [];
      };

      const notifications = await loadNotifications();
      expect(notifications).toHaveLength(0);
    });
  });

  describe('updateNotificationBadge', () => {
    test('should calculate unread count correctly', () => {
      const notifications = [
        { id: '1', is_read: false },
        { id: '2', is_read: true },
        { id: '3', is_read: false },
        { id: '4', is_read: false }
      ];

      const getUnreadCount = (notifs) => {
        return notifs.filter(n => !n.is_read).length;
      };

      const unreadCount = getUnreadCount(notifications);
      expect(unreadCount).toBe(3);
    });

    test('should format badge text correctly', () => {
      const formatBadge = (count) => {
        if (count === 0) return null;
        return count > 9 ? '9+' : count.toString();
      };

      expect(formatBadge(0)).toBe(null);
      expect(formatBadge(5)).toBe('5');
      expect(formatBadge(10)).toBe('9+');
      expect(formatBadge(99)).toBe('9+');
    });
  });

  describe('markNotificationsAsRead', () => {
    test('should mark all notifications as read', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Notifications marked as read' })
      });

      const markNotificationsAsRead = async () => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const response = await fetch('/api/notifications/mark-read', {
          method: 'POST',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Failed to mark notifications as read');
        }

        return response.json();
      };

      await markNotificationsAsRead();

      expect(mockFetch).toHaveBeenCalledWith('/api/notifications/mark-read', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer mock-token',
          'Content-Type': 'application/json',
          'X-Organization-ID': 'org-123'
        }
      });
    });
  });

  describe('formatNotificationDate', () => {
    test('should format relative dates correctly', () => {
      const now = new Date();

      const formatNotificationDate = (dateString) => {
        if (!dateString) return '';

        const date = new Date(dateString);
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      };

      const justNow = new Date(now.getTime() - 30000); // 30 seconds ago
      expect(formatNotificationDate(justNow.toISOString())).toBe('Just now');

      const fiveMinsAgo = new Date(now.getTime() - 300000); // 5 minutes ago
      expect(formatNotificationDate(fiveMinsAgo.toISOString())).toBe('5 minutes ago');

      const twoHoursAgo = new Date(now.getTime() - 7200000); // 2 hours ago
      expect(formatNotificationDate(twoHoursAgo.toISOString())).toBe('2 hours ago');

      const threeDaysAgo = new Date(now.getTime() - 259200000); // 3 days ago
      expect(formatNotificationDate(threeDaysAgo.toISOString())).toBe('3 days ago');
    });
  });

  describe('Notification Types', () => {
    test('should assign correct icons and colors', () => {
      const getNotificationStyle = (type) => {
        const styles = {
          'event': { icon: 'bi-calendar', color: 'bg-primary' },
          'team': { icon: 'bi-people', color: 'bg-success' },
          'billing': { icon: 'bi-credit-card', color: 'bg-warning' },
          'system': { icon: 'bi-exclamation-triangle', color: 'bg-danger' }
        };

        return styles[type] || { icon: 'bi-info-circle', color: 'bg-primary' };
      };

      expect(getNotificationStyle('event')).toEqual({ icon: 'bi-calendar', color: 'bg-primary' });
      expect(getNotificationStyle('team')).toEqual({ icon: 'bi-people', color: 'bg-success' });
      expect(getNotificationStyle('billing')).toEqual({ icon: 'bi-credit-card', color: 'bg-warning' });
      expect(getNotificationStyle('unknown')).toEqual({ icon: 'bi-info-circle', color: 'bg-primary' });
    });
  });
});
