/**
 * Tests for search functionality
 */

describe('Search Functionality', () => {
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

  describe('Global Search', () => {
    test('should search across all content types', async () => {
      const mockResults = {
        events: [
          { id: 'event-1', title: 'Tech Conference', description: 'A tech event' }
        ],
        templates: [
          { id: 'template-1', name: 'Conference Template', description: 'Template for conferences' }
        ],
        team_members: [
          { id: 'member-1', name: 'John Doe', email: 'john@test.com', role: 'admin' }
        ],
        conversations: [
          { id: 'conv-1', created_at: '2025-10-30T10:00:00Z' }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults
      });

      const performSearch = async (query) => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Search failed');
        }

        return response.json();
      };

      const results = await performSearch('conference');

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/search?q=conference',
        expect.objectContaining({ method: 'GET' })
      );

      expect(results.events).toHaveLength(1);
      expect(results.templates).toHaveLength(1);
      expect(results.team_members).toHaveLength(1);
      expect(results.conversations).toHaveLength(1);
    });

    test('should handle empty search query', async () => {
      const performSearch = async (query) => {
        if (!query || query.trim() === '') {
          throw new Error('Please enter a search term');
        }

        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });

        return response.json();
      };

      await expect(performSearch('')).rejects.toThrow('Please enter a search term');
      await expect(performSearch('   ')).rejects.toThrow('Please enter a search term');
    });

    test('should handle no results', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          events: [],
          templates: [],
          team_members: [],
          conversations: []
        })
      });

      const performSearch = async (query) => {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
          method: 'GET',
          headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
        });

        return response.json();
      };

      const results = await performSearch('nonexistent');

      const totalResults = (results.events?.length || 0) +
                          (results.templates?.length || 0) +
                          (results.team_members?.length || 0) +
                          (results.conversations?.length || 0);

      expect(totalResults).toBe(0);
    });
  });

  describe('Conversation Search', () => {
    test('should search conversations via API', async () => {
      const mockResults = {
        conversations: [
          { id: 'conv-1', title: 'Planning discussion' },
          { id: 'conv-2', title: 'Budget planning' }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults
      });

      const searchConversations = async (query) => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const response = await fetch(`/api/agents/conversations/search?q=${encodeURIComponent(query)}`, {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Search failed');
        }

        return response.json();
      };

      const results = await searchConversations('planning');

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/agents/conversations/search?q=planning',
        expect.objectContaining({ method: 'GET' })
      );

      expect(results.conversations).toHaveLength(2);
    });

    test('should use client-side search for short queries', () => {
      const conversations = [
        { id: '1', title: 'Plan A', preview: 'First plan' },
        { id: '2', title: 'Plan B', preview: 'Second plan' },
        { id: '3', title: 'Execute', preview: 'Third item' }
      ];

      const clientSideSearch = (query, items) => {
        if (query.length < 3) {
          const lowerQuery = query.toLowerCase();
          return items.filter(item => {
            const title = item.title?.toLowerCase() || '';
            const preview = item.preview?.toLowerCase() || '';
            return title.includes(lowerQuery) || preview.includes(lowerQuery);
          });
        }
        return items; // Would call API for longer queries
      };

      const results = clientSideSearch('pl', conversations);
      expect(results).toHaveLength(2);
      expect(results[0].id).toBe('1');
      expect(results[1].id).toBe('2');
    });
  });

  describe('URL Encoding', () => {
    test('should properly encode special characters', () => {
      const queries = [
        'hello world',
        'user@email.com',
        'test & test',
        'price: $100'
      ];

      queries.forEach(query => {
        const encoded = encodeURIComponent(query);
        expect(encoded).not.toContain(' ');
        expect(encoded).not.toContain('@');
        expect(encoded).not.toContain('&');
      });
    });
  });
});
