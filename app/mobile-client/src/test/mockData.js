/**
 * Mock data for testing
 */

export const mockUser = {
  id: '1',
  username: 'testuser',
  email: 'test@example.com',
  name: 'Test User',
  organizationId: 'org-123',
};

export const mockEvent = {
  id: '1',
  name: 'Birthday Party',
  date: '2024-12-25',
  icon: '🎉',
  status: 'active',
  guests_count: 50,
  budget: 5000,
  budget_spent: 2500,
  progress: 50,
  description: 'A wonderful birthday celebration',
  location: 'Community Center',
  created_at: '2024-12-01T00:00:00Z',
  updated_at: '2024-12-05T00:00:00Z',
};

export const mockEvents = [
  mockEvent,
  {
    id: '2',
    name: 'Wedding',
    date: '2025-06-15',
    icon: '💒',
    status: 'draft',
    guests_count: 150,
    budget: 25000,
    budget_spent: 5000,
    progress: 20,
  },
  {
    id: '3',
    name: 'Conference',
    date: '2024-12-10',
    icon: '📊',
    status: 'completed',
    guests_count: 200,
    budget: 50000,
    budget_spent: 48000,
    progress: 100,
  },
];

export const mockTeamMember = {
  id: '1',
  name: 'John Doe',
  email: 'john@example.com',
  role: 'admin',
  status: 'active',
  avatar: 'https://example.com/avatar.jpg',
  joined_date: '2024-01-01',
};

export const mockTeamMembers = [
  mockTeamMember,
  {
    id: '2',
    name: 'Jane Smith',
    email: 'jane@example.com',
    role: 'member',
    status: 'active',
    joined_date: '2024-02-01',
  },
  {
    id: '3',
    name: 'Bob Johnson',
    email: 'bob@example.com',
    role: 'owner',
    status: 'active',
    joined_date: '2024-01-01',
  },
];

export const mockInvite = {
  id: '1',
  email: 'newuser@example.com',
  role: 'member',
  status: 'pending',
  created_at: '2024-12-05T00:00:00Z',
};

export const mockSubscription = {
  id: '1',
  plan_name: 'Pro',
  status: 'active',
  billing_cycle: 'monthly',
  next_billing_date: '2025-01-05',
  current_period_end: '2025-01-05',
  payment_method: {
    last4: '4242',
    exp_month: '12',
    exp_year: '2025',
  },
};

export const mockPlan = {
  id: '1',
  name: 'Pro',
  price: 29,
  billing_period: 'month',
  description: 'Perfect for growing teams',
  features: [
    'Unlimited events',
    'Up to 10 team members',
    'Priority support',
    'Advanced analytics',
  ],
  limits: {
    events: -1,
    team_members: 10,
    storage: 100,
  },
};

export const mockPlans = [
  {
    id: '1',
    name: 'Free',
    price: 0,
    billing_period: 'month',
    features: ['Up to 3 events', '1 team member', 'Basic support'],
    limits: { events: 3, team_members: 1, storage: 1 },
  },
  mockPlan,
  {
    id: '3',
    name: 'Enterprise',
    price: 99,
    billing_period: 'month',
    features: ['Unlimited everything', '24/7 support', 'Custom integrations'],
    limits: { events: -1, team_members: -1, storage: -1 },
  },
];

export const mockUsage = {
  events: { current: 2, limit: 3 },
  team_members: { current: 1, limit: 1 },
  storage: { current: 0.5, limit: 1 },
};

export const mockDashboardStats = {
  total_events: 5,
  active_events: 3,
  total_guests: 150,
  budget_used: 75,
  trend: {
    events: 10,
    guests: 5,
    budget: -5,
  },
};

export const mockActivity = [
  {
    id: '1',
    type: 'event_created',
    message: 'Created event "Birthday Party"',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    user: 'Test User',
  },
  {
    id: '2',
    type: 'member_added',
    message: 'Added Jane Smith to team',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    user: 'Test User',
  },
];

export const mockBillingHistory = [
  {
    id: '1',
    amount: 29,
    date: '2024-11-05',
    status: 'paid',
    description: 'Pro Plan - Monthly',
    invoice_url: 'https://example.com/invoice/1',
  },
  {
    id: '2',
    amount: 29,
    date: '2024-10-05',
    status: 'paid',
    description: 'Pro Plan - Monthly',
    invoice_url: 'https://example.com/invoice/2',
  },
];

export const mockTasks = [
  {
    id: '1',
    title: 'Book venue',
    status: 'completed',
    due_date: '2024-12-10',
  },
  {
    id: '2',
    title: 'Send invitations',
    status: 'in_progress',
    due_date: '2024-12-15',
  },
];

export const mockGuests = [
  {
    id: '1',
    name: 'Alice Johnson',
    email: 'alice@example.com',
    rsvp: 'accepted',
  },
  {
    id: '2',
    name: 'Bob Smith',
    email: 'bob@example.com',
    rsvp: 'pending',
  },
];

export const mockBudget = {
  total: 5000,
  spent: 2500,
  categories: [
    { name: 'Venue', budgeted: 2000, spent: 1500 },
    { name: 'Catering', budgeted: 2000, spent: 800 },
    { name: 'Decorations', budgeted: 1000, spent: 200 },
  ],
};
