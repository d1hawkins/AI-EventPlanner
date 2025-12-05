# 💬 AI Event Planner - Chat-Focused Interface

## Overview

A **Gemini Canvas-inspired** chat-first interface for AI Event Planner. Everything happens through natural conversation with your AI assistant.

---

## 🚀 Quick Start

### Switch to Chat-Focused Interface

**Option 1: Replace main App**
```bash
cd app/mobile-client/src
mv App.jsx App-Original.jsx
mv App-ChatFocused.jsx App.jsx
```

**Option 2: Use directly**
```javascript
// In main.jsx, change import
import App from './App-ChatFocused.jsx'
```

### Run the App
```bash
npm install
npm run dev
```

Visit: `http://localhost:3000`

---

## 🎯 Key Features

### ✨ Chat-First Design
- **Single screen** - Everything in conversation
- **No navigation** - Just talk to AI
- **Inline cards** - Events appear in chat
- **Quick actions** - Contextual chips

### 💬 Natural Interaction
```
You: "Plan a birthday party"
AI:  "Great! When is the birthday?"
You: "June 15th"
AI:  "Perfect! How many guests?"
```

### 📦 What's Included

**New Components** (6 files)
```
src/components/
├── ChatMessage.jsx       # AI/User message bubbles
├── ChatInput.jsx         # Floating input with send
├── ChatHeader.jsx        # Minimal top header
├── InlineEventCard.jsx   # Event cards in chat
├── ActionChip.jsx        # Quick reply buttons
└── SideMenu.jsx          # Hamburger menu
```

**New Pages** (1 file)
```
src/pages/
└── ChatScreen.jsx        # Main chat interface
```

**New App** (1 file)
```
src/
└── App-ChatFocused.jsx   # Chat-first app shell
```

---

## 🎨 Design Highlights

### Gemini Canvas Style
- **Clean & Minimal** - Pure white background
- **Conversation Flow** - Natural reading order
- **Contextual Actions** - Suggestions when needed
- **Floating Input** - Always accessible at bottom
- **No Navigation Bar** - More screen space

### Color Palette
```css
Background:    #FFFFFF (Pure white)
AI Bubble:     #E8F0FE (Light blue)
User Bubble:   #E3F2FD (Lighter blue)
Primary:       #1A73E8 (Google blue)
Text:          #202124 (Near black)
```

---

## 💡 Usage Examples

### Create an Event
```
You: "I want to plan a summer BBQ"
AI:  "Sounds fun! Let's plan it.
      When would you like to have it?"

You: "June 15th at 2pm"
AI:  "Perfect! How many guests?"

You: "About 50 people"
AI:  "✨ Created: Summer BBQ Party
      [Shows event card]
      What would you like to do next?"
```

### Check Event Status
```
You: "How's my BBQ party coming?"
AI:  "Your Summer BBQ is 60% complete!
      [Shows event card with progress]

      Done ✓
      • Venue booked
      • Catering ordered

      Still needed:
      • Send invitations
      • Arrange music

      Need help with anything?"
```

### Quick Actions
```
AI:  "What would you like to do?

      [New Event] [My Events]
      [Get Ideas] [Find Venues]"
```

---

## 🏗️ Component API

### ChatMessage
```jsx
<ChatMessage
  message="Hello! How can I help?"
  isAI={true}
  timestamp="2 minutes ago"
>
  {/* Optional: Inline cards or action chips */}
</ChatMessage>
```

### InlineEventCard
```jsx
<InlineEventCard
  event={{
    name: 'Summer BBQ',
    date: '2024-06-15',
    icon: '🎉',
    guests: 50,
    budget: 3000,
    progress: 60
  }}
  onAction={(action, event) => {
    // action: 'view' or 'chat'
  }}
/>
```

### ActionChip
```jsx
<ActionChip
  icon="📅"
  text="When is it?"
  onClick={() => handleAction()}
  variant="default" // or 'primary', 'success'
/>
```

### ChatInput
```jsx
<ChatInput
  onSend={(message) => handleSend(message)}
  placeholder="Type a message..."
/>
```

---

## 🎯 Interaction Patterns

### Conversation Flow
1. User sends message
2. Show user bubble (right-aligned)
3. Show typing indicator
4. Show AI response (left-aligned)
5. Show action chips if relevant
6. Wait for next user input

### Event Creation
1. User expresses intent: "Plan a party"
2. AI asks questions with chips
3. User responds (text or chip tap)
4. AI creates event, shows card
5. Continue conversation

### Event Management
1. User asks about event: "Show my BBQ"
2. AI displays inline event card
3. User can tap actions or ask questions
4. AI responds with updates
5. Event card updates inline

---

## 📱 Mobile Optimizations

### Touch-Friendly
- **44px minimum** tap targets
- **Large input area** - Easy typing
- **Smooth scrolling** - Momentum scroll
- **Auto-scroll** - New messages visible

### Keyboard Handling
- Input resizes with content
- Shift+Enter for new line
- Enter to send
- Auto-focus on open

### Performance
- Message virtualization (future)
- Image lazy loading
- Smooth 60fps animations
- Efficient re-renders

---

## 🔧 Customization

