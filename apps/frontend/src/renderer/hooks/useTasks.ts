/**
 * APEX Development Platform - useTasks Hook
 * Phase 4: UI, Integrations & Analytics
 */

import { useState, useEffect, useCallback } from 'react';
import type { Task, TaskFilter, TaskUpdate, CreateTaskInput } from '../../preload/api/task-api';

/** Tasks hook return type */
export interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: Error | null;
  // CRUD operations
  createTask: (input: CreateTaskInput) => Promise<Task>;
  updateTask: (id: string, updates: TaskUpdate) => Promise<Task>;
  deleteTask: (id: string) => Promise<void>;
  // Filters
  filter: TaskFilter;
  setFilter: (filter: TaskFilter) => void;
  // Actions
  refresh: () => Promise<void>;
  getById: (id: string) => Task | undefined;
}

/**
 * Tasks Hook - Manage task state and operations
 */
export function useTasks(initialFilter?: TaskFilter): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [filter, setFilter] = useState<TaskFilter>(initialFilter || {});

  // Load tasks
  const loadTasks = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await window.apex.tasks.list(filter);
      setTasks(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load tasks'));
    } finally {
      setLoading(false);
    }
  }, [filter]);

  // Initial load and filter changes
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  // Subscribe to task events
  useEffect(() => {
    const unsubscribeCreated = window.apex.tasks.onCreated((task) => {
      setTasks((prev) => [...prev, task]);
    });

    const unsubscribeUpdated = window.apex.tasks.onUpdated((task) => {
      setTasks((prev) => prev.map((t) => (t.id === task.id ? task : t)));
    });

    const unsubscribeDeleted = window.apex.tasks.onDeleted((taskId) => {
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    });

    return () => {
      unsubscribeCreated();
      unsubscribeUpdated();
      unsubscribeDeleted();
    };
  }, []);

  // Create task
  const createTask = useCallback(async (input: CreateTaskInput): Promise<Task> => {
    const task = await window.apex.tasks.create(input);
    return task;
  }, []);

  // Update task
  const updateTask = useCallback(async (id: string, updates: TaskUpdate): Promise<Task> => {
    const task = await window.apex.tasks.update(id, updates);
    return task;
  }, []);

  // Delete task
  const deleteTask = useCallback(async (id: string): Promise<void> => {
    await window.apex.tasks.delete(id);
  }, []);

  // Get task by ID
  const getById = useCallback(
    (id: string): Task | undefined => {
      return tasks.find((t) => t.id === id);
    },
    [tasks]
  );

  return {
    tasks,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
    filter,
    setFilter,
    refresh: loadTasks,
    getById,
  };
}
