# 📋 Phase 1 Implementation Plan - Mobile Client

## Overview

This document provides a detailed implementation plan for Phase 1 high-priority features that will bring the mobile client to feature parity with critical SaaS client functionality while maintaining the chat-first mobile experience.

**Timeline**: 4-6 weeks
**Priority**: High
**Goal**: Achieve 60%+ feature parity with SaaS client

---

## 🎯 Phase 1 Goals

### Primary Objectives
1. ✅ Enable full event lifecycle management (Create, Read, Update, Delete)
2. ✅ Provide overview dashboard with key metrics
3. ✅ Enable team collaboration and management
4. ✅ Display subscription status and usage
5. ✅ Maintain chat-first UX with seamless navigation

### Success Metrics
- Users can manage events end-to-end without leaving mobile app
- Dashboard provides at-a-glance status of all events
- Teams can collaborate effectively on mobile
- Users understand their subscription limits
- Chat remains primary interface with smart navigation to detailed views

---

## 🏗️ Architecture Overview

### Navigation Strategy: Hybrid Chat-First

```
Chat Interface (Primary)
    ↓
  User asks question or takes action
    ↓
  AI responds with:
    - Quick info (inline cards)
    - Action chips for common tasks
    - "View Details" buttons → Navigate to dedicated pages
    ↓
Dedicated Pages (Secondary)
    - Full CRUD operations
    - Detailed data tables
    - Complex forms
    - Can always return to chat
```

### Tech Stack
- **Framework**: React 18 with Hooks
- **Routing**: React Router v6
- **State Management**: React Context + Custom Hooks
- **API Client**: Axios with interceptors
- **Styling**: Tailwind CSS with dark mode
- **Animations**: Framer Motion

---

## 📦 Component Structure

### New Pages (To Be Created)

```
src/pages/
├── EventsPage.jsx          # Event list with filters/search
├── EventDetailPage.jsx     # Single event detail with tabs
├── DashboardPage.jsx       # Overview with statistics
├── TeamPage.jsx            # Team member management
├── SubscriptionPage.jsx    # Plan and usage details
└── SettingsPage.jsx        # User and org settings
```

### New Components (To Be Created)

```
src/components/
├── events/
│   ├── EventList.jsx       # List of event cards
│   ├── EventCard.jsx       # Single event summary card
│   ├── EventForm.jsx       # Create/Edit event form
│   ├── TaskList.jsx        # Task management
│   ├── GuestList.jsx       # Guest management
│   └── BudgetTracker.jsx   # Budget/expense tracking
├── dashboard/
│   ├── StatCard.jsx        # Stat display card
│   ├── ActivityFeed.jsx    # Recent activity
│   └── UpcomingEvents.jsx  # Upcoming events widget
├── team/
│   ├── TeamMemberCard.jsx  # Team member info
│   ├── InviteForm.jsx      # Invite new member
│   └── RoleSelector.jsx    # Role/permission selector
├── subscription/
│   ├── PlanCard.jsx        # Current plan display
│   ├── UsageChart.jsx      # Usage visualization
│   └── UpgradeCard.jsx     # Upgrade prompt
└── common/
    ├── LoadingSpinner.jsx  # Loading indicator
    ├── ErrorMessage.jsx    # Error display
    ├── EmptyState.jsx      # Empty state placeholder
    ├── SearchBar.jsx       # Search input
    ├── FilterMenu.jsx      # Filter options
    └── ConfirmDialog.jsx   # Confirmation modal
```

### API Services (To Be Created)

```
src/services/
├── api.js              # Base API client configuration
├── eventsService.js    # Event-related API calls
├── teamsService.js     # Team-related API calls
├── subscriptionService.js  # Subscription API calls
├── dashboardService.js     # Dashboard API calls
└── settingsService.js      # Settings API calls
```

### Custom Hooks (To Be Created)

```
src/hooks/
├── useEvents.js        # Event data fetching/mutations
├── useTeam.js          # Team data management
├── useSubscription.js  # Subscription data
├── useDashboard.js     # Dashboard data
└── useToast.js         # Toast notifications
```

---

## 🔌 API Integration Plan

### 1. Base API Client Setup

**File**: `src/services/api.js`

**Features**:
- Axios instance with base URL configuration
- Request interceptor for auth token
- Request interceptor for tenant ID header
- Response interceptor for error handling
- Automatic token refresh on 401
- Request/response logging (dev mode)

**Error Handling**:
```javascript
// Centralized error handling
- 401 Unauthorized → Redirect to login
- 403 Forbidden → Show permission error
- 404 Not Found → Show not found message
- 429 Rate Limited → Show retry message
- 500 Server Error → Show generic error
- Network Error → Show offline message
```

### 2. Events API Integration

