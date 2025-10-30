/**
 * Tests for export functionality (analytics, conversations, etc.)
 */

describe('Export Functionality', () => {
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

  describe('Analytics Export', () => {
    test('should export analytics as CSV', async () => {
      const csvData = 'Agent,Conversations,Avg Rating\nEvent Planner,100,4.5\nBudget Advisor,50,4.8';

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: async () => csvData
      });

      const exportAnalyticsCSV = async (startDate, endDate, agentType) => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (agentType) params.append('agent_type', agentType);
        params.append('format', 'csv');

        const response = await fetch(`/api/agents/analytics/export?${params.toString()}`, {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Failed to export analytics');
        }

        return response.text();
      };

      const result = await exportAnalyticsCSV('2025-10-01', '2025-10-31', 'all');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/agents/analytics/export?'),
        expect.objectContaining({ method: 'GET' })
      );

      expect(result).toContain('Agent,Conversations');
      expect(result).toContain('Event Planner,100,4.5');
    });

    test('should export analytics as PDF', async () => {
      const mockPdfBlob = new Blob(['PDF content'], { type: 'application/pdf' });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        blob: async () => mockPdfBlob
      });

      const exportAnalyticsPDF = async (startDate, endDate, agentType) => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (agentType) params.append('agent_type', agentType);
        params.append('format', 'pdf');

        const response = await fetch(`/api/agents/analytics/export?${params.toString()}`, {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Failed to export analytics');
        }

        return response.blob();
      };

      const result = await exportAnalyticsPDF('2025-10-01', '2025-10-31', 'event-planner');

      expect(result.type).toBe('application/pdf');
    });
  });

  describe('Conversation Export', () => {
    test('should export conversation with full data', async () => {
      const mockConversation = {
        id: 'conv-123',
        agent_name: 'Event Planner',
        messages: [
          { role: 'user', content: 'Hello', timestamp: '2025-10-30T10:00:00Z' },
          { role: 'assistant', content: 'Hi there!', timestamp: '2025-10-30T10:00:05Z' }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockConversation
      });

      const exportConversation = async (conversationId) => {
        const token = localStorage.getItem('authToken');
        const orgId = localStorage.getItem('organizationId');

        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        if (orgId) {
          headers['X-Organization-ID'] = orgId;
        }

        const response = await fetch(`/api/agents/conversations/${conversationId}/export?format=json`, {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          throw new Error('Failed to export conversation');
        }

        return response.json();
      };

      const result = await exportConversation('conv-123');

      expect(result.id).toBe('conv-123');
      expect(result.messages).toHaveLength(2);
      expect(result.messages[0].role).toBe('user');
    });

    test('should format conversation for text export', () => {
      const conversationData = {
        id: 'conv-123',
        agent_name: 'Event Planner',
        messages: [
          { role: 'user', content: 'Hello', timestamp: '2025-10-30T10:00:00Z' },
          { role: 'assistant', content: 'Hi there!', timestamp: '2025-10-30T10:00:05Z' }
        ]
      };

      const formatConversation = (data) => {
        let content = `Conversation Export\n`;
        content += `Date: ${new Date().toLocaleString()}\n`;
        content += `Conversation ID: ${data.id}\n`;
        content += `Agent: ${data.agent_name || 'AI Assistant'}\n`;
        content += `\n${'='.repeat(80)}\n\n`;

        if (data.messages && data.messages.length > 0) {
          data.messages.forEach(message => {
            const role = message.role === 'user' ? 'User' : message.role === 'assistant' ? 'Agent' : 'System';
            const timestamp = message.timestamp ? new Date(message.timestamp).toLocaleString() : '';
            content += `[${timestamp}] ${role}:\n${message.content}\n\n`;
          });
        }

        return content;
      };

      const formatted = formatConversation(conversationData);

      expect(formatted).toContain('Conversation Export');
      expect(formatted).toContain('Conversation ID: conv-123');
      expect(formatted).toContain('Agent: Event Planner');
      expect(formatted).toContain('[10/30/2025');
      expect(formatted).toContain('User:\nHello');
      expect(formatted).toContain('Agent:\nHi there!');
    });
  });

  describe('CSV Team Export', () => {
    test('should export team members to CSV', () => {
      const teamMembers = [
        { name: 'John Doe', email: 'john@test.com', role: 'Admin', status: 'Active' },
        { name: 'Jane Smith', email: 'jane@test.com', role: 'Member', status: 'Active' }
      ];

      const exportTeamList = (members) => {
        let csvContent = 'Name,Email,Role,Status\n';

        members.forEach(member => {
          const escapeCsv = (str) => {
            if (str.includes(',') || str.includes('"') || str.includes('\n')) {
              return `"${str.replace(/"/g, '""')}"`;
            }
            return str;
          };

          csvContent += `${escapeCsv(member.name)},${escapeCsv(member.email)},${escapeCsv(member.role)},${escapeCsv(member.status)}\n`;
        });

        return csvContent;
      };

      const csv = exportTeamList(teamMembers);

      expect(csv).toContain('Name,Email,Role,Status');
      expect(csv).toContain('John Doe,john@test.com,Admin,Active');
      expect(csv).toContain('Jane Smith,jane@test.com,Member,Active');
    });

    test('should escape CSV special characters', () => {
      const escapeCsv = (str) => {
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      };

      expect(escapeCsv('Normal Text')).toBe('Normal Text');
      expect(escapeCsv('Text, with comma')).toBe('"Text, with comma"');
      expect(escapeCsv('Text "with quotes"')).toBe('"Text ""with quotes"""');
      expect(escapeCsv('Text\nwith newline')).toBe('"Text\nwith newline"');
    });
  });

  describe('Blob Handling', () => {
    test('should create blob with correct MIME type', () => {
      const csvData = 'Name,Email\nJohn,john@test.com';
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });

      expect(blob.type).toBe('text/csv;charset=utf-8;');
      expect(blob.size).toBeGreaterThan(0);
    });

    test('should create download link correctly', () => {
      const createDownload = (content, filename, type) => {
        const blob = new Blob([content], { type: type });
        const url = URL.createObjectURL(blob);

        // Verify URL was created
        expect(url).toBe('mock-url');
        expect(global.URL.createObjectURL).toHaveBeenCalledWith(blob);

        return { url, blob };
      };

      const { url } = createDownload('test content', 'test.csv', 'text/csv');
      expect(url).toBeTruthy();
    });
  });

  describe('Filename Generation', () => {
    test('should generate descriptive filenames', () => {
      const generateFilename = (type, params = {}) => {
        const timestamp = new Date().toISOString().slice(0, 10);

        if (type === 'analytics') {
          const { agentType = 'all', startDate = 'all', endDate = 'all' } = params;
          return `agent-analytics-${agentType}-${startDate}-to-${endDate}.csv`;
        }

        if (type === 'conversation') {
          const { conversationId } = params;
          return `conversation-${conversationId}-${timestamp}.txt`;
        }

        if (type === 'team') {
          return `team_members_${timestamp}.csv`;
        }

        return `export_${timestamp}.txt`;
      };

      expect(generateFilename('analytics', { agentType: 'event-planner', startDate: '2025-10-01', endDate: '2025-10-31' }))
        .toBe('agent-analytics-event-planner-2025-10-01-to-2025-10-31.csv');

      expect(generateFilename('conversation', { conversationId: 'conv-123' }))
        .toMatch(/^conversation-conv-123-\d{4}-\d{2}-\d{2}\.txt$/);

      expect(generateFilename('team'))
        .toMatch(/^team_members_\d{4}-\d{2}-\d{2}\.csv$/);
    });
  });
});
