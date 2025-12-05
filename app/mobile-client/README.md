# AI Event Planner - Mobile Client

A modern, mobile-first React application for event planning with AI assistance.

## 🚀 Features

- **Conversational AI**: Chat-based interface for natural event planning
- **Event Management**: Create, track, and manage events with progress indicators
- **Calendar View**: Visual calendar with event scheduling
- **Budget Tracking**: Monitor and manage event budgets
- **Guest Management**: Track RSVPs and manage attendees
- **Notifications**: Real-time updates and reminders
- **Offline Support**: PWA with offline capabilities

## 📱 Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Date Utilities**: date-fns

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button.jsx
│   ├── Card.jsx
│   ├── EventCard.jsx
│   ├── ChatBubble.jsx
│   ├── ProgressBar.jsx
│   ├── BottomNav.jsx
│   └── QuickReplyButton.jsx
├── pages/              # Page components
│   ├── Landing.jsx
│   ├── Home.jsx
│   ├── Chat.jsx
│   ├── EventDetail.jsx
│   ├── Calendar.jsx
│   ├── Profile.jsx
│   ├── Settings.jsx
│   └── Notifications.jsx
├── hooks/              # Custom React hooks
│   ├── useAuth.js
│   ├── useEvents.js
│   └── useChat.js
├── api/                # API client and endpoints
│   ├── client.js
│   ├── events.js
│   └── chat.js
├── utils/              # Utility functions
│   └── dateUtils.js
├── styles/             # Global styles
│   └── index.css
├── App.jsx             # Main app component
└── main.jsx            # Entry point
```

## 🎨 Design System

### Colors
```javascript
primary: '#4E73DF'    // CTAs, links, active states
success: '#1CC88A'    // Completed, positive actions
warning: '#F6C23E'    // Warnings, pending items
danger: '#E74A3B'     // Errors, urgent items
gray: '#858796'       // Secondary text, icons
```

### Typography
- **Font**: Inter, system-ui
- **Sizes**: 12px (xs) → 28px (2xl)
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Spacing
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The app will be available at `http://localhost:3000`

## 📄 Pages

### 1. Landing/Login
- Welcome screen with value proposition
- Email/password login
- "Get Started" CTA

### 2. Home Dashboard
- Event cards with progress tracking
- "New Event" button
- Quick access to all events
- Bottom navigation

### 3. Chat Interface
- Conversational AI assistant
- Chat bubbles (AI vs user)
- Quick reply buttons
- Voice and attachment support

### 4. Event Detail
- Event hero section
- Progress indicator
- Budget tracking
- Task checklist
- Quick chat access

### 5. Calendar
- Month view calendar
- Event indicators
- Upcoming events list
- Tap to view details

### 6. Profile
- User information
- Account settings
- Subscription details
- Usage statistics
- Sign out

### 7. Settings
- Dark mode toggle
- Notification preferences
- Privacy & security
- Data management
- Help & support

### 8. Notifications
- Chronologically grouped
- Multiple notification types
- Mark as read
- Swipe to dismiss

## 🔗 API Integration

The app connects to the FastAPI backend:

### Authentication
```javascript
POST /auth/token          // Login
GET  /auth/me             // Get current user
GET  /auth/me/organization // Get user's organization
```

### Events
```javascript
GET    /api/events        // List all events
GET    /api/events/:id    // Get event details
POST   /api/events        // Create event
PUT    /api/events/:id    // Update event
DELETE /api/events/:id    // Delete event
```

### Chat
```javascript
GET  /api/agents/conversations              // List conversations
GET  /api/agents/conversations/:id          // Get conversation
POST /api/agents/conversations              // Create conversation
POST /api/agents/conversations/:id/messages // Send message
```

## 📱 Mobile Optimizations

### Touch-Friendly
- Minimum 44x44px tap targets
- Swipe gestures for navigation
- Pull-to-refresh on lists
- Bottom navigation for thumb access

### Performance
- Code splitting by route
- Lazy loading images
- Service worker for offline
- Optimized bundle size

### Responsive
- Mobile-first design
- Breakpoints: 768px (tablet), 1024px (desktop)
- Flexible layouts
- Touch and mouse support

## ♿ Accessibility

- WCAG AA compliant color contrast
- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader friendly
- Focus indicators
- Semantic HTML

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

## 🌐 Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_APP_NAME=AI Event Planner
```

## 📦 Build & Deploy

### Production Build
```bash
npm run build
```

Output will be in `dist/` directory.

### Deploy to Netlify
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

### Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

## 🔧 Development

### Component Development
```bash
# Add new component
touch src/components/MyComponent.jsx

# Import in page
import { MyComponent } from '@/components/MyComponent';
```

### Adding a New Page
1. Create component in `src/pages/`
2. Add route in `App.jsx`
3. Add navigation item if needed

### Custom Hooks
```javascript
// src/hooks/useMyHook.js
import { useState, useEffect } from 'react';

export const useMyHook = () => {
  // Hook logic
  return { /* exported values */ };
};
```

## 📝 Code Style

- ESLint for linting
- Prettier for formatting
- Conventional commits for git messages

## 🐛 Debugging

### React DevTools
Install React DevTools browser extension for component inspection.

### Network Requests
All API calls are logged in development mode.

### Console Logging
```javascript
console.log('Debug:', data);
console.error('Error:', error);
console.warn('Warning:', message);
```

## 🚀 Performance Tips

1. **Lazy Load Components**
```javascript
const Profile = lazy(() => import('./pages/Profile'));
```

2. **Memoize Expensive Calculations**
```javascript
const memoizedValue = useMemo(() => computeExpensiveValue(a, b), [a, b]);
```

3. **Optimize Re-renders**
```javascript
const MemoizedComponent = memo(MyComponent);
```

## 📚 Resources

- [React Documentation](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Framer Motion](https://www.framer.com/motion/)
- [Lucide Icons](https://lucide.dev)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Design inspired by modern mobile-first principles
- AI-powered by the event planner backend
- Built with love for event organizers

---

**Version**: 1.0.0
**Last Updated**: 2024-12-05
