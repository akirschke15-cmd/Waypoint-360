import { Routes, Route, useLocation, Link, useNavigate } from 'react-router-dom';
import { Menu, BarChart3, GitBranch, Clock, AlertTriangle, Palette, LogOut } from 'lucide-react';
import { useState, useCallback } from 'react';
import CommandCenter from '@/components/CommandCenter';
import GateTimeline from '@/components/GateTimeline';
import DependencyGraph from '@/components/DependencyGraph';
import WorkstreamCard from '@/components/WorkstreamCard';
import WorkstreamForm from '@/components/WorkstreamForm';
import RiskHeatMap from '@/components/RiskHeatMap';
import Login from '@/components/Login';
import { ThemeProvider, useTheme } from '@/themes/index';
import type { ThemeName } from '@/themes/index';

const navigation = [
  { name: 'Dashboard', href: '/', icon: BarChart3 },
  { name: 'Gate Timeline', href: '/gates', icon: Clock },
  { name: 'Dependencies', href: '/dependencies', icon: GitBranch },
  { name: 'Risks', href: '/risks', icon: AlertTriangle },
];

function Sidebar({ open, setOpen, onLogout }: { open: boolean; setOpen: (open: boolean) => void; onLogout: () => void }) {
  const location = useLocation();
  const { currentTheme, setTheme } = useTheme();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const toggleTheme = () => {
    setTheme(currentTheme === 'swa' ? 'neutral' : 'swa' as ThemeName);
  };

  return (
    <>
      {open && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setOpen(false)} />
      )}

      <aside className={`fixed left-0 top-0 z-40 h-screen w-64 bg-neutral-800 border-r border-neutral-700 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:h-screen ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="p-6 border-b border-neutral-700">
          <h1 className="text-xl font-bold text-swa-blue">Waypoint 360</h1>
          <p className="text-[10px] text-neutral-500 mt-0.5 uppercase tracking-widest">Program Control Tower</p>
        </div>

        <nav className="flex-1 overflow-y-auto p-3">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors mb-1 ${
                  isActive
                    ? 'bg-swa-blue/10 text-swa-blue border border-swa-blue/20'
                    : 'text-neutral-400 hover:bg-neutral-700/50 hover:text-neutral-200 border border-transparent'
                }`}
                onClick={() => setOpen(false)}
              >
                <Icon size={18} />
                <span className="text-sm font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-neutral-700 space-y-3">
          <button
            onClick={toggleTheme}
            className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-xs text-neutral-500 hover:bg-neutral-700/50 hover:text-neutral-300 transition-colors"
          >
            <Palette size={14} />
            <span>{currentTheme === 'swa' ? 'SWA Theme' : 'Neutral Theme'}</span>
          </button>
          <div className="flex items-center justify-between px-1">
            <div className="text-[10px] text-neutral-600">
              <p className="text-neutral-400 font-medium">{user.name || 'User'}</p>
              <p>{user.role || ''}</p>
            </div>
            <button
              onClick={onLogout}
              className="p-1.5 rounded text-neutral-500 hover:text-red-400 hover:bg-neutral-700/50 transition-colors"
              title="Sign out"
            >
              <LogOut size={14} />
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

function AppLayout({ onLogout }: { onLogout: () => void }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const pageTitle = navigation.find((item) => item.href === location.pathname)?.name
    || (location.pathname.startsWith('/workstreams/') ? 'Workstream Detail' : 'Dashboard');

  return (
    <div className="flex min-h-screen bg-neutral-900">
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} onLogout={onLogout} />

      <main className="flex-1 overflow-auto">
        <header className="sticky top-0 z-30 bg-neutral-800/95 border-b border-neutral-700 px-6 py-3 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg bg-neutral-700 text-neutral-100"
                aria-label="Open sidebar"
              >
                <Menu size={18} />
              </button>
              <div>
                <h2 className="text-lg font-semibold text-neutral-100">{pageTitle}</h2>
                <p className="text-xs text-neutral-500">
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
              </div>
            </div>
          </div>
        </header>

        <div className="p-6 lg:p-8">
          <Routes>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/gates" element={<GateTimeline />} />
            <Route path="/dependencies" element={<DependencyGraph />} />
            <Route path="/risks" element={<RiskHeatMap />} />
            <Route path="/workstreams/:id" element={<WorkstreamCard />} />
            <Route path="/workstreams/new" element={<WorkstreamForm />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

function AuthenticatedApp() {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('token'));

  const handleLogin = useCallback(() => {
    setIsAuthenticated(true);
    navigate('/');
  }, [navigate]);

  const handleLogout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setIsAuthenticated(false);
  }, []);

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return <AppLayout onLogout={handleLogout} />;
}

export default function App() {
  return (
    <ThemeProvider defaultTheme="swa">
      <AuthenticatedApp />
    </ThemeProvider>
  );
}