**Endpoints**:
```
GET    /api/events                    # List all events
POST   /api/events                    # Create event
GET    /api/events/:id                # Get event details
PUT    /api/events/:id                # Update event
DELETE /api/events/:id                # Delete event
GET    /api/events/:id/tasks          # Get tasks
POST   /api/events/:id/tasks          # Create task
PUT    /api/events/:id/tasks/:taskId  # Update task
DELETE /api/events/:id/tasks/:taskId  # Delete task
GET    /api/events/:id/guests         # Get guests
POST   /api/events/:id/guests         # Add guest
PUT    /api/events/:id/guests/:id     # Update guest
DELETE /api/events/:id/guests/:id     # Remove guest
GET    /api/events/:id/budget         # Get budget
POST   /api/events/:id/expenses       # Add expense
```

**Service Methods**:
```javascript
eventsService.getAll(filters)
eventsService.getById(id)
eventsService.create(eventData)
eventsService.update(id, eventData)
eventsService.delete(id)
eventsService.getTasks(eventId)
eventsService.createTask(eventId, taskData)
eventsService.updateTask(eventId, taskId, taskData)
eventsService.deleteTask(eventId, taskId)
eventsService.getGuests(eventId)
eventsService.addGuest(eventId, guestData)
eventsService.updateGuest(eventId, guestId, guestData)
eventsService.removeGuest(eventId, guestId)
eventsService.getBudget(eventId)
eventsService.addExpense(eventId, expenseData)
```

### 3. Team API Integration

**Endpoints**:
```
GET    /api/teams/:orgId/members           # List members
POST   /api/teams/:orgId/invite            # Invite member
DELETE /api/teams/:orgId/members/:userId   # Remove member
PUT    /api/teams/:orgId/members/:userId/role  # Update role
GET    /api/teams/:orgId/activity          # Activity log
```

**Service Methods**:
```javascript
teamsService.getMembers(orgId)
teamsService.inviteMember(orgId, email, role)
teamsService.removeMember(orgId, userId)
teamsService.updateRole(orgId, userId, role)
teamsService.getActivity(orgId)
```

### 4. Subscription API Integration

**Endpoints**:
```
GET    /api/subscription/organizations/:id/usage-limits  # Get limits (✅ Done!)
GET    /api/subscription/status                          # Get status
GET    /api/subscription/billing-history                 # Billing history
POST   /api/subscription/upgrade                         # Upgrade plan
POST   /api/subscription/downgrade                       # Downgrade plan
```

**Service Methods**:
```javascript
subscriptionService.getUsageLimits(orgId)  // ✅ Already implemented
subscriptionService.getStatus()
subscriptionService.getBillingHistory()
subscriptionService.upgrade(planId)
subscriptionService.downgrade(planId)
```

### 5. Dashboard API Integration

**Endpoints**:
```
GET    /api/dashboard/stats               # Overview statistics
GET    /api/dashboard/recent-activity     # Recent activity
GET    /api/dashboard/upcoming-events     # Upcoming events
```

**Service Methods**:
```javascript
dashboardService.getStats()
dashboardService.getRecentActivity()
dashboardService.getUpcomingEvents()
```

---

## 📄 Page Implementations

### 1. Events Page

**Route**: `/events`

**Features**:
- List all events with cards
- Search by name, date, status
- Filter by status (draft, active, completed, cancelled)
- Sort by date, name, progress
- Pull-to-refresh
- "Create Event" FAB button
- Empty state for no events

**Layout**:
```
┌─────────────────────────┐
│ 🔍 Search Events        │
│ [Filters] [Sort]        │
├─────────────────────────┤
│ 🎉 Birthday Party       │
│ Dec 15, 2024 • 75%      │
│ 50 guests • $2k/$3k     │
├─────────────────────────┤
│ 💼 Company Retreat      │
│ Jan 10, 2025 • 30%      │
│ 200 guests • $5k/$10k   │
├─────────────────────────┤
│         [+ Create]      │
└─────────────────────────┘
```

**Dark Mode**: ✅ Fully supported

### 2. Event Detail Page

**Route**: `/events/:id`

**Features**:
- Event header with icon, name, date, status
- Tabs: Overview, Tasks, Guests, Budget, Timeline
- Edit button (opens form)
- Delete button (with confirmation)
- Share event
- Return to chat about this event

**Overview Tab**:
- Event details (date, time, location, description)
- Progress bar
- Quick stats (guests, budget, tasks)
- Recent updates

**Tasks Tab**:
- Add/edit/delete tasks
- Mark complete/incomplete
- Assign to team members
- Due dates
- Priority levels

**Guests Tab**:
- Guest list with RSVP status
- Add guest (name, email, RSVP)
- Edit guest details
- Remove guest
- Send invitations
- Import/export

**Budget Tab**:
- Budget overview (allocated vs spent)
- Category breakdown
- Add expense
- Expense list
- Budget alerts

