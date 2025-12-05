export const ProgressBar = ({ progress, className = '', showLabel = false }) => {
  const getColorClass = (progress) => {
    if (progress >= 80) return 'bg-success';
    if (progress >= 50) return 'bg-primary';
    if (progress >= 25) return 'bg-warning';
    return 'bg-danger';
  };

  return (
    <div className={className}>
      <div className="h-2 bg-gray-light rounded-full overflow-hidden">
        <div
          className={`h-full ${getColorClass(progress)} transition-all duration-300`}
          style={{ width: `${progress}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray mt-1">{progress}% complete</p>
      )}
    </div>
  );
};
