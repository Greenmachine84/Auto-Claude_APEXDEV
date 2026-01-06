/**
 * APEX Development Platform - Main Application
 * Phase 4: UI, Integrations & Analytics
 *
 * Root React component with routing and providers.
 */

import React, { useEffect, useState, Suspense } from 'react';
import { useAppStore } from './store';
import { ThemeProvider } from './components/common/ThemeProvider';
import { Sidebar } from './components/common/Sidebar';
import { TopBar } from './components/common/TopBar';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { NotificationToast } from './components/common/NotificationToast';

// Lazy load route components
const KanbanView = React.lazy(() => import('./components/kanban/KanbanView'));
const TerminalView = React.lazy(() => import('./components/terminal/TerminalView'));
const AgentView = React.lazy(() => import('./components/agents/AgentView'));
const MemoryView = React.lazy(() => import('./components/memory/MemoryView'));
const WorkflowView = React.lazy(() => import('./components/workflow/WorkflowView'));
const SettingsView = React.lazy(() => import('./components/settings/SettingsView'));
const AnalyticsView = React.lazy(() => import('./components/analytics/AnalyticsView'));

/** View types */
export type ViewType =
  | 'kanban'
  | 'terminal'
  | 'agents'
  | 'memory'
  | 'workflow'
  | 'settings'
  | 'analytics';

/**
 * Main Application Component
 */
const App: React.FC = () => {
  const { settings, currentView, setCurrentView, initialize, isInitialized } = useAppStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [terminalOpen, setTerminalOpen] = useState(false);

  // Initialize app on mount
  useEffect(() => {
    initialize();

    // Subscribe to menu events
    const unsubscribers = [
      window.apex.events.on('menu:toggle-sidebar', () => setSidebarOpen((prev) => !prev)),
      window.apex.events.on('menu:toggle-terminal', () => setTerminalOpen((prev) => !prev)),
      window.apex.events.on('menu:new-task', () => setCurrentView('kanban')),
    ];

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [initialize, setCurrentView]);

  // Render current view
  const renderView = () => {
    switch (currentView) {
      case 'kanban':
        return <KanbanView />;
      case 'terminal':
        return <TerminalView />;
      case 'agents':
        return <AgentView />;
      case 'memory':
        return <MemoryView />;
      case 'workflow':
        return <WorkflowView />;
      case 'settings':
        return <SettingsView />;
      case 'analytics':
        return <AnalyticsView />;
      default:
        return <KanbanView />;
    }
  };

  // Show loading while initializing
  if (!isInitialized) {
    return (
      <div className="app-loading">
        <LoadingSpinner size="large" />
        <span>Initializing APEX...</span>
      </div>
    );
  }

  return (
    <ThemeProvider theme={settings.ui.theme}>
      <ErrorBoundary>
        <div className={`app-container ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          {/* Sidebar */}
          <Sidebar
            isOpen={sidebarOpen}
            currentView={currentView}
            onViewChange={setCurrentView}
            onToggle={() => setSidebarOpen(!sidebarOpen)}
          />

          {/* Main Content */}
          <main className="main-content">
            {/* Top Bar */}
            <TopBar
              currentView={currentView}
              onMenuClick={() => setSidebarOpen(!sidebarOpen)}
              onSettingsClick={() => setCurrentView('settings')}
            />

            {/* View Content */}
            <div className="view-container">
              <Suspense fallback={<LoadingSpinner />}>{renderView()}</Suspense>
            </div>

            {/* Terminal Panel */}
            {terminalOpen && (
              <div
                className="terminal-panel"
                style={{ height: settings.ui.terminalHeight }}
              >
                <Suspense fallback={<LoadingSpinner size="small" />}>
                  <TerminalView embedded />
                </Suspense>
              </div>
            )}
          </main>

          {/* Notifications */}
          <NotificationToast />
        </div>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App;