### Change Colors
```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      'ai-bubble': '#YOUR_COLOR',
      'user-bubble': '#YOUR_COLOR',
      'primary': '#YOUR_COLOR',
    }
  }
}
```

### Add Custom Actions
```javascript
// In ChatScreen.jsx
const customActions = [
  { icon: '🎯', text: 'My Action', action: 'custom' },
];

// Handle in handleActionClick
if (action === 'custom') {
  // Your logic
}
```

### Modify AI Responses
```javascript
// In ChatScreen.jsx, update handleSendMessage
if (lowerContent.includes('your-keyword')) {
  aiResponse = {
    type: 'ai',
    content: 'Your custom response',
    actions: [...],
  };
}
```

---

## 🔌 Backend Integration

### Connect to API
```javascript
// In ChatScreen.jsx
import { chatAPI } from '../api/chat';

const handleSendMessage = async (content) => {
  // Send to backend
  const response = await chatAPI.sendMessage(conversationId, content);

  // Display AI response
  setMessages([...messages, {
    type: 'ai',
    content: response.message,
    timestamp: new Date(),
  }]);
};
```

### WebSocket for Real-Time
```javascript
import { useEffect } from 'react';

useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/chat');

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Add to messages
  };

  return () => ws.close();
}, []);
```

---

## ♿ Accessibility

### Screen Reader Support
- Messages announced as they arrive
- Action chips properly labeled
- Input field clearly identified
- Navigation through conversation

### Keyboard Navigation
- Tab through action chips
- Enter to send message
- Escape to close menu
- Arrow keys in chips

### Visual Accessibility
- High contrast text
- Clear focus indicators
- Scalable text sizes
- Color-blind safe palette

---

## 🧪 Testing

### Manual Testing Checklist
- [ ] Send text message
- [ ] Tap action chips
- [ ] View inline event cards
- [ ] Open side menu
- [ ] Voice input (if enabled)
- [ ] Long messages scroll properly
- [ ] Typing indicator shows
- [ ] Auto-scroll to latest
- [ ] Input resizes correctly
- [ ] Works on small screens

### Test Conversations
```
# Test 1: Event Creation
"Plan a party" → Follow prompts

# Test 2: Event Viewing
"Show my events" → See cards

# Test 3: Help
"Help" → See options

# Test 4: Natural Language
"Change my party to next week" → Update confirmed
```

---

## 📊 Comparison: Original vs Chat-Focused

| Aspect | Original | Chat-Focused |
|--------|----------|-------------|
| Screens | 7+ pages | 1 chat screen |
| Navigation | Bottom nav | Hamburger menu |
| Event View | Separate page | Inline card |
| Create Event | Form screen | Conversation |
| Complexity | Medium | Low |
| Learning Curve | Traditional app | Just chat |

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Netlify
```bash
netlify deploy --prod --dir=dist
```

### Deploy to Vercel
```bash
vercel --prod
```

### Environment Variables
```env
VITE_API_URL=https://your-api.com
VITE_WS_URL=wss://your-api.com
```

---

## 📚 Documentation

- **Design Doc**: `/docs/mobile-ui-chat-focused.md`
- **Comparison**: `/docs/chat-focused-comparison.md`
- **Original Design**: `/docs/mobile-ui-design.md`

---

## 💡 Tips

### For Best UX
1. Keep responses conversational
2. Show typing indicator
3. Use action chips generously
4. Auto-scroll to new messages
5. Handle errors gracefully

### For Performance
1. Virtualize long conversations
2. Lazy load images
3. Debounce typing events
4. Cache common responses
5. Optimize re-renders

### For Engagement
1. Welcome message on open
2. Suggest next actions
3. Celebrate completions
4. Provide context
5. Be helpful!

---

## 🐛 Troubleshooting

### Messages not scrolling
```javascript
// Add key to messages map
{messages.map((msg) => (
  <div key={msg.id}>...</div>
))}
```

### Input not focusing
```javascript
// Use ref and focus
inputRef.current?.focus();
```

### Chips not clickable
```javascript
// Check z-index and pointer-events
className="relative z-10"
```

---

## 🎉 What's Next?

### Planned Features
- [ ] Voice input/output
- [ ] Image sharing
- [ ] Event templates in chat
- [ ] Smart suggestions
- [ ] Conversation search
- [ ] Export chat history
- [ ] Multi-language support
- [ ] Custom themes

---

## 🤝 Contributing

Want to improve the chat interface? Here's how:

1. **Add new action chips**
   - Edit `ChatScreen.jsx`
   - Add to `actions` array
   - Handle in `handleActionClick`

2. **Customize AI responses**
   - Update `handleSendMessage`
   - Add conversation patterns
   - Connect to real AI backend

3. **Enhance components**
   - Improve animations
   - Add more variants
   - Better error states

---

## 📞 Support

Having issues? Check these resources:

- **Documentation**: `/docs/` folder
- **Examples**: Look in `ChatScreen.jsx`
- **Original Design**: Compare with `App.jsx`

---

**This chat-focused interface makes event planning feel like texting a friend. No complex menus, no navigation—just conversation!**

---

**Version**: 2.0 (Chat-Focused)
**Inspired by**: Gemini Canvas
**Created**: 2024-12-05
