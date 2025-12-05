import { Card } from './Card';
import { ProgressBar } from './ProgressBar';
import { formatDate } from '../utils/dateUtils';

export const EventCard = ({ event, onClick }) => {
  const { id, name, date, icon, progress, status } = event;

  const statusColors = {
    active: 'text-primary',
    completed: 'text-success',
    cancelled: 'text-gray',
  };

  const progressDots = Array.from({ length: 5 }, (_, i) => (
    <span
      key={i}
      className={`inline-block w-2 h-2 rounded-full ${
        i < Math.floor(progress / 20) ? 'bg-success' : 'bg-gray-light'
      }`}
    />
  ));

  return (
    <Card interactive onClick={() => onClick && onClick(event)} className="mb-3">
      <div className="flex flex-col">
        <div className="text-2xl mb-2">{icon || '🎉'}</div>
        <h3 className="font-semibold text-lg mb-1">{name}</h3>
        <p className="text-sm text-gray mb-3">{formatDate(date)}</p>

        <ProgressBar progress={progress} className="mb-2" />

        <div className="flex items-center justify-between">
          <div className="flex gap-1">{progressDots}</div>
          <span className={`text-sm font-medium ${statusColors[status]}`}>
            {progress}% done
          </span>
        </div>
      </div>
    </Card>
  );
};
