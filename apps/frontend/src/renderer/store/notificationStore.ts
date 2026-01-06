/**
 * APEX Development Platform - Notification Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

/** Notification type */
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

/** Notification item */
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message?: string;
  duration?: number;
  dismissible?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: number;
}

/** Notification state */
export interface NotificationState {
  notifications: Notification[];
  maxNotifications: number;
}

/** Notification actions */
export interface NotificationActions {
  // Add notifications
  addNotification: (notification: Omit<Notification, 'id' | 'createdAt'>) => string;
  info: (title: string, message?: string) => string;
  success: (title: string, message?: string) => string;
  warning: (title: string, message?: string) => string;
  error: (title: string, message?: string) => string;

  // Remove notifications
  removeNotification: (id: string) => void;
  clearAll: () => void;

  // Settings
  setMaxNotifications: (max: number) => void;
}

/** Generate notification ID */
const generateId = () => `notif-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

/**
 * Notification Store - Toast notifications state
 */
export const useNotificationStore = create<NotificationState & NotificationActions>()(
  devtools(
    (set, get) => ({
      // Initial state
      notifications: [],
      maxNotifications: 5,

      // Add notification
      addNotification: (notification) => {
        const id = generateId();
        const newNotification: Notification = {
          ...notification,
          id,
          createdAt: Date.now(),
          duration: notification.duration ?? (notification.type === 'error' ? 0 : 5000),
          dismissible: notification.dismissible ?? true,
        };

        set((state) => {
          let notifications = [newNotification, ...state.notifications];
          
          // Trim to max
          if (notifications.length > state.maxNotifications) {
            notifications = notifications.slice(0, state.maxNotifications);
          }

          return { notifications };
        });

        // Auto-dismiss
        if (newNotification.duration && newNotification.duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, newNotification.duration);
        }

        return id;
      },

      // Shorthand methods
      info: (title, message) =>
        get().addNotification({ type: 'info', title, message }),

      success: (title, message) =>
        get().addNotification({ type: 'success', title, message }),

      warning: (title, message) =>
        get().addNotification({ type: 'warning', title, message }),

      error: (title, message) =>
        get().addNotification({ type: 'error', title, message, duration: 0 }),

      // Remove notification
      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),

      // Clear all
      clearAll: () => set({ notifications: [] }),

      // Set max notifications
      setMaxNotifications: (max) => set({ maxNotifications: max }),
    }),
    { name: 'NotificationStore' }
  )
);
