/**
 * APEX Development Platform - Workflow Toolbar
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Button } from '../common/Button';
import type { Workflow } from './WorkflowView';

/** Toolbar props */
export interface WorkflowToolbarProps {
  workflow: Workflow;
  zoom: number;
  isEditing: boolean;
  onZoomChange: (zoom: number) => void;
  onToggleEdit: () => void;
  onSave: () => void;
}

/**
 * Workflow Toolbar Component
 */
export const WorkflowToolbar: React.FC<WorkflowToolbarProps> = ({
  workflow,
  zoom,
  isEditing,
  onZoomChange,
  onToggleEdit,
  onSave,
}) => {
  return (
    <div className="apex-workflow-toolbar">
      {/* Left: Info */}
      <div className="apex-workflow-toolbar__info">
        <h3>{workflow.name}</h3>
        <span className="apex-workflow-toolbar__stats">
          {workflow.nodes.length} nodes • {workflow.edges.length} edges
        </span>
      </div>

      {/* Center: Zoom */}
      <div className="apex-workflow-toolbar__zoom">
        <button
          onClick={() => onZoomChange(Math.max(0.25, zoom - 0.25))}
          disabled={zoom <= 0.25}
        >
          −
        </button>
        <span>{Math.round(zoom * 100)}%</span>
        <button
          onClick={() => onZoomChange(Math.min(2, zoom + 0.25))}
          disabled={zoom >= 2}
        >
          +
        </button>
        <button onClick={() => onZoomChange(1)}>Reset</button>
      </div>

      {/* Right: Actions */}
      <div className="apex-workflow-toolbar__actions">
        <Button
          variant={isEditing ? 'primary' : 'ghost'}
          onClick={onToggleEdit}
        >
          {isEditing ? '🔒 Lock' : '✏️ Edit'}
        </Button>
        {isEditing && (
          <Button variant="primary" onClick={onSave}>
            💾 Save
          </Button>
        )}
      </div>
    </div>
  );
};
