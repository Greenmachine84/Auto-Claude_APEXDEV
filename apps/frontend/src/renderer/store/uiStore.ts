/**
 * APEX Development Platform - UI Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

/** Sidebar state */
type SidebarView = 'tasks' | 'agents' | 'memory' | 'workflow' | 'settings' | 'analytics';

/** Modal types */
type ModalType = 'task' | 'agent' | 'settings' | 'confirm' | 'custom' | null;

/** UI state */
export interface UIState {
  // Sidebar
  sidebarOpen: boolean;
  sidebarView: SidebarView;
  sidebarWidth: number;

  // Modals
  activeModal: ModalType;
  modalData: unknown;

  // Panels
  terminalOpen: boolean;
  terminalHeight: number;
  detailPanelOpen: boolean;
  detailPanelWidth: number;

  // Command palette
  commandPaletteOpen: boolean;

  // Fullscreen
  fullscreen: boolean;

  // Focus mode
  focusMode: boolean;
}

/** UI actions */
export interface UIActions {
  // Sidebar
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setSidebarView: (view: SidebarView) => void;
  setSidebarWidth: (width: number) => void;

  // Modals
  openModal: (type: ModalType, data?: unknown) => void;
  closeModal: () => void;

  // Panels
  toggleTerminal: () => void;
  setTerminalOpen: (open: boolean) => void;
  setTerminalHeight: (height: number) => void;
  toggleDetailPanel: () => void;
  setDetailPanelOpen: (open: boolean) => void;
  setDetailPanelWidth: (width: number) => void;

  // Command palette
  toggleCommandPalette: () => void;
  setCommandPaletteOpen: (open: boolean) => void;

  // Fullscreen
  toggleFullscreen: () => void;
  setFullscreen: (fullscreen: boolean) => void;

  // Focus mode
  toggleFocusMode: () => void;
  setFocusMode: (focusMode: boolean) => void;

  // Reset
  resetLayout: () => void;
}

/** Default state */
const defaultState: UIState = {
  sidebarOpen: true,
  sidebarView: 'tasks',
  sidebarWidth: 280,
  activeModal: null,
  modalData: null,
  terminalOpen: false,
  terminalHeight: 200,
  detailPanelOpen: false,
  detailPanelWidth: 400,
  commandPaletteOpen: false,
  fullscreen: false,
  focusMode: false,
};

/**
 * UI Store - UI layout and state
 */
export const useUIStore = create<UIState & UIActions>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        ...defaultState,

        // Sidebar
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
        setSidebarView: (view) => set({ sidebarView: view, sidebarOpen: true }),
        setSidebarWidth: (width) => set({ sidebarWidth: Math.max(200, Math.min(500, width)) }),

        // Modals
        openModal: (type, data) => set({ activeModal: type, modalData: data }),
        closeModal: () => set({ activeModal: null, modalData: null }),

        // Terminal
        toggleTerminal: () => set((state) => ({ terminalOpen: !state.terminalOpen })),
        setTerminalOpen: (open) => set({ terminalOpen: open }),
        setTerminalHeight: (height) => set({ terminalHeight: Math.max(100, Math.min(600, height)) }),

        // Detail panel
        toggleDetailPanel: () => set((state) => ({ detailPanelOpen: !state.detailPanelOpen })),
        setDetailPanelOpen: (open) => set({ detailPanelOpen: open }),
        setDetailPanelWidth: (width) => set({ detailPanelWidth: Math.max(300, Math.min(800, width)) }),

        // Command palette
        toggleCommandPalette: () => set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
        setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),

        // Fullscreen
        toggleFullscreen: () =>
          set((state) => {
            const newFullscreen = !state.fullscreen;
            if (newFullscreen) {
              document.documentElement.requestFullscreen?.();
            } else {
              document.exitFullscreen?.();
            }
            return { fullscreen: newFullscreen };
          }),
        setFullscreen: (fullscreen) => set({ fullscreen }),

        // Focus mode
        toggleFocusMode: () =>
          set((state) => ({
            focusMode: !state.focusMode,
            sidebarOpen: state.focusMode, // Restore sidebar when exiting
            terminalOpen: false,
            detailPanelOpen: false,
          })),
        setFocusMode: (focusMode) =>
          set({
            focusMode,
            sidebarOpen: !focusMode,
            terminalOpen: false,
            detailPanelOpen: false,
          }),

        // Reset layout
        resetLayout: () => set(defaultState),
      }),
      {
        name: 'apex-ui-store',
        partialize: (state) => ({
          sidebarOpen: state.sidebarOpen,
          sidebarView: state.sidebarView,
          sidebarWidth: state.sidebarWidth,
          terminalHeight: state.terminalHeight,
          detailPanelWidth: state.detailPanelWidth,
        }),
      }
    ),
    { name: 'UIStore' }
  )
);
