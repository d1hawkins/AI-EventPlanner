#!/usr/bin/env node

/**
 * Test Generation Script
 *
 * This script helps generate boilerplate test files for React components and utilities.
 * Usage: node scripts/generate-tests.js <file-path>
 *
 * Example: node scripts/generate-tests.js src/components/LoadingSpinner.jsx
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (args.length === 0) {
  console.log(`
Usage: node scripts/generate-tests.js <file-path>

Examples:
  node scripts/generate-tests.js src/components/LoadingSpinner.jsx
  node scripts/generate-tests.js src/hooks/useEvents.js
  node scripts/generate-tests.js src/services/teamsService.js

This will create a corresponding .test.js(x) file with boilerplate test code.
  `);
  process.exit(1);
}

const filePath = args[0];
const fullPath = path.join(process.cwd(), filePath);

if (!fs.existsSync(fullPath)) {
  console.error(`Error: File not found: ${filePath}`);
  process.exit(1);
}

const fileName = path.basename(filePath);
const fileExt = path.extname(fileName);
const baseName = fileName.replace(fileExt, '');
const dirName = path.dirname(fullPath);

// Determine test file extension (.test.js or .test.jsx)
const testExt = fileExt === '.jsx' ? '.test.jsx' : '.test.js';
const testFileName = `${baseName}${testExt}`;
const testFilePath = path.join(dirName, testFileName);

if (fs.existsSync(testFilePath)) {
  console.error(`Error: Test file already exists: ${testFilePath}`);
  process.exit(1);
}

// Detect file type
const isComponent = fileExt === '.jsx' || filePath.includes('/components/');
const isHook = baseName.startsWith('use') && filePath.includes('/hooks/');
const isService = filePath.includes('/services/');
const isContext = filePath.includes('/context/');

// Generate appropriate template
let testContent = '';

if (isComponent) {
  testContent = generateComponentTest(baseName, fileName);
} else if (isHook) {
  testContent = generateHookTest(baseName, fileName);
} else if (isService) {
  testContent = generateServiceTest(baseName, fileName);
} else if (isContext) {
  testContent = generateContextTest(baseName, fileName);
} else {
  testContent = generateGenericTest(baseName, fileName);
}

// Write test file
fs.writeFileSync(testFilePath, testContent);

console.log(`✅ Test file created: ${testFilePath}`);
console.log(`\nNext steps:`);
console.log(`1. Open the test file and implement test cases`);
console.log(`2. Run tests: npm test -- ${testFileName}`);
console.log(`3. Check coverage: npm run test:coverage`);

// Template generators

function generateComponentTest(baseName, fileName) {
  return `import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ${baseName} } from './${fileName}';

describe('${baseName} Component', () => {
  describe('Rendering', () => {
    it('should render correctly', () => {
      render(<${baseName} />);
      // TODO: Add assertions
      expect(screen.getByRole('...').toBeInTheDocument();
    });

    it('should render with props', () => {
      render(<${baseName} prop="value" />);
      // TODO: Add assertions
    });
  });

  describe('Interactions', () => {
    it('should handle user interaction', () => {
      const handleClick = vi.fn();
      render(<${baseName} onClick={handleClick} />);

      fireEvent.click(screen.getByRole('button'));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty state', () => {
      render(<${baseName} />);
      // TODO: Add assertions
    });

    it('should handle error state', () => {
      render(<${baseName} error="Error message" />);
      // TODO: Add assertions
    });
  });
});
`;
}

function generateHookTest(baseName, fileName) {
  return `import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { ${baseName} } from './${fileName}';

describe('${baseName} Hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      const { result } = renderHook(() => ${baseName}());

      // TODO: Add assertions
      expect(result.current).toBeDefined();
    });
  });

  describe('State Updates', () => {
    it('should update state correctly', async () => {
      const { result } = renderHook(() => ${baseName}());

      act(() => {
        // TODO: Call hook method
        result.current.update();
      });

      // TODO: Add assertions
      expect(result.current.value).toBe('expected');
    });
  });

  describe('Async Operations', () => {
    it('should handle async operations', async () => {
      const { result } = renderHook(() => ${baseName}());

      act(() => {
        result.current.fetchData();
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      // TODO: Add assertions
    });
  });

  describe('Error Handling', () => {
    it('should handle errors gracefully', async () => {
      const { result } = renderHook(() => ${baseName}());

      // TODO: Trigger error condition
      // TODO: Add assertions
    });
  });
});
`;
}

function generateServiceTest(baseName, fileName) {
  return `import { describe, it, expect, beforeEach, vi } from 'vitest';
import ${baseName} from './${fileName}';
import apiClient from '../api/client';

vi.mock('../api/client');

describe('${baseName}', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Method 1', () => {
    it('should call API with correct parameters', async () => {
      const mockData = { id: 1, name: 'Test' };
      apiClient.get.mockResolvedValue({ data: mockData });

      const result = await ${baseName}.method1();

      expect(apiClient.get).toHaveBeenCalledWith('/endpoint');
      expect(result).toEqual(mockData);
    });

    it('should handle errors', async () => {
      const error = new Error('API Error');
      apiClient.get.mockRejectedValue(error);

      await expect(${baseName}.method1()).rejects.toThrow('API Error');
    });
  });

  // TODO: Add tests for all service methods
});
`;
}

function generateContextTest(baseName, fileName) {
  return `import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ${baseName}Provider, use${baseName} } from './${fileName}';

const TestComponent = () => {
  const context = use${baseName}();

  return (
    <div>
      <span data-testid="value">{context.value}</span>
      <button onClick={context.update} data-testid="update-button">
        Update
      </button>
    </div>
  );
};

describe('${baseName} Context', () => {
  beforeEach(() => {
    // TODO: Reset any global state
  });

  describe('Provider', () => {
    it('should provide context values', () => {
      render(
        <${baseName}Provider>
          <TestComponent />
        </${baseName}Provider>
      );

      expect(screen.getByTestId('value')).toHaveTextContent('expected');
    });

    it('should update context values', () => {
      render(
        <${baseName}Provider>
          <TestComponent />
        </${baseName}Provider>
      );

      fireEvent.click(screen.getByTestId('update-button'));

      expect(screen.getByTestId('value')).toHaveTextContent('updated');
    });
  });

  describe('Hook', () => {
    it('should throw error when used outside provider', () => {
      const consoleError = console.error;
      console.error = () => {};

      expect(() => {
        render(<TestComponent />);
      }).toThrow();

      console.error = consoleError;
    });
  });
});
`;
}

function generateGenericTest(baseName, fileName) {
  return `import { describe, it, expect } from 'vitest';
import { ${baseName} } from './${fileName}';

describe('${baseName}', () => {
  describe('Functionality', () => {
    it('should work correctly', () => {
      // TODO: Add test implementation
      expect(${baseName}).toBeDefined();
    });
  });

  describe('Edge Cases', () => {
    it('should handle edge cases', () => {
      // TODO: Add test implementation
    });
  });
});
`;
}
