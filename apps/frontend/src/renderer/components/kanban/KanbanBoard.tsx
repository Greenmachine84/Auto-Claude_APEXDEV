/**
 * APEX Development Platform - Kanban Board
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useCallback } from 'react';
import { KanbanColumn } from './KanbanColumn';
import { LoadingSpinner } from '../common/LoadingSpinner';
import type { Task, TaskStatus } from '../../../preload/api/task-api';

/** Column configuration */
interface ColumnConfig {
  id: TaskStatus;
  title: string;
  color: string;
}

/** Column configurations */
const columns: ColumnConfig[] = [
  { id: 'pending', title: 'To Do', color: '#6b7280' },
  { id: 'running', title: 'In Progress', color: '#3b82f6' },
  { id: 'completed', title: 'Done', color: '#22c55e' },
  { id: 'failed', title: 'Failed', color: '#ef4444' },
];

/** Kanban board props */
export interface KanbanBoardProps {
  groupedTasks: Record<TaskStatus, Task[]>;
  loading?: boolean;
  onTaskClick: (task: Task) => void;
  onTaskMove: (taskId: string, newStatus: TaskStatus) => void;
}

/**
 * Kanban Board Component
 */
export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  groupedTasks,
  loading,
  onTaskClick,
  onTaskMove,
}) => {
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<TaskStatus | null>(null);

  // Handle drag start
  const handleDragStart = useCallback((taskId: string) => {
    setDraggedTaskId(taskId);
  }, []);

  // Handle drag over
  const handleDragOver = useCallback((status: TaskStatus) => {
    setDragOverColumn(status);
  }, []);

  // Handle drop
  const handleDrop = useCallback(
    (status: TaskStatus) => {
      if (draggedTaskId) {
        onTaskMove(draggedTaskId, status);
        setDraggedTaskId(null);
        setDragOverColumn(null);
      }
    },
    [draggedTaskId, onTaskMove]
  );

  // Handle drag end
  const handleDragEnd = useCallback(() => {
    setDraggedTaskId(null);
    setDragOverColumn(null);
  }, []);

  if (loading) {
    return (
      <div className="apex-kanban-board apex-kanban-board--loading">
        <LoadingSpinner label="Loading tasks..." />
      </div>
    );
  }

  return (
    <div className="apex-kanban-board">
      {columns.map((column) => (
        <KanbanColumn
          key={column.id}
          id={column.id}
          title={column.title}
          color={column.color}
          tasks={groupedTasks[column.id] || []}
          isDragOver={dragOverColumn === column.id}
          onTaskClick={onTaskClick}
          onDragStart={handleDragStart}
          onDragOver={() => handleDragOver(column.id)}
          onDrop={() => handleDrop(column.id)}
          onDragEnd={handleDragEnd}
        />
      ))}
    </div>
  );
};
