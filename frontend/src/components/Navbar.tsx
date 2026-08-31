import React from 'react';
import { ShieldAlert, LayoutDashboard, ListOrdered, CheckSquare, BarChart3, FileSpreadsheet, Settings, Cpu, Sun, Moon } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isBackendConnected: boolean;
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  isBackendConnected,
  theme,
  toggleTheme,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', icon: ListOrdered },
    { id: 'reviews', label: 'Reviews', icon: CheckSquare },
    { id: 'evaluation', label: 'Evaluation', icon: BarChart3 },
    { id: 'audit', label: 'Audit Log', icon: FileSpreadsheet },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'sandbox', label: 'Model Sandbox', icon: Cpu },
  ];

  return (
    <header className="navbar">
      <div className="brand">
        <div className="brand-icon">
          <ShieldAlert size={26} />
        </div>
        <div className="brand-title">
          <h1>AI Risk Manager</h1>
          <p>Defensive Payment Fraud Detection Engine</p>
        </div>
      </div>

      <nav className="nav-links" aria-label="Main Navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="health-badge">
          <div className={`health-dot ${isBackendConnected ? '' : 'disconnected'}`} />
          <span>{isBackendConnected ? 'API Connected' : 'Connecting...'}</span>
        </div>
      </div>
    </header>
  );
};
