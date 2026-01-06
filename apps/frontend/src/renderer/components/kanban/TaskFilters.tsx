/**
 * APEX Development Platform - Task Filters
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Input } from '../common/Input';
import { Select, type SelectOption } from '../common/Select';
import type { TaskFilter, TaskPriority, TaskStatus } from '../../../preload/api/task-api';

/** Task filters props */
export interface TaskFiltersProps {
  filters: TaskFilter;
  onFiltersChange: (filters: TaskFilter) => void;
}

/** Status filter options */
const statusOptions: SelectOption<TaskStatus | ''>[] = [
  { value: '', label: 'All Statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'running', label: 'Running' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
];

/** Priority filter options */
const priorityOptions: SelectOption<TaskPriority | ''>[] = [
  { value: '', label: 'All Priorities' },
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

/**
 * Task Filters Component
 */
export const TaskFilters: React.FC<TaskFiltersProps> = ({ filters, onFiltersChange }) => {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, search: e.target.value || undefined });
  };

  const handleStatusChange = (status: TaskStatus | '') => {
    onFiltersChange({ ...filters, status: status || undefined });
  };

  const handlePriorityChange = (priority: TaskPriority | '') => {
    onFiltersChange({ ...filters, priority: priority || undefined });
  };

  const handleClearFilters = () => {
    onFiltersChange({});
  };

  const hasFilters = filters.search || filters.status || filters.priority;

  return (
    <div className="apex-task-filters">
      <Input
        placeholder="Search tasks..."
        value={filters.search || ''}
        onChange={handleSearchChange}
        leftIcon="🔍"
        size="small"
      />

      <Select
        options={statusOptions}
        value={(filters.status as TaskStatus) || ''}
        onChange={handleStatusChange}
        placeholder="Status"
        size="small"
      />

      <Select
        options={priorityOptions}
        value={(filters.priority as TaskPriority) || ''}
        onChange={handlePriorityChange}
        placeholder="Priority"
        size="small"
      />

      {hasFilters && (
        <button
          className="apex-task-filters__clear"
          onClick={handleClearFilters}
          title="Clear filters"
        >
          Clear
        </button>
      )}
    </div>
  );
};
