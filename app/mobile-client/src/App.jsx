import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Home } from './pages/Home';
import { Chat } from './pages/Chat';
import { Profile } from './pages/Profile';
import { useAuth } from './hooks/useAuth';

// Placeholder components for missing pages
const Landing = () => (
  <div className="min-h-screen bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center px-4">
    <div className="text-center text-white">
      <div className="text-6xl mb-6">🎉</div>
      <h1 className="text-4xl font-bold mb-4">AI Event Planner</h1>
      <p className="text-lg mb-8 opacity-90">Plan perfect events with AI assistance</p>
      <button
        onClick={() => window.location.href = '/home'}
        className="bg-white text-primary px-8 py-3 rounded-lg font-semibold text-lg shadow-lg"
      >
        Get Started
      </button>
    </div>
  </div>
);

const Calendar = () => (
  <div className="min-h-screen bg-gray-bg p-4">
    <h1 className="text-2xl font-bold mb-4">Calendar</h1>
    <p>Calendar view coming soon...</p>
  </div>
);

const Settings = () => (
  <div className="min-h-screen bg-gray-bg p-4">
    <h1 className="text-2xl font-bold mb-4">Settings</h1>
    <p>Settings page coming soon...</p>
  </div>
);

const Notifications = () => (
  <div className="min-h-screen bg-gray-bg p-4">
    <h1 className="text-2xl font-bold mb-4">Notifications</h1>
    <p>Notifications coming soon...</p>
  </div>
);

const EventDetail = () => (
  <div className="min-h-screen bg-gray-bg p-4">
    <h1 className="text-2xl font-bold mb-4">Event Details</h1>
    <p>Event details coming soon...</p>
  </div>
);

// Protected Route wrapper
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    // For demo purposes, allow access
    // In production, redirect to login: return <Navigate to="/login" />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route
          path="/calendar"
          element={
            <ProtectedRoute>
              <Calendar />
            </ProtectedRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <ProtectedRoute>
              <Chat />
            </ProtectedRoute>
          }
        />
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/notifications"
          element={
            <ProtectedRoute>
              <Notifications />
            </ProtectedRoute>
          }
        />
        <Route
          path="/events/:id"
          element={
            <ProtectedRoute>
              <EventDetail />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
