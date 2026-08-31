import { useEffect, useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { fetchHealth } from './services/api';
import { DashboardView } from './views/DashboardView';
import { TransactionsView } from './views/TransactionsView';
import { ReviewsView } from './views/ReviewsView';
import { EvaluationView } from './views/EvaluationView';
import { AuditView } from './views/AuditView';
import { SettingsView } from './views/SettingsView';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('ai_risk_manager_theme') as 'dark' | 'light') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ai_risk_manager_theme', theme);
  }, [theme]);

  useEffect(() => {
    fetchHealth().then((ok) => setIsConnected(ok));
    const interval = setInterval(() => {
      fetchHealth().then((ok) => setIsConnected(ok));
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return (
    <div className="app-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isBackendConnected={isConnected}
        theme={theme}
        toggleTheme={toggleTheme}
      />

      <main className="main-content">
        {activeTab === 'dashboard' && <DashboardView onNavigateTab={setActiveTab} />}
        {activeTab === 'transactions' && <TransactionsView />}
        {activeTab === 'reviews' && <ReviewsView />}
        {activeTab === 'evaluation' && <EvaluationView />}
        {activeTab === 'audit' && <AuditView />}
        {activeTab === 'settings' && <SettingsView initialSandbox={false} />}
      </main>
    </div>
  );
}

export default App;
