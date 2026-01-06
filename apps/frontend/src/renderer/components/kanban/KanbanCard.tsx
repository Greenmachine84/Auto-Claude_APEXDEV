/**
 * APEX Development Platform - Kanban Card
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { Task } from '../../../preload/api/task-api';

/** Priority colors */
const priorityColors: Record<string, string> = {
  low: '#6b7280',
  medium: '#f59e0b',
  high: '#f97316',
  critical: '#ef4444',
};

/** Priority labels */
const priorityLabels: Record<string, string> = {
  low: 'Low',
  medium: 'Med',
  high: 'High',
  critical: 'Crit',
};

/** Agent type icons */
const agentIcons: Record<string, string> = {
  coder: '💻',
  reviewer: '🔍',
  fixer: '🛠️',
  planner: '📝',
  analyst: '📊',
};

/** Kanban card props */
export interface KanbanCardProps {
  task: Task;
  onClick: () => void;
  onDragStart: () => void;
  onDragEnd: () => void;
}

/**
 * Kanban Card Component
 */
export const KanbanCard: React.FC<KanbanCardProps> = ({
  task,
  onClick,
  onDragStart,
  onDragEnd,
}) => {
  const handleDragStart = (e: React.DragEvent) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', task.id);
    onDragStart();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div
      className="apex-kanban-card"
      draggable
      onClick={onClick}
      onDragStart={handleDragStart}
      onDragEnd={onDragEnd}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}
    >
      {/* Card Header */}
      <div className="apex-kanban-card__header">
        <span
          className="apex-kanban-card__priority"
          style={{ backgroundColor: priorityColors[task.priority] }}
          title={`Priority: ${task.priority}`}
        >
          {priorityLabels[task.priority]}
        </span>
        {task.agentType && (
          <span className="apex-kanban-card__agent" title={`Agent: ${task.agentType}`}>
            {agentIcons[task.agentType] || '🤖'}
          </span>
        )}
      </div>

      {/* Card Title */}
      <h4 className="apex-kanban-card__title">{task.title}</h4>

      {/* Card Description */}
      {task.description && (
        <p className="apex-kanban-card__description">{task.description}</p>
      )}

      {/* Card Footer */}
      <div className="apex-kanban-card__footer">
        <span className="apex-kanban-card__date" title="Created">
          {formatDate(task.createdAt)}
        </span>
        {task.error && (
          <span className="apex-kanban-card__error" title={task.error}>
            ⚠️
          </span>
        )}
      </div>
    </div>
  );
};