**Timeline Tab**:
- Visual timeline of event schedule
- Milestones
- Deadlines

**Dark Mode**: ✅ Fully supported

### 3. Dashboard Page

**Route**: `/dashboard`

**Features**:
- Overview statistics (4 stat cards)
- Upcoming events (next 5)
- Recent activity feed
- Quick actions
- "Ask AI" shortcut to chat

**Layout**:
```
┌─────────────────────────┐
│ Dashboard               │
├─────────────────────────┤
│ ┌────┐ ┌────┐ ┌────┐   │
│ │ 12 │ │ 8  │ │ 95%│   │
│ │Evt │ │Act │ │Bdg │   │
│ └────┘ └────┘ └────┘   │
├─────────────────────────┤
│ Upcoming Events         │
│ 🎉 Birthday Party       │
│ 💼 Company Retreat      │
│ ...                     │
├─────────────────────────┤
│ Recent Activity         │
│ • John joined team      │
│ • Budget updated        │
│ ...                     │
└─────────────────────────┘
```

**Dark Mode**: ✅ Fully supported

### 4. Team Page

**Route**: `/team`

**Features**:
- Team member list with avatars
- Role badges (Owner, Admin, Member)
- Invite button
- Search members
- Member actions (edit role, remove)
- Activity log

**Layout**:
```
┌─────────────────────────┐
│ Team (5 members)        │
│ [+ Invite]              │
├─────────────────────────┤
│ 👤 John Doe             │
│    Owner • Active       │
│    john@example.com     │
├─────────────────────────┤
│ 👤 Jane Smith           │
│    Admin • Active       │
│    jane@example.com     │
│    [Edit] [Remove]      │
├─────────────────────────┤
│ ...                     │
└─────────────────────────┘
```

**Dark Mode**: ✅ Fully supported

### 5. Subscription Page

**Route**: `/subscription`

**Features**:
- Current plan card
- Usage metrics with progress bars
- Feature comparison table
- Upgrade/downgrade buttons
- Billing history
- Payment method

**Layout**:
```
┌─────────────────────────┐
│ Current Plan            │
│ 💼 Professional         │
│ $29/month               │
├─────────────────────────┤
│ Usage This Month        │
│ Events: 8/20 ▓▓▓░░      │
│ Users: 5/10  ▓▓▓▓▓░░    │
│ Storage: 2GB/10GB ▓░░   │
├─────────────────────────┤
│ [Upgrade to Business]   │
├─────────────────────────┤
│ Billing History         │
│ Dec 2024 • $29 • Paid   │
│ Nov 2024 • $29 • Paid   │
└─────────────────────────┘
```

**Dark Mode**: ✅ Fully supported

---

## 🎨 UI/UX Patterns

### Loading States

**Skeleton Screens**:
```javascript
// For lists
<EventCardSkeleton count={3} />

// For forms
<FormSkeleton fields={5} />

// For pages
<PageSkeleton />
```

**Spinners**:
```javascript
// Inline actions
<Button loading={isLoading}>Save</Button>

// Full page
<LoadingSpinner fullPage />

// Section
<LoadingSpinner />
```

### Error Handling

**Error Messages**:
```javascript
// Inline errors
<ErrorMessage message="Failed to load events" retry={handleRetry} />

// Toast errors
toast.error("Could not delete event")

// Empty states with error
<EmptyState
  icon="⚠️"
  title="Failed to load"
  message="Could not load events"
  action="Try Again"
  onAction={handleRetry}
/>
```

### Empty States

```javascript
<EmptyState
  icon="📅"
  title="No events yet"
  message="Create your first event to get started"
  action="Create Event"
  onAction={handleCreate}
/>
```

### Confirmation Dialogs

```javascript
<ConfirmDialog
  open={showDelete}
  title="Delete Event?"
  message="This action cannot be undone"
  confirmText="Delete"
  confirmVariant="danger"
  onConfirm={handleDelete}
  onCancel={() => setShowDelete(false)}
/>
```

### Toast Notifications

```javascript
// Success
toast.success("Event created successfully")

// Error
toast.error("Failed to save changes")

// Info
toast.info("Changes saved as draft")

// Warning
toast.warning("Budget limit exceeded")
```

---

## 🔄 Chat Integration

### Navigation from Chat

**User**: "Show me my events"
**AI**: "Here are your upcoming events:"
- [Inline Event Cards]
- [Action Chip: "View All Events"] → Navigate to `/events`

**User**: "Create a new event"
**AI**: "I'd love to help you create an event!"
- [Action Chip: "Use Form"] → Navigate to `/events/new`
- [Action Chip: "Tell Me About It"] → Conversational creation

