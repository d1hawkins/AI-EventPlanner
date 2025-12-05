import { BrowserRouter } from 'react-router-dom';
import { ChatScreen } from './pages/ChatScreen';
import { ThemeProvider } from './context/ThemeContext';

/**
 * Chat-Focused App - Inspired by Gemini Canvas
 *
 * This is a simplified, chat-first interface where everything
 * happens through conversation with the AI assistant.
 *
 * Key Features:
 * - Single-screen chat interface
 * - No bottom navigation
 * - Inline event cards within chat
 * - Contextual action chips
 * - Minimal UI chrome
 * - Everything driven by conversation
 * - Dark/Light mode support
 */

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <ChatScreen />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
