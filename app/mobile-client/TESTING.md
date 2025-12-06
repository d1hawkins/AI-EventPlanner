# Testing Guide

## 🧪 Testing Infrastructure

The mobile client uses **Vitest** with **React Testing Library** for comprehensive unit and integration testing.

### Tech Stack
- **Test Runner**: Vitest (Vite-native, fast)
- **Testing Library**: @testing-library/react
- **DOM Environment**: jsdom
- **Coverage**: Vitest coverage (v8 provider)
- **Assertions**: Vitest + @testing-library/jest-dom

---

## 🚀 Running Tests

### Run All Tests
```bash
npm test
```

### Run Tests in Watch Mode
```bash
npm run test:watch
```

### Run Tests Once (CI mode)
```bash
npm run test:run
```

### Run with UI
```bash
npm run test:ui
```
Opens a browser UI at `http://localhost:51204/__vitest__/`

### Generate Coverage Report
```bash
npm run test:coverage
```

Coverage report will be generated in `coverage/` directory.

---

## 📊 Coverage Goals

**Target**: 100% code coverage

Coverage thresholds configured in `vitest.config.js`:
- **Lines**: 100%
- **Functions**: 100%
- **Branches**: 100%
- **Statements**: 100%

### View Coverage Report

After running `npm run test:coverage`:

1. **Terminal**: See summary in console
2. **HTML Report**: Open `coverage/index.html` in browser
3. **LCOV**: `coverage/lcov.info` for CI integration

---

## 📁 Test File Structure

```
src/
├── test/
│   ├── setup.js           # Global test setup
│   ├── test-utils.jsx     # Custom render functions
│   └── mockData.js        # Mock data for tests
├── api/
│   ├── client.js
│   └── client.test.js     # API client tests
├── services/
│   ├── eventsService.js
│   └── eventsService.test.js
├── hooks/
│   ├── useEvents.js
│   └── useEvents.test.jsx
├── components/
│   ├── Button.jsx
│   └── Button.test.jsx
├── pages/
│   ├── Chat.jsx
│   └── Chat.test.jsx
└── context/
    ├── ThemeContext.jsx
    └── ThemeContext.test.jsx
```

**Naming Convention**: `*.test.js` or `*.test.jsx` next to the file being tested.

---

## ✍️ Writing Tests

### Test Template

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import YourComponent from './YourComponent';

describe('YourComponent', () => {
  beforeEach(() => {
    // Setup before each test
    vi.clearAllMocks();
  });

  describe('Feature Group', () => {
    it('should do something', () => {
      render(<YourComponent />);

      // Assertions
      expect(screen.getByText('Expected Text')).toBeInTheDocument();
    });
  });
});
```

### Testing Components with Providers

Use the custom `renderWithProviders` utility:

```javascript
import { renderWithProviders } from '../test/test-utils';

it('should render with all providers', () => {
  renderWithProviders(<YourComponent />);

  expect(screen.getByText('Content')).toBeInTheDocument();
});
```

This automatically wraps your component with:
- `BrowserRouter`
- `ThemeProvider`
- `ToastProvider`

### Testing Hooks

```javascript
import { renderHook, act } from '@testing-library/react';
import { useYourHook } from './useYourHook';

it('should update state', () => {
  const { result } = renderHook(() => useYourHook());

  act(() => {
    result.current.updateState('new value');
  });

  expect(result.current.state).toBe('new value');
});
```

### Testing API Calls

```javascript
import { vi } from 'vitest';
import apiClient from '../api/client';

vi.mock('../api/client');

it('should fetch data from API', async () => {
  const mockData = { id: 1, name: 'Test' };
  apiClient.get.mockResolvedValue({ data: mockData });

  const result = await yourService.getData();

  expect(apiClient.get).toHaveBeenCalledWith('/endpoint');
  expect(result).toEqual(mockData);
});
```

### Testing User Interactions

```javascript
import userEvent from '@testing-library/user-event';

it('should handle user input', async () => {
  const user = userEvent.setup();
  render(<YourComponent />);

  const input = screen.getByRole('textbox');
  await user.type(input, 'Hello');

  expect(input).toHaveValue('Hello');
});
```

### Testing Async Operations

```javascript
import { waitFor } from '@testing-library/react';

it('should load data asynchronously', async () => {
  render(<YourComponent />);

  // Wait for loading to complete
  await waitFor(() => {
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  expect(screen.getByText('Loaded Data')).toBeInTheDocument();
});
```

---

## 🎯 Testing Best Practices

### 1. Test User Behavior, Not Implementation

❌ **Bad**:
```javascript
expect(component.state.value).toBe('test');
```

✅ **Good**:
```javascript
expect(screen.getByText('test')).toBeInTheDocument();
```

### 2. Use Accessible Queries

Priority order:
1. `getByRole`
2. `getByLabelText`
3. `getByPlaceholderText`
4. `getByText`
5. `getByTestId` (last resort)

❌ **Bad**:
```javascript
const button = container.querySelector('.btn-primary');
```

✅ **Good**:
```javascript
const button = screen.getByRole('button', { name: /submit/i });
```

### 3. Test Edge Cases

```javascript
describe('Input Validation', () => {
  it('should handle empty input', () => { /* ... */ });
  it('should handle very long input', () => { /* ... */ });
  it('should handle special characters', () => { /* ... */ });
  it('should handle null/undefined', () => { /* ... */ });
});
```

### 4. Keep Tests Isolated

```javascript
beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  // Reset any global state
});
```

### 5. Use Descriptive Test Names

❌ **Bad**:
```javascript
it('works', () => { /* ... */ });
```

✅ **Good**:
```javascript
it('should display error message when login fails', () => { /* ... */ });
```

---

## 🔧 Custom Test Utilities

### renderWithProviders

Renders component with all app providers:

```javascript
import { renderWithProviders } from '../test/test-utils';

