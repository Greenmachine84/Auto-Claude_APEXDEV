/**
 * APEX Development Platform - Task Modal
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { TaskForm } from './TaskForm';
import type { Task } from '../../../preload/api/task-api';

/** Task modal props */
export interface TaskModalProps {
  isOpen: boolean;
  task: Task | null;
  onClose: () => void;
  onSave: (task: Partial<Task>) => Promise<void>;
  onDelete: (taskId: string) => Promise<void>;
}

/**
 * Task Modal Component
 */
export const TaskModal: React.FC<TaskModalProps> = ({
  isOpen,
  task,
  onClose,
  onSave,
  onDelete,
}) => {
  const [loading, setLoading] = React.useState(false);

  const handleSave = async (data: Partial<Task>) => {
    setLoading(true);
    try {
      await onSave(data);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (task && window.confirm('Are you sure you want to delete this task?')) {
      setLoading(true);
      try {
        await onDelete(task.id);
      } finally {
        setLoading(false);
      }
    }
  };

  const footer = (
    <div className="apex-task-modal__footer">
      <div className="apex-task-modal__footer-left">
        {task && (
          <Button variant="danger" onClick={handleDelete} disabled={loading}>
            Delete
          </Button>
        )}
      </div>
      <div className="apex-task-modal__footer-right">
        <Button variant="ghost" onClick={onClose} disabled={loading}>
          Cancel
        </Button>
        <Button
          variant="primary"
          type="submit"
          form="task-form"
          loading={loading}
        >
          {task ? 'Update' : 'Create'}
        </Button>
      </div>
    </div>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={task ? 'Edit Task' : 'New Task'}
      size="medium"
      footer={footer}
    >
      <TaskForm task={task} onSubmit={handleSave} />
    </Modal>
  );
};