**User**: "How many team members do I have?"
**AI**: "You have 5 team members."
- [Action Chip: "View Team"] → Navigate to `/team`
- [Action Chip: "Invite Someone"] → Navigate to `/team/invite`

**User**: "What's my subscription?"
**AI**: "You're on the Professional plan ($29/month)."
- [Action Chip: "View Details"] → Navigate to `/subscription`
- [Action Chip: "Upgrade"] → Navigate to `/subscription?upgrade=true`

### Return to Chat

All pages have:
- Header with back button
- "Ask AI" FAB button that returns to chat with context
- Chat icon in side menu

Example context:
```javascript
// From event detail page
navigateToChat({
  context: "event",
  eventId: event.id,
  eventName: event.name,
  prompt: `Help me with "${event.name}"`
})

// Chat loads with:
// "I'm here to help with your Birthday Party event. What would you like to do?"
```

---

## 📱 Responsive Design

### Breakpoints
- Mobile: 0-640px (primary focus)
- Tablet: 641-1024px (stretch goal)
- Desktop: 1025px+ (not in scope)

### Touch Targets
- Minimum: 44x44px (Apple HIG)
- Preferred: 48x48px (Material Design)

### Typography Scale
```css
xs: 12px   /* Helper text */
sm: 14px   /* Secondary text */
base: 16px /* Body text */
lg: 18px   /* Emphasized text */
xl: 20px   /* Small headings */
2xl: 24px  /* Headings */
3xl: 30px  /* Page titles */
```

---

## 🧪 Testing Strategy

### Unit Tests
- API service methods
- Custom hooks
- Utility functions

### Integration Tests
- API integration
- Form submission
- Navigation flows

### Manual Testing Checklist

**Events**:
- [ ] Create event
- [ ] Edit event
- [ ] Delete event
- [ ] View event details
- [ ] Add/remove tasks
- [ ] Manage guests
- [ ] Track budget

**Dashboard**:
- [ ] View statistics
- [ ] See upcoming events
- [ ] Check activity feed
- [ ] Quick actions work

**Team**:
- [ ] View team members
- [ ] Invite member
- [ ] Update role
- [ ] Remove member

**Subscription**:
- [ ] View current plan
- [ ] Check usage
- [ ] See billing history
- [ ] Upgrade flow

**Dark Mode**:
- [ ] Toggle theme
- [ ] All pages render correctly
- [ ] Good contrast
- [ ] Smooth transitions

---

## 📅 Implementation Timeline

### Week 1: Foundation
- ✅ Create API client infrastructure
- ✅ Set up service modules
- ✅ Create common components (Loading, Error, Empty State)
- ✅ Set up routing for new pages

### Week 2: Events
- ✅ Events page with list
- ✅ Event detail page
- ✅ Create/Edit event forms
- ✅ Basic task management

### Week 3: Dashboard & Team
- ✅ Dashboard with statistics
- ✅ Team page with member list
- ✅ Invite functionality
- ✅ Role management

### Week 4: Subscription & Polish
- ✅ Subscription page
- ✅ Usage tracking
- ✅ Toast notifications
- ✅ Error handling improvements

### Week 5: Integration & Testing
- ✅ Chat navigation integration
- ✅ End-to-end testing
- ✅ Dark mode verification
- ✅ Bug fixes

### Week 6: Buffer & Documentation
- ✅ Final polish
- ✅ Documentation updates
- ✅ Code review
- ✅ Deployment preparation

---

## 🚀 Success Criteria

### Functional Requirements
- [ ] Users can create, edit, and delete events
- [ ] Users can view all events in a list
- [ ] Users can manage tasks, guests, and budget for events
- [ ] Dashboard shows accurate statistics
- [ ] Team management is fully functional
- [ ] Subscription information is displayed correctly
- [ ] Chat navigation works seamlessly
- [ ] All features work in dark mode

### Performance Requirements
- [ ] Pages load in < 2 seconds
- [ ] API calls complete in < 1 second
- [ ] Smooth animations (60fps)
- [ ] No memory leaks
- [ ] Efficient re-renders

### UX Requirements
- [ ] Intuitive navigation
- [ ] Clear error messages
- [ ] Responsive loading states
- [ ] Helpful empty states
- [ ] Accessible (keyboard, screen readers)

---

## 📚 Resources

### Documentation
- React Router: https://reactrouter.com
- Axios: https://axios-http.com
- Tailwind CSS: https://tailwindcss.com
- Framer Motion: https://www.framer.com/motion

### Design References
- Material Design: https://material.io
- iOS HIG: https://developer.apple.com/design/human-interface-guidelines
- Tailwind UI: https://tailwindui.com

---

**Plan Version**: 1.0
**Created**: 2024-12-05
**Status**: 🚀 Ready to Implement
**Branch**: `claude/identify-placeholders-011CUYG8UfAYNCycbNS291Da`
