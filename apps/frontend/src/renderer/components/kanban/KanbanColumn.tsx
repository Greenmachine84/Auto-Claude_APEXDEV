/**
 * APEX Development Platform - Kanban Column
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { KanbanCard } from './KanbanCard';
import type { Task, TaskStatus } from '../../../preload/api/task-api';

/** Kanban column props */
export interface KanbanColumnProps {
  id: TaskStatus;
  title: string;
  color: string;
  tasks: Task[];
  isDragOver?: boolean;
  onTaskClick: (task: Task) => void;
  onDragStart: (taskId: string) => void;
  onDragOver: () => void;
  onDrop: () => void;
  onDragEnd: () => void;
}

/**
 * Kanban Column Component
 */
export const KanbanColumn: React.FC<KanbanColumnProps> = ({
  id,
  title,
  color,
  tasks,
  isDragOver,
  onTaskClick,
  onDragStart,
  onDragOver,
  onDrop,
  onDragEnd,
}) => {
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    onDragOver();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    onDrop();
  };

  return (
    <div
      className={`apex-kanban-column ${isDragOver ? 'apex-kanban-column--drag-over' : ''}`}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Column Header */}
      <div className="apex-kanban-column__header">
        <div className="apex-kanban-column__header-left">
          <span
            className="apex-kanban-column__indicator"
            style={{ backgroundColor: color }}
          />
          <h3 className="apex-kanban-column__title">{title}</h3>
          <span className="apex-kanban-column__count">{tasks.length}</span>
        </div>
      </div>

      {/* Task List */}
      <div className="apex-kanban-column__content">
        {tasks.length === 0 ? (
          <div className="apex-kanban-column__empty">
            <p>No tasks</p>
          </div>
        ) : (
          tasks.map((task) => (
            <KanbanCard
              key={task.id}
              task={task}
              onClick={() => onTaskClick(task)}
              onDragStart={() => onDragStart(task.id)}
              onDragEnd={onDragEnd}
            />
          ))
        )}
      </div>
    </div>
  );
};
