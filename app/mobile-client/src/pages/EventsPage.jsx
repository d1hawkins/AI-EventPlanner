import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, SlidersHorizontal, ArrowLeft } from 'lucide-react';
import { useEvents } from '../hooks/useEvents';
import { EventListCard } from '../components/events/EventListCard';
import { LoadingSpinner, CardSkeleton } from '../components/common/LoadingSpinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { EmptyState, EmptySearchState, EmptyFilterState } from '../components/common/EmptyState';
import { SearchBar } from '../components/common/SearchBar';
import { Button } from '../components/Button';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useToast } from '../hooks/useToast';

/**
 * EventsPage - Main events list page
 *
 * Features:
 * - List all events
 * - Search events
 * - Filter by status
 * - Sort events
 * - Create new event
 * - Navigate to event details
 * - Delete events
 */

export const EventsPage = () => {
  const navigate = useNavigate();
  const toast = useToast();

  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [showFilters, setShowFilters] = useState(false);
  const [eventToDelete, setEventToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const { events, loading, error, deleteEvent, refetch } = useEvents({
    search: searchTerm,
    status: filterStatus !== 'all' ? filterStatus : undefined,
    sort: sortBy,
  });

  const handleEventClick = (event) => {
    navigate(`/events/${event.id}`);
  };

  const handleEditEvent = (event) => {
    navigate(`/events/${event.id}/edit`);
  };

  const handleDeleteEvent = async () => {
    if (!eventToDelete) return;

    try {
      setIsDeleting(true);
      await deleteEvent(eventToDelete.id);
      toast.success(`"${eventToDelete.name}" deleted successfully`);
      setEventToDelete(null);
    } catch (err) {
      toast.error(`Failed to delete event: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateEvent = () => {
    navigate('/events/new');
  };

  const filteredEvents = events.filter((event) => {
    if (searchTerm && !event.name.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    if (filterStatus !== 'all' && event.status !== filterStatus) {
      return false;
    }
    return true;
  });

  const sortedEvents = [...filteredEvents].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(a.date) - new Date(b.date);
      case 'name':
        return a.name.localeCompare(b.name);
      case 'progress':
        return (b.progress || 0) - (a.progress || 0);
      default:
        return 0;
    }
  });

  const statusCounts = events.reduce((acc, event) => {
    acc[event.status] = (acc[event.status] || 0) + 1;
    return acc;
  }, { all: events.length });

  return (
    <div className="min-h-screen bg-gray-bg dark:bg-dark-bg-primary pb-20 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-dark-bg-secondary border-b border-gray-200 dark:border-dark-bg-tertiary px-4 py-4 sticky top-0 z-10 transition-colors">
        <div className="flex items-center justify-between mb-4">
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
                Events
              </h1>
              <p className="text-sm text-gray-600 dark:text-dark-text-secondary transition-colors">
                {events.length} {events.length === 1 ? 'event' : 'events'}
              </p>
            </div>
          </div>

          <button
            onClick={handleCreateEvent}
            className="p-2 bg-primary dark:bg-primary-light text-white rounded-lg hover:bg-primary-dark dark:hover:bg-primary transition-colors"
            aria-label="Create event"
          >
            <Plus size={24} />
          </button>
        </div>

        {/* Search */}
        <SearchBar
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Search events..."
        />

        {/* Filters Toggle */}
        <div className="flex items-center gap-2 mt-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              showFilters
                ? 'bg-primary dark:bg-primary-light text-white'
                : 'bg-gray-100 dark:bg-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary'
            }`}
          >
            <SlidersHorizontal size={16} />
            Filters
          </button>

          {/* Quick filter chips */}
          <div className="flex-1 flex gap-2 overflow-x-auto">
            {['all', 'active', 'draft', 'completed'].map((status) => (
              <button
                key={status}
                onClick={() => setFilterStatus(status)}
                className={`px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  filterStatus === status
                    ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                    : 'bg-gray-100 dark:bg-dark-bg-tertiary text-gray-700 dark:text-dark-text-primary'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
                {statusCounts[status] > 0 && (
                  <span className="ml-1 text-xs opacity-75">({statusCounts[status]})</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Filter Panel */}
        {showFilters && (
          <div className="mt-3 p-3 bg-gray-50 dark:bg-dark-bg-primary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg transition-colors">
            <div className="flex items-center gap-3">
              <label className="text-sm font-medium text-gray-700 dark:text-dark-text-primary transition-colors">
                Sort by:
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="flex-1 px-3 py-2 bg-white dark:bg-dark-bg-secondary border border-gray-200 dark:border-dark-bg-tertiary rounded-lg text-gray-900 dark:text-dark-text-primary transition-colors"
              >
                <option value="date">Date</option>
                <option value="name">Name</option>
                <option value="progress">Progress</option>
              </select>
            </div>
          </div>
        )}
      </header>

      {/* Content */}
      <div className="px-4 py-4">
        {loading && !events.length ? (
          <CardSkeleton count={5} />
        ) : error ? (
          <ErrorMessage
            title="Failed to load events"
            message={error}
            retry={refetch}
          />
        ) : sortedEvents.length === 0 ? (
          searchTerm ? (
            <EmptySearchState
              searchTerm={searchTerm}
              onClear={() => setSearchTerm('')}
            />
          ) : filterStatus !== 'all' ? (
            <EmptyFilterState onClear={() => setFilterStatus('all')} />
          ) : (
            <EmptyState
              icon="📅"
              title="No events yet"
              message="Create your first event to get started planning!"
              action="Create Event"
              onAction={handleCreateEvent}
            />
          )
        ) : (
          <div>
            {sortedEvents.map((event) => (
              <EventListCard
                key={event.id}
                event={event}
                onClick={handleEventClick}
                onEdit={handleEditEvent}
                onDelete={(e) => setEventToDelete(e)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        open={!!eventToDelete}
        onClose={() => setEventToDelete(null)}
        onConfirm={handleDeleteEvent}
        title="Delete Event?"
        message={`Are you sure you want to delete "${eventToDelete?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        confirmVariant="danger"
        loading={isDeleting}
      />

      {/* Floating Action Button (alternative for mobile) */}
      <button
        onClick={handleCreateEvent}
        className="fixed bottom-20 right-4 w-14 h-14 bg-primary dark:bg-primary-light text-white rounded-full shadow-lg flex items-center justify-center hover:bg-primary-dark dark:hover:bg-primary transition-all hover:scale-110 active:scale-95"
        aria-label="Create event"
      >
        <Plus size={28} />
      </button>
    </div>
  );
};
