/**
 * APEX Development Platform - Kanban View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect, useCallback } from 'react';
import { KanbanBoard } from './KanbanBoard';
import { TaskModal } from './TaskModal';
import { TaskFilters } from './TaskFilters';
import { Button } from '../common/Button';
import { useTasks } from '../../hooks/useTasks';
import type { Task, TaskFilter, TaskStatus } from '../../../preload/api/task-api';

/**
 * Kanban View Component
 */
const KanbanView: React.FC = () => {
  const { tasks, loading, error, createTask, updateTask, deleteTask, refresh } = useTasks();
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [filters, setFilters] = useState<TaskFilter>({});

  // Group tasks by status
  const groupedTasks = React.useMemo(() => {
    const groups: Record<TaskStatus, Task[]> = {
      pending: [],
      running: [],
      'in-progress': [],
      completed: [],
      failed: [],
      cancelled: [],
    };

    tasks.forEach((task) => {
      if (groups[task.status]) {
        groups[task.status].push(task);
      }
    });

    return groups;
  }, [tasks]);

  // Handle task click
  const handleTaskClick = useCallback((task: Task) => {
    setSelectedTask(task);
    setIsModalOpen(true);
  }, []);

  // Handle new task
  const handleNewTask = useCallback(() => {
    setSelectedTask(null);
    setIsModalOpen(true);
  }, []);

  // Handle task save
  const handleTaskSave = useCallback(
    async (taskData: Partial<Task>) => {
      if (selectedTask) {
        await updateTask(selectedTask.id, taskData);
      } else {
        await createTask(taskData as Parameters<typeof createTask>[0]);
      }
      setIsModalOpen(false);
      setSelectedTask(null);
    },
    [selectedTask, createTask, updateTask]
  );

  // Handle task delete
  const handleTaskDelete = useCallback(
    async (taskId: string) => {
      await deleteTask(taskId);
      setIsModalOpen(false);
      setSelectedTask(null);
    },
    [deleteTask]
  );

  // Handle drag and drop
  const handleTaskMove = useCallback(
    async (taskId: string, newStatus: TaskStatus) => {
      await updateTask(taskId, { status: newStatus });
    },
    [updateTask]
  );

  // Subscribe to task updates
  useEffect(() => {
    const unsubscribe = window.apex.tasks.onTaskUpdate(() => {
      refresh();
    });
    return unsubscribe;
  }, [refresh]);

  if (error) {
    return (
      <div className="apex-kanban-error">
        <p>Error loading tasks: {error.message}</p>
        <Button onClick={refresh}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="apex-kanban-view">
      {/* Header */}
      <div className="apex-kanban-view__header">
        <TaskFilters filters={filters} onFiltersChange={setFilters} />
        <Button variant="primary" onClick={handleNewTask}>
          + New Task
        </Button>
      </div>

      {/* Board */}
      <KanbanBoard
        groupedTasks={groupedTasks}
        loading={loading}
        onTaskClick={handleTaskClick}
        onTaskMove={handleTaskMove}
      />

      {/* Task Modal */}
      <TaskModal
        isOpen={isModalOpen}
        task={selectedTask}
        onClose={() => setIsModalOpen(false)}
        onSave={handleTaskSave}
        onDelete={handleTaskDelete}
      />
    </div>
  );
};

export default KanbanView;
