/**
 * APEX Development Platform - Notification Service
 * Phase 4: UI, Integrations & Analytics
 *
 * Handles native notifications and in-app alerts.
 */

import { Notification, BrowserWindow, nativeImage } from 'electron';
import * as path from 'path';
import { EventEmitter } from 'events';

/** Notification type */
export type NotificationType = 'info' | 'success' | 'warning' | 'error';

/** Notification options */
export interface NotificationOptions {
  title: string;
  body: string;
  type?: NotificationType;
  icon?: string;
  silent?: boolean;
  timeout?: number;
  actions?: { type: 'button'; text: string }[];
  onClick?: () => void;
  onClose?: () => void;
}

/** Notification record */
export interface NotificationRecord {
  id: string;
  title: string;
  body: string;
  type: NotificationType;
  createdAt: Date;
  read: boolean;
}

/**
 * Notification Service
 * Manages native and in-app notifications
 */
export class NotificationService extends EventEmitter {
  private static instance: NotificationService | null = null;
  private history: NotificationRecord[] = [];
  private maxHistory = 100;
  private notificationId = 0;

  private constructor() {
    super();
  }

  public static getInstance(): NotificationService {
    if (!NotificationService.instance) {
      NotificationService.instance = new NotificationService();
    }
    return NotificationService.instance;
  }

  /**
   * Show native notification
   */
  public show(options: NotificationOptions): string {
    const id = `notif_${++this.notificationId}`;
    const type = options.type || 'info';

    // Record notification
    const record: NotificationRecord = {
      id,
      title: options.title,
      body: options.body,
      type,
      createdAt: new Date(),
      read: false,
    };
    this.addToHistory(record);

    // Show native notification if supported
    if (Notification.isSupported()) {
      const notification = new Notification({
        title: options.title,
        body: options.body,
        silent: options.silent ?? false,
        icon: this.getIcon(type),
      });

      notification.on('click', () => {
        this.markAsRead(id);
        options.onClick?.();
        this.emit('click', id);
      });

      notification.on('close', () => {
        options.onClose?.();
        this.emit('close', id);
      });

      notification.show();

      // Auto-close after timeout
      if (options.timeout) {
        setTimeout(() => notification.close(), options.timeout);
      }
    }

    // Also send to renderer
    this.sendToRenderer(record);
    this.emit('show', record);

    return id;
  }

  /**
   * Show info notification
   */
  public info(title: string, body: string): string {
    return this.show({ title, body, type: 'info' });
  }

  /**
   * Show success notification
   */
  public success(title: string, body: string): string {
    return this.show({ title, body, type: 'success' });
  }

  /**
   * Show warning notification
   */
  public warning(title: string, body: string): string {
    return this.show({ title, body, type: 'warning' });
  }

  /**
   * Show error notification
   */
  public error(title: string, body: string): string {
    return this.show({ title, body, type: 'error' });
  }

  /**
   * Get notification history
   */
  public getHistory(limit?: number): NotificationRecord[] {
    const records = [...this.history].reverse();
    return limit ? records.slice(0, limit) : records;
  }

  /**
   * Get unread notifications
   */
  public getUnread(): NotificationRecord[] {
    return this.history.filter((n) => !n.read).reverse();
  }

  /**
   * Get unread count
   */
  public getUnreadCount(): number {
    return this.history.filter((n) => !n.read).length;
  }

  /**
   * Mark notification as read
   */
  public markAsRead(id: string): void {
    const notification = this.history.find((n) => n.id === id);
    if (notification) {
      notification.read = true;
      this.emit('read', id);
    }
  }

  /**
   * Mark all as read
   */
  public markAllAsRead(): void {
    this.history.forEach((n) => (n.read = true));
    this.emit('readAll');
  }

  /**
   * Clear notification history
   */
  public clearHistory(): void {
    this.history = [];
    this.emit('cleared');
  }

  private addToHistory(record: NotificationRecord): void {
    this.history.push(record);
    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }
  }

  private getIcon(type: NotificationType): string {
    const iconMap: Record<NotificationType, string> = {
      info: 'info.png',
      success: 'success.png',
      warning: 'warning.png',
      error: 'error.png',
    };
    return path.join(__dirname, '../../assets/icons', iconMap[type]);
  }

  private sendToRenderer(record: NotificationRecord): void {
    const windows = BrowserWindow.getAllWindows();
    windows.forEach((window) => {
      if (!window.isDestroyed()) {
        window.webContents.send('notification:new', record);
      }
    });
  }

  public static resetInstance(): void {
    NotificationService.instance = null;
  }
}
