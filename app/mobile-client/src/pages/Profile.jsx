import { useNavigate } from 'react-router-dom';
import {
  Mail,
  Bell,
  Lock,
  CreditCard,
  BarChart3,
  LogOut,
  ChevronRight,
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { BottomNav } from '../components/BottomNav';
import { useAuth } from '../hooks/useAuth';

export const Profile = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const MenuItem = ({ icon: Icon, label, value, onClick }) => (
    <button
      onClick={onClick}
      className="w-full flex items-center justify-between py-3 border-b border-gray-light last:border-0"
    >
      <div className="flex items-center gap-3">
        <Icon size={20} className="text-gray" />
        <div className="text-left">
          <p className="font-medium">{label}</p>
          {value && <p className="text-sm text-gray">{value}</p>}
        </div>
      </div>
      <ChevronRight size={20} className="text-gray" />
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-bg pb-20">
      {/* Header */}
      <header className="bg-white shadow-sm p-4">
        <h1 className="text-xl font-semibold">Profile</h1>
      </header>

      <div className="p-4">
        {/* Profile Card */}
        <Card className="text-center mb-6">
          <div className="w-20 h-20 bg-primary rounded-full mx-auto mb-3 flex items-center justify-center text-white text-3xl">
            👤
          </div>
          <h2 className="font-semibold text-lg mb-1">
            {user?.username || 'User'}
          </h2>
          <p className="text-sm text-gray mb-4">
            {user?.email || 'user@example.com'}
          </p>
          <Button variant="secondary" size="sm" fullWidth>
            Edit Profile
          </Button>
        </Card>

        {/* Account Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray uppercase mb-3">
            Account
          </h3>
          <Card className="p-0">
            <div className="p-4">
              <MenuItem
                icon={Mail}
                label="Email"
                value={user?.email || 'user@example.com'}
                onClick={() => {}}
              />
              <MenuItem
                icon={Bell}
                label="Notifications"
                value="Enabled"
                onClick={() => navigate('/settings')}
              />
              <MenuItem
                icon={Lock}
                label="Privacy"
                value="Manage settings"
                onClick={() => navigate('/settings')}
              />
            </div>
          </Card>
        </div>

        {/* Subscription Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray uppercase mb-3">
            Subscription
          </h3>
          <Card>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CreditCard size={20} className="text-primary" />
                <div>
                  <p className="font-semibold">Professional Plan</p>
                  <p className="text-sm text-gray">$29/month</p>
                </div>
              </div>
            </div>
            <Button variant="secondary" size="sm" fullWidth>
              Manage Plan
            </Button>
          </Card>
        </div>

        {/* Statistics Section */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray uppercase mb-3">
            Statistics
          </h3>
          <Card>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-primary mb-1">12</div>
                <div className="text-xs text-gray">Events</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-success mb-1">156</div>
                <div className="text-xs text-gray">Tasks Done</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-warning mb-1">$45K</div>
                <div className="text-xs text-gray">Budget</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Danger Zone */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray uppercase mb-3">
            Danger Zone
          </h3>
          <Button
            variant="danger"
            fullWidth
            icon={<LogOut size={18} />}
            onClick={handleLogout}
          >
            Sign Out
          </Button>
        </div>
      </div>

      <BottomNav />
    </div>
  );
};
