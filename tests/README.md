# Frontend Tests

This directory contains Jest tests for the AI Event Planner frontend JavaScript functionality.

## Setup

Install dependencies:

```bash
npm install
```

## Running Tests

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run tests with coverage report
```bash
npm run test:coverage
```

## Test Structure

The tests are organized by functionality:

- **`events.test.js`** - Event management (create, edit, delete, view)
- **`team.test.js`** - Team management (invitations, member CRUD, CSV import/export)
- **`notifications.test.js`** - Notification system (load, mark as read, formatting)
- **`search.test.js`** - Global and conversation search
- **`exports.test.js`** - Export functionality (analytics CSV/PDF, conversation export)

## Test Coverage

The tests cover:

### API Integration Tests
- ✅ Event CRUD operations
- ✅ Team member management
- ✅ Bulk invitations
- ✅ CSV import/export
- ✅ Notifications
- ✅ Search (global and conversation)
- ✅ Analytics export (CSV/PDF)
- ✅ Conversation export

### Data Handling Tests
- ✅ CSV parsing and validation
- ✅ File blob creation
- ✅ Filename generation
- ✅ Date formatting
- ✅ URL encoding

### Error Handling Tests
- ✅ API error responses
- ✅ Authentication validation
- ✅ Input validation
- ✅ Network failures

## Mock Setup

The test environment includes mocks for:
- `localStorage` - For auth token and organization ID
- `fetch` - For API calls
- `bootstrap` - For UI components (modals, alerts, etc.)
- `URL.createObjectURL` - For file downloads
- `console` methods - To reduce test output noise

## Writing New Tests

To add new tests:

1. Create a new file in `/tests/` following the naming convention: `feature.test.js`
2. Import required mocks from `setup.js`
3. Follow the existing test structure:

```javascript
describe('Feature Name', () => {
  beforeEach(() => {
    // Setup
  });

  describe('Subfeature', () => {
    test('should do something', async () => {
      // Arrange
      mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });

      // Act
      const result = await yourFunction();

      // Assert
      expect(result).toBeDefined();
      expect(mockFetch).toHaveBeenCalledWith(/* ... */);
    });
  });
});
```

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Frontend Tests
  run: npm test

- name: Upload Coverage
  run: npm run test:coverage
```

## Coverage Goals

Current coverage targets:
- **Statements**: > 80%
- **Branches**: > 75%
- **Functions**: > 80%
- **Lines**: > 80%

## Troubleshooting

### Tests fail with "ReferenceError: fetch is not defined"
This should be handled by `setup.js`. Ensure the setup file is being loaded correctly.

### localStorage errors
Make sure you're not directly accessing `window.localStorage` in your code. Use `localStorage.getItem()` instead.

### Bootstrap errors
The bootstrap library is mocked in `setup.js`. If you need specific modal behavior, update the mock there.

## Contributing

When adding new features to the frontend:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before committing
3. Maintain or improve code coverage
4. Update this README if adding new test files
