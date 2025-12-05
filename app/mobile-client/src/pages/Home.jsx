import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { EventCard } from '../components/EventCard';
import { Button } from '../components/Button';
import { BottomNav } from '../components/BottomNav';
import { useEvents } from '../hooks/useEvents';
import { useAuth } from '../hooks/useAuth';

export const Home = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { events, loading } = useEvents();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4" />
          <p className="text-gray">Loading events...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-bg pb-20">
      {/* Header */}
      <header className="bg-white shadow-sm p-4 flex justify-between items-center">
        <h1 className="text-xl font-semibold">AI Event Planner</h1>
        <button
          onClick={() => navigate('/notifications')}
          className="relative p-2"
        >
          <span className="text-2xl">🔔</span>
          {/* Notification badge */}
          <span className="absolute top-1 right-1 bg-danger text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
            3
          </span>
        </button>
      </header>

      {/* Content */}
      <div className="p-4">
        {/* Greeting */}
        <div className="mb-6">
          <h2 className="text-2xl font-semibold mb-1">
            Hi {user?.username || 'there'}! 👋
          </h2>
          <p className="text-gray">Ready to plan?</p>
        </div>

        {/* New Event Button */}
        <Button
          fullWidth
          icon={<Plus size={20} />}
          onClick={() => navigate('/new-event')}
          className="mb-6"
        >
          New Event
        </Button>

        {/* Events List */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-3">Your Events</h3>

          {events.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎉</div>
              <p className="text-gray-400 mb-4">No events yet</p>
              <p className="text-gray mb-6">Let's plan your first event!</p>
              <Button
                variant="primary"
                icon={<Plus size={20} />}
                onClick={() => navigate('/new-event')}
              >
                Create Event
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {events.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  onClick={() => navigate(`/events/${event.id}`)}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Bottom Navigation */}
      <BottomNav />
    </div>
  );
};
