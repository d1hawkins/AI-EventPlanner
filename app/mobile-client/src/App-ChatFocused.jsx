import { BrowserRouter } from 'react-router-dom';
import { ChatScreen } from './pages/ChatScreen';

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
 */

function App() {
  return (
    <BrowserRouter>
      <ChatScreen />
    </BrowserRouter>
  );
}

export default App;
