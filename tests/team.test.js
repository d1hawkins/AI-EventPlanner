/**
 * Tests for team management functionality
 */

describe('Team Management', () => {
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

  describe('sendInvitations', () => {
    test('should send team invitations successfully', async () => {
      const emails = ['user1@example.com', 'user2@example.com'];

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ message: 'Invitation sent' })
      });

      const sendInvitations = async (emailList, role = 'member', message = '') => {
        const orgId = localStorage.getItem('organizationId');
        const token = localStorage.getItem('authToken');

        const invitationPromises = emailList.map(email =>
          fetch(`/api/subscription/organizations/${orgId}/members/invite`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
              'X-Organization-ID': orgId
            },
            body: JSON.stringify({ email, role, message })
          })
        );

        const responses = await Promise.all(invitationPromises);
        return responses;
      };

      const results = await sendInvitations(emails, 'member', 'Join our team');

      expect(mockFetch).toHaveBeenCalledTimes(2);
      expect(results).toHaveLength(2);
      expect(results.every(r => r.ok)).toBe(true);
    });

    test('should handle partial failures', async () => {
      const emails = ['valid@example.com', 'invalid@example.com'];

      mockFetch
        .mockResolvedValueOnce({ ok: true, json: async () => ({ message: 'Sent' }) })
        .mockResolvedValueOnce({ ok: false, status: 400, json: async () => ({ detail: 'Invalid email' }) });

      const sendInvitations = async (emailList, role = 'member') => {
        const orgId = localStorage.getItem('organizationId');
        const token = localStorage.getItem('authToken');

        const invitationPromises = emailList.map(email =>
          fetch(`/api/subscription/organizations/${orgId}/members/invite`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
              'X-Organization-ID': orgId
            },
            body: JSON.stringify({ email, role })
          })
        );

        const responses = await Promise.all(invitationPromises);

        const failures = [];
        for (let i = 0; i < responses.length; i++) {
          if (!responses[i].ok) {
            failures.push(emailList[i]);
          }
        }

        return { responses, failures };
      };

      const { failures } = await sendInvitations(emails);
      expect(failures).toEqual(['invalid@example.com']);
    });
  });

  describe('editMember', () => {
    test('should update member details', async () => {
      const memberId = 'member-123';
      const updateData = {
        name: 'Updated Name',
        email: 'updated@example.com',
        role: 'admin'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...updateData, id: memberId })
      });

      const saveMemberChanges = async (id, data) => {
        const orgId = localStorage.getItem('organizationId');
        const token = localStorage.getItem('authToken');

        const response = await fetch(`/api/subscription/organizations/${orgId}/members/${id}`, {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            'X-Organization-ID': orgId
          },
          body: JSON.stringify(data)
        });

        if (!response.ok) {
          throw new Error('Failed to update member');
        }

        return response.json();
      };

      const result = await saveMemberChanges(memberId, updateData);

      expect(mockFetch).toHaveBeenCalledWith(
        `/api/subscription/organizations/org-123/members/${memberId}`,
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(updateData)
        })
      );

      expect(result.id).toBe(memberId);
    });

    test('should validate required fields', async () => {
      const saveMemberChanges = async (id, data) => {
        if (!data.name || !data.email || !data.role) {
          throw new Error('All fields are required');
        }

        const response = await fetch(`/api/subscription/organizations/org-123/members/${id}`, {
          method: 'PATCH',
          headers: { 'Authorization': 'Bearer mock-token', 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });

        return response.json();
      };

      await expect(saveMemberChanges('member-123', { name: '' })).rejects.toThrow('All fields are required');
    });
  });

  describe('removeMember', () => {
    test('should delete team member', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Member removed' })
      });

      const removeMember = async (memberId) => {
        const orgId = localStorage.getItem('organizationId');
        const token = localStorage.getItem('authToken');

        const response = await fetch(`/api/subscription/organizations/${orgId}/members/${memberId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'X-Organization-ID': orgId
          }
        });

        if (!response.ok) {
          throw new Error('Failed to remove member');
        }

        return response.json();
      };

      await removeMember('member-123');

      expect(mockFetch).toHaveBeenCalledWith(
        '/api/subscription/organizations/org-123/members/member-123',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  describe('CSV Import', () => {
    test('should parse CSV and send bulk invitations', async () => {
      const csvContent = 'email,name,role\nuser1@test.com,User One,member\nuser2@test.com,User Two,admin';

      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ message: 'Invitation sent' })
      });

      const importTeamMembers = async (csvText) => {
        const lines = csvText.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        if (lines.length < 2) {
          throw new Error('CSV file must contain headers and at least one data row');
        }

        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const emailIndex = headers.indexOf('email');
        const roleIndex = headers.indexOf('role');

        if (emailIndex === -1) {
          throw new Error('CSV file must contain an "email" column');
        }

        const members = [];
        for (let i = 1; i < lines.length; i++) {
          const values = lines[i].split(',').map(v => v.trim());
          const email = values[emailIndex] || '';
          const role = roleIndex !== -1 ? values[roleIndex] : 'member';

          if (email) {
            members.push({ email, role });
          }
        }

        const orgId = localStorage.getItem('organizationId');
        const token = localStorage.getItem('authToken');

        const invitationPromises = members.map(member =>
          fetch(`/api/subscription/organizations/${orgId}/members/invite`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
              'X-Organization-ID': orgId
            },
            body: JSON.stringify(member)
          })
        );

        return Promise.all(invitationPromises);
      };

      const results = await importTeamMembers(csvContent);

      expect(results).toHaveLength(2);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    test('should reject invalid CSV', async () => {
      const importTeamMembers = async (csvText) => {
        const lines = csvText.split('\n').map(line => line.trim()).filter(line => line.length > 0);

        if (lines.length < 2) {
          throw new Error('CSV file must contain headers and at least one data row');
        }

        const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
        const emailIndex = headers.indexOf('email');

        if (emailIndex === -1) {
          throw new Error('CSV file must contain an "email" column');
        }

        return [];
      };

      await expect(importTeamMembers('name,role\nJohn,admin')).rejects.toThrow('CSV file must contain an "email" column');
      await expect(importTeamMembers('email\n')).rejects.toThrow('CSV file must contain headers and at least one data row');
    });
  });
});
