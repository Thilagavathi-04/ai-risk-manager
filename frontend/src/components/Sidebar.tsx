import React from 'react';
import {
  ShieldAlert,
  LayoutDashboard,
  ListOrdered,
  CheckSquare,
  BarChart3,
  FileSpreadsheet,
  SlidersHorizontal,
  Sun,
  Moon,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  isBackendConnected: boolean;
  theme: 'dark' | 'light';
  toggleTheme: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  theme,
  toggleTheme,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', icon: ListOrdered },
    { id: 'reviews', label: 'Reviews', icon: CheckSquare },
    { id: 'evaluation', label: 'Evaluation', icon: BarChart3 },
    { id: 'audit', label: 'Audit Log', icon: FileSpreadsheet },
    { id: 'settings', label: 'Model & Test Data', icon: SlidersHorizontal },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <ShieldAlert size={24} />
        </div>
        <div className="brand-title">
          <h1>AI Risk Manager</h1>
          <p>Merchant Risk Control</p>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Main Navigation">
        <span className="sidebar-section-title">Overview & Tools</span>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <button
          className="theme-toggle-btn-sidebar"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? (
            <>
              <Sun size={16} /> <span>Light Mode</span>
            </>
          ) : (
            <>
              <Moon size={16} /> <span>Dark Mode</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
};
