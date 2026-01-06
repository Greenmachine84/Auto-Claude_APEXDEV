/**
 * APEX Development Platform - Task Form
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect } from 'react';
import { Input } from '../common/Input';
import { Select, type SelectOption } from '../common/Select';
import type { Task, TaskPriority, TaskStatus } from '../../../preload/api/task-api';
import type { AgentType } from '../../../preload/api/agent-api';

/** Task form props */
export interface TaskFormProps {
  task: Task | null;
  onSubmit: (data: Partial<Task>) => void;
}

/** Priority options */
const priorityOptions: SelectOption<TaskPriority>[] = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'critical', label: 'Critical' },
];

/** Status options */
const statusOptions: SelectOption<TaskStatus>[] = [
  { value: 'pending', label: 'Pending' },
  { value: 'running', label: 'Running' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
];

/** Agent type options */
const agentOptions: SelectOption<AgentType | ''>[] = [
  { value: '', label: 'None' },
  { value: 'coder', label: '💻 Coder' },
  { value: 'reviewer', label: '🔍 Reviewer' },
  { value: 'fixer', label: '🛠️ Fixer' },
  { value: 'planner', label: '📝 Planner' },
  { value: 'analyst', label: '📊 Analyst' },
];

/**
 * Task Form Component
 */
export const TaskForm: React.FC<TaskFormProps> = ({ task, onSubmit }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [status, setStatus] = useState<TaskStatus>('pending');
  const [agentType, setAgentType] = useState<AgentType | ''>('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Initialize form with task data
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || '');
      setPriority(task.priority);
      setStatus(task.status);
      setAgentType((task.agentType as AgentType) || '');
    } else {
      setTitle('');
      setDescription('');
      setPriority('medium');
      setStatus('pending');
      setAgentType('');
    }
    setErrors({});
  }, [task]);

  // Validate form
  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length > 200) {
      newErrors.title = 'Title must be less than 200 characters';
    }

    if (description.length > 2000) {
      newErrors.description = 'Description must be less than 2000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle submit
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      priority,
      status: task ? status : 'pending',
      agentType: agentType || undefined,
    });
  };

  return (
    <form id="task-form" className="apex-task-form" onSubmit={handleSubmit}>
      <Input
        label="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        error={errors.title}
        placeholder="Task title"
        required
        fullWidth
      />

      <div className="apex-task-form__textarea">
        <label htmlFor="description" className="apex-input__label">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional task description"
          rows={4}
          className={`apex-input ${errors.description ? 'apex-input--error' : ''}`}
        />
        {errors.description && (
          <span className="apex-input__error">{errors.description}</span>
        )}
      </div>

      <div className="apex-task-form__row">
        <Select
          label="Priority"
          options={priorityOptions}
          value={priority}
          onChange={(val) => setPriority(val as TaskPriority)}
          fullWidth
        />

        {task && (
          <Select
            label="Status"
            options={statusOptions}
            value={status}
            onChange={(val) => setStatus(val as TaskStatus)}
            fullWidth
          />
        )}
      </div>

      <Select
        label="Assign Agent"
        options={agentOptions}
        value={agentType}
        onChange={(val) => setAgentType(val as AgentType | '')}
        clearable
        fullWidth
      />
    </form>
  );
};
