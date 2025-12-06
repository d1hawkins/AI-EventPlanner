import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Calendar, Users, TrendingUp, DollarSign, RefreshCw } from 'lucide-react';
import { useDashboard } from '../hooks/useDashboard';
import { StatCard } from '../components/dashboard/StatCard';
import { ActivityFeed } from '../components/dashboard/ActivityFeed';
import { EventListCard } from '../components/events/EventListCard';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Button } from '../components/Button';

/**
 * DashboardPage - Overview dashboard with statistics
 *
 * Features:
 * - Key statistics cards
 * - Recent activity feed
 * - Upcoming events
 * - Quick actions
 */

export const DashboardPage = () => {
  const navigate = useNavigate();
  const { stats, activity, upcomingEvents, loading, error, refetch } = useDashboard();

  if (loading) {
    return <LoadingSpinner fullPage message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        variant="fullPage"
        title="Failed to load dashboard"
        message={error}
        retry={refetch}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gray-bg dark:bg-dark-bg-primary pb-20 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-dark-bg-secondary border-b border-gray-200 dark:border-dark-bg-tertiary px-4 py-4 sticky top-0 z-10 transition-colors">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
              aria-label="Go back"
            >
              <ArrowLeft size={24} className="text-gray-700 dark:text-dark-text-primary" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-dark-text-primary transition-colors">
                Dashboard
              </h1>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
                Overview of your events
              </p>
            </div>
          </div>

          <button
            onClick={refetch}
            className="p-2 hover:bg-gray-100 dark:hover:bg-dark-bg-tertiary rounded-lg transition-colors"
            aria-label="Refresh"
          >
            <RefreshCw size={20} className="text-gray-700 dark:text-dark-text-primary" />
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="px-4 py-6 space-y-6">
        {/* Statistics Cards */}
        <div className="grid grid-cols-2 gap-4">
          <StatCard
            icon={Calendar}
            label="Total Events"
            value={stats?.total_events || 0}
            change={stats?.events_change}
            trend={stats?.events_trend}
            color="blue"
          />
          <StatCard
            icon={Calendar}
            label="Active Events"
            value={stats?.active_events || 0}
            change={stats?.active_change}
            trend={stats?.active_trend}
            color="green"
          />
          <StatCard
            icon={Users}
            label="Total Guests"
            value={stats?.total_guests || 0}
            change={stats?.guests_change}
            trend={stats?.guests_trend}
            color="purple"
          />
          <StatCard
            icon={DollarSign}
            label="Budget Used"
            value={stats?.budget_used ? `${stats.budget_used}%` : '0%'}
            change={stats?.budget_change}
            trend={stats?.budget_trend}
            color="orange"
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 transition-colors">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary mb-3 transition-colors">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <Button
              variant="primary"
              size="sm"
              icon={<Calendar size={18} />}
              onClick={() => navigate('/events/new')}
            >
              New Event
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={<Users size={18} />}
              onClick={() => navigate('/team')}
            >
              Manage Team
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={<Calendar size={18} />}
              onClick={() => navigate('/events')}
            >
              View All
            </Button>
            <Button
              variant="secondary"
              size="sm"
              icon={<TrendingUp size={18} />}
              onClick={() => navigate('/subscription')}
            >
              Upgrade
            </Button>
          </div>
        </div>

        {/* Upcoming Events */}
        {upcomingEvents && upcomingEvents.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary transition-colors">
                Upcoming Events
              </h2>
              <button
                onClick={() => navigate('/events')}
                className="text-sm font-medium text-primary dark:text-primary-light hover:underline transition-colors"
              >
                View All
              </button>
            </div>
            <div className="space-y-3">
              {upcomingEvents.slice(0, 3).map((event) => (
                <EventListCard
                  key={event.id}
                  event={event}
                  onClick={(e) => navigate(`/events/${e.id}`)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Recent Activity */}
        <div className="bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-xl p-4 transition-colors">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text-primary transition-colors">
              Recent Activity
            </h2>
            <button
              onClick={() => navigate('/activity')}
              className="text-sm font-medium text-primary dark:text-primary-light hover:underline transition-colors"
            >
              View All
            </button>
          </div>
          <ActivityFeed activities={activity} limit={5} />
        </div>

        {/* Back to Chat */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-900/40 rounded-xl p-4 transition-colors">
          <p className="text-sm text-blue-900 dark:text-blue-300 mb-3 transition-colors">
            Need help planning your events? Chat with our AI assistant for personalized assistance!
          </p>
          <Button
            variant="primary"
            size="sm"
            fullWidth
            onClick={() => navigate('/chat')}
          >
            Chat with AI Assistant
          </Button>
        </div>
      </div>
    </div>
  );
};
