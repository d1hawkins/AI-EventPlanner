import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Calendar, MessageCircle, User } from 'lucide-react';

export const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/home', icon: Home, label: 'Home' },
    { path: '/calendar', icon: Calendar, label: 'Calendar' },
    { path: '/chat', icon: MessageCircle, label: 'Chat' },
    { path: '/profile', icon: User, label: 'Profile' },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white dark:bg-dark-bg-secondary border-t border-gray-light dark:border-dark-bg-tertiary shadow-lg safe-area-bottom transition-colors">
      <div className="flex justify-around items-center py-2">
        {navItems.map(({ path, icon: Icon, label }) => {
          // Highlight chat when on "/" or "/chat"
          const isActive = location.pathname === path ||
                          (location.pathname === '/' && path === '/chat');

          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`flex flex-col items-center gap-1 px-4 py-2 transition-colors ${
                isActive
                  ? 'text-primary dark:text-primary-light'
                  : 'text-gray dark:text-dark-text-secondary'
              }`}
            >
              <Icon size={24} />
              <span className="text-xs font-medium">{label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
