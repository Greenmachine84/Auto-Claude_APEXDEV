/**
 * APEX Development Platform - Renderer Entry
 * Phase 4: UI, Integrations & Analytics
 *
 * React application entry point.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/globals.css';

// Enable React strict mode in development
const StrictModeWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  if (process.env.NODE_ENV === 'development') {
    return <React.StrictMode>{children}</React.StrictMode>;
  }
  return <>{children}</>;
};

// Root element
const container = document.getElementById('root');
if (!container) {
  throw new Error('Root element not found');
}

// Create React root
const root = createRoot(container);

// Render application
root.render(
  <StrictModeWrapper>
    <App />
  </StrictModeWrapper>
);

// Hot module replacement for development
if (import.meta.hot) {
  import.meta.hot.accept();
}
