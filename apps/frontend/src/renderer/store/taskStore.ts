/**
 * APEX Development Platform - Task Store
 * Phase 4: UI, Integrations & Analytics
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { Task, TaskFilter, TaskUpdate, CreateTaskInput, TaskStatus } from '../../preload/api/task-api';

/** Task state */
export interface TaskState {
  tasks: Task[];
  selectedTaskId: string | null;
  filter: TaskFilter;
  loading: boolean;
  error: Error | null;
}

/** Task actions */
export interface TaskActions {
  // CRUD
  loadTasks: (filter?: TaskFilter) => Promise<void>;
  createTask: (input: CreateTaskInput) => Promise<Task>;
  updateTask: (id: string, updates: TaskUpdate) => Promise<Task>;
  deleteTask: (id: string) => Promise<void>;

  // Selection
  selectTask: (id: string | null) => void;
  getSelectedTask: () => Task | undefined;

  // Filtering
  setFilter: (filter: TaskFilter) => void;
  clearFilter: () => void;

  // Bulk operations
  updateTaskStatus: (id: string, status: TaskStatus) => Promise<void>;
  bulkUpdateStatus: (ids: string[], status: TaskStatus) => Promise<void>;
  bulkDelete: (ids: string[]) => Promise<void>;

  // Events
  handleTaskCreated: (task: Task) => void;
  handleTaskUpdated: (task: Task) => void;
  handleTaskDeleted: (taskId: string) => void;
}

/**
 * Task Store - Task management state
 */
export const useTaskStore = create<TaskState & TaskActions>()(
  devtools(
    (set, get) => ({
      // Initial state
      tasks: [],
      selectedTaskId: null,
      filter: {},
      loading: false,
      error: null,

      // Load tasks
      loadTasks: async (filter) => {
        const taskFilter = filter || get().filter;
        set({ loading: true, error: null, filter: taskFilter });
        try {
          const tasks = await window.apex.tasks.list(taskFilter);
          set({ tasks: tasks as Task[], loading: false });
        } catch (error) {
          set({
            loading: false,
            error: error instanceof Error ? error : new Error('Failed to load tasks'),
          });
        }
      },

      // Create task
      createTask: async (input) => {
        const task = await window.apex.tasks.create(input);
        set((state) => ({ tasks: [...state.tasks, task as Task] }));
        return task;
      },

      // Update task
      updateTask: async (id, updates) => {
        const task = await window.apex.tasks.update(id, updates);
        set((state) => ({ tasks: state.tasks.map((t) => (t.id === id ? task as Task : t)) }));
        return task;
      },

      // Delete task
      deleteTask: async (id) => {
        await window.apex.tasks.delete(id);
        set((state) => ({
          tasks: state.tasks.filter((t) => t.id !== id),
          selectedTaskId: state.selectedTaskId === id ? null : state.selectedTaskId,
        }));
      },

      // Select task
      selectTask: (id) => set({ selectedTaskId: id }),

      // Get selected task
      getSelectedTask: () => {
        const { tasks, selectedTaskId } = get();
        return tasks.find((t) => t.id === selectedTaskId);
      },

      // Set filter
      setFilter: (filter) => {
        set({ filter });
        get().loadTasks(filter);
      },

      // Clear filter
      clearFilter: () => {
        set({ filter: {} });
        get().loadTasks({});
      },

      // Update task status
      updateTaskStatus: async (id, status) => {
        await get().updateTask(id, { status });
      },

      // Bulk update status
      bulkUpdateStatus: async (ids, status) => {
        await Promise.all(ids.map((id) => get().updateTask(id, { status })));
      },

      // Bulk delete
      bulkDelete: async (ids) => {
        await Promise.all(ids.map((id) => get().deleteTask(id)));
      },

      // Handle task created event
      handleTaskCreated: (task) => {
        set((state) => {
          if (state.tasks.find((t) => t.id === task.id)) return state;
          return { tasks: [...state.tasks, task] };
        });
      },

      // Handle task updated event
      handleTaskUpdated: (task) => {
        set((state) => ({
          tasks: state.tasks.map((t) => (t.id === task.id ? task : t)),
        }));
      },

      // Handle task deleted event
      handleTaskDeleted: (taskId) => {
        set((state) => ({
          tasks: state.tasks.filter((t) => t.id !== taskId),
          selectedTaskId: state.selectedTaskId === taskId ? null : state.selectedTaskId,
        }));
      },
    }),
    { name: 'TaskStore' }
  )
);

