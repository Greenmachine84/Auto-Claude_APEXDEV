/**
 * APEX Development Platform - Notification Toast
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useEffect, useState, useCallback } from 'react';

/** Notification type */
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

/** Notification data */
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/** Toast icons */
const typeIcons: Record<NotificationType, string> = {
  info: 'ℹ️',
  success: '✅',
  warning: '⚠️',
  error: '❌',
};

/**
 * Notification Toast Component
 */
export const NotificationToast: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // Add notification
  const addNotification = useCallback((notification: Omit<Notification, 'id'>) => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setNotifications((prev) => [...prev, { ...notification, id }]);

    // Auto-dismiss after duration
    const duration = notification.duration ?? 5000;
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  }, []);

  // Remove notification
  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  // Subscribe to notification events
  useEffect(() => {
    const unsubscribers = [
      window.apex.events.on('notification:show', (data: Omit<Notification, 'id'>) => {
        addNotification(data);
      }),
      window.apex.events.on('notification:clear', () => {
        setNotifications([]);
      }),
    ];

    return () => {
      unsubscribers.forEach((unsub) => unsub());
    };
  }, [addNotification]);

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div className="apex-toast-container">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`apex-toast apex-toast--${notification.type}`}
          role="alert"
        >
          <span className="apex-toast__icon">{typeIcons[notification.type]}</span>
          <div className="apex-toast__content">
            <strong className="apex-toast__title">{notification.title}</strong>
            {notification.message && (
              <p className="apex-toast__message">{notification.message}</p>
            )}
          </div>
          {notification.action && (
            <button className="apex-toast__action" onClick={notification.action.onClick}>
              {notification.action.label}
            </button>
          )}
          <button
            className="apex-toast__close"
            onClick={() => removeNotification(notification.id)}
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};

// Export helper to trigger notifications
export const showNotification = (notification: Omit<Notification, 'id'>): void => {
  window.dispatchEvent(
    new CustomEvent('apex:notification', { detail: notification })
  );
};
