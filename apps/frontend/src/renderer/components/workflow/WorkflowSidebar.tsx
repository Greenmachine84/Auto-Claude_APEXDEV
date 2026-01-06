/**
 * APEX Development Platform - Workflow Sidebar
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import type { WorkflowNode } from './types';
import type { NodeType } from './WorkflowView';

/** Node templates */
const nodeTemplates: { type: NodeType; icon: string; label: string }[] = [
  { type: 'task', icon: '📝', label: 'Task' },
  { type: 'condition', icon: '🔀', label: 'Condition' },
  { type: 'parallel', icon: '≡', label: 'Parallel' },
  { type: 'agent', icon: '🤖', label: 'Agent' },
];

/** Sidebar props */
export interface WorkflowSidebarProps {
  selectedNode: WorkflowNode | null;
  onAddNode: (type: NodeType, position: { x: number; y: number }) => void;
  onUpdateNode: (nodeId: string, updates: Partial<WorkflowNode>) => void;
  onDeleteNode: (nodeId: string) => void;
}

/**
 * Workflow Sidebar Component
 */
export const WorkflowSidebar: React.FC<WorkflowSidebarProps> = ({
  selectedNode,
  onAddNode,
  onUpdateNode,
  onDeleteNode,
}) => {
  return (
    <div className="apex-workflow-sidebar">
      {/* Node Palette */}
      <div className="apex-workflow-sidebar__section">
        <h4>Add Node</h4>
        <div className="apex-workflow-sidebar__palette">
          {nodeTemplates.map(({ type, icon, label }) => (
            <button
              key={type}
              className="apex-workflow-sidebar__node-btn"
              onClick={() => onAddNode(type, { x: 300, y: 200 })}
            >
              <span>{icon}</span>
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Node Properties */}
      {selectedNode && (
        <div className="apex-workflow-sidebar__section">
          <h4>Node Properties</h4>
          <div className="apex-workflow-sidebar__properties">
            <Input
              label="Label"
              value={selectedNode.label}
              onChange={(e) =>
                onUpdateNode(selectedNode.id, { label: e.target.value })
              }
            />
            <div className="apex-workflow-sidebar__field">
              <label>Type</label>
              <span className="apex-workflow-sidebar__type">
                {selectedNode.type}
              </span>
            </div>
            <div className="apex-workflow-sidebar__field">
              <label>Position</label>
              <span>
                X: {Math.round(selectedNode.position.x)}, Y:{' '}
                {Math.round(selectedNode.position.y)}
              </span>
            </div>
            {selectedNode.type !== 'start' && selectedNode.type !== 'end' && (
              <Button
                variant="danger"
                fullWidth
                onClick={() => onDeleteNode(selectedNode.id)}
              >
                🗑️ Delete Node
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Help */}
      <div className="apex-workflow-sidebar__section apex-workflow-sidebar__help">
        <h4>Quick Tips</h4>
        <ul>
          <li>Drag nodes to reposition</li>
          <li>Drag from output to input to connect</li>
          <li>Click nodes/edges to select</li>
          <li>Pan canvas by dragging background</li>
        </ul>
      </div>
    </div>
  );
};