renderWithProviders(<Component />, {
  route: '/events', // optional: set initial route
});
```

### renderWithRouter

Renders component with just Router (no theme/toast):

```javascript
import { renderWithRouter } from '../test/test-utils';

renderWithRouter(<Component />, { route: '/dashboard' });
```

### Mock Data

Pre-defined mock data available in `src/test/mockData.js`:

```javascript
import {
  mockEvent,
  mockEvents,
  mockUser,
  mockTeamMember,
  mockSubscription,
  mockDashboardStats,
} from '../test/mockData';
```

---

## 📝 Test Coverage Checklist

### Services (4 modules)
- [x] eventsService.js - 100%
- [ ] teamsService.js
- [ ] subscriptionService.js
- [ ] dashboardService.js

### Hooks (16 hooks)
- [ ] useEvents.js
- [ ] useEvent.js
- [ ] useEventTasks.js
- [ ] useEventGuests.js
- [ ] useEventBudget.js
- [ ] useTeam.js
- [ ] useTeamActivity.js
- [ ] usePendingInvites.js
- [ ] useSubscription.js
- [ ] useUsageLimits.js
- [ ] useBillingHistory.js
- [ ] useAvailablePlans.js
- [ ] useUsageStats.js
- [ ] useDashboard.js
- [ ] useDashboardStats.js
- [ ] useRecentActivity.js
- [ ] useUpcomingEvents.js
- [x] useToast.jsx (via ThemeContext test)

### Common Components
- [x] Button.jsx - 100%
- [ ] LoadingSpinner.jsx
- [ ] ErrorMessage.jsx
- [ ] EmptyState.jsx
- [ ] SearchBar.jsx
- [ ] ConfirmDialog.jsx
- [ ] ChatBubble.jsx
- [ ] EventCard.jsx
- [ ] QuickReplyButton.jsx
- [ ] BottomNav.jsx

### Page Components
- [ ] Chat.jsx
- [ ] EventsPage.jsx
- [ ] DashboardPage.jsx
- [ ] TeamPage.jsx
- [ ] SubscriptionPage.jsx
- [ ] Home.jsx
- [ ] Profile.jsx

### Context Providers
- [x] ThemeContext.jsx - 100%
- [ ] ToastProvider (in useToast.jsx)

### Specialized Components
- [ ] EventListCard.jsx
- [ ] StatCard.jsx
- [ ] ActivityFeed.jsx
- [ ] TeamMemberCard.jsx
- [ ] RoleSelector.jsx
- [ ] InviteForm.jsx
- [ ] PlanCard.jsx
- [ ] UsageCard.jsx

---

## 🐛 Debugging Tests

### Run Single Test File
```bash
npm test -- Button.test.jsx
```

### Run Tests Matching Pattern
```bash
npm test -- -t "should render"
```

### Debug in VS Code

Add to `.vscode/launch.json`:
```json
{
  "type": "node",
  "request": "launch",
  "name": "Vitest",
  "runtimeExecutable": "npm",
  "runtimeArgs": ["run", "test"],
  "console": "integratedTerminal"
}
```

### View Test Output
```bash
npm test -- --reporter=verbose
```

---

## 🚨 Common Issues & Solutions

### Issue: "Cannot find module"

**Solution**: Check import paths and ensure file exists.

```bash
# Verify file structure
ls src/components/
```

### Issue: "ReferenceError: localStorage is not defined"

**Solution**: Already mocked in `src/test/setup.js`. Clear before each test:

```javascript
beforeEach(() => {
  localStorage.clear();
});
```

### Issue: "matchMedia is not a function"

**Solution**: Already mocked in `src/test/setup.js`.

### Issue: Tests timeout

**Solution**: Increase timeout:

```javascript
it('should do something', async () => {
  // test code
}, { timeout: 10000 }); // 10 seconds
```

### Issue: Async test warnings

**Solution**: Use `waitFor`:

```javascript
await waitFor(() => {
  expect(screen.getByText('Loaded')).toBeInTheDocument();
});
```

---

## 📚 Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Jest DOM Matchers](https://github.com/testing-library/jest-dom)
- [Common Mistakes](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

## ✅ Quick Start

1. **Install dependencies** (already done)
   ```bash
   npm install
   ```

2. **Run tests**
   ```bash
   npm test
   ```

3. **Generate coverage**
   ```bash
   npm run test:coverage
   ```

4. **View coverage report**
   ```bash
   open coverage/index.html
   ```

---

## 🎯 Goals

- **Coverage**: 100% for all production code
- **Speed**: < 1s for unit tests, < 5s for all tests
- **Reliability**: Zero flaky tests
- **Maintainability**: Clear, readable test code

**Current Status**: Testing infrastructure complete, actively writing tests to 100% coverage.

---

**Last Updated**: 2024-12-05
**Test Framework**: Vitest + React Testing Library
**Coverage Goal**: 100%
