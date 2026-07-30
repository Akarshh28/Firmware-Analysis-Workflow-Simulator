import { create } from 'zustand';

import { PageId } from '../components/Sidebar';

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
  isRead: boolean;
  timestamp: number;
  action?: {
    label: string;
    pageId: PageId;
  };
}

interface NotificationState {
  notifications: AppNotification[];
  addNotification: (notif: Omit<AppNotification, 'id' | 'timestamp' | 'isRead'>) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
  unreadCount: () => number;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  addNotification: (notif) => {
    const newNotif: AppNotification = {
      ...notif,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      isRead: false,
    };
    set((state) => ({
      notifications: [newNotif, ...state.notifications],
    }));
  },
  markAsRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, isRead: true } : n
      ),
    }));
  },
  markAllAsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, isRead: true })),
    }));
  },
  clearAll: () => {
    set({ notifications: [] });
  },
  unreadCount: () => {
    return get().notifications.filter((n) => !n.isRead).length;
  },
}));
