/**
 * APEX Development Platform - Workflow Node
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useRef, useCallback } from 'react';
import type { WorkflowNode as NodeType } from './types';

/** Node icons by type */
const nodeIcons: Record<string, string> = {
  start: '▶️',
  end: '⏹️',
  task: '📝',
  condition: '🔀',
  parallel: '≡',
  agent: '🤖',
};

/** Node colors by type */
const nodeColors: Record<string, string> = {
  start: '#22c55e',
  end: '#ef4444',
  task: '#3b82f6',
  condition: '#f59e0b',
  parallel: '#8b5cf6',
  agent: '#ec4899',
};

/** Node props */
export interface WorkflowNodeProps {
  node: NodeType;
  isSelected: boolean;
  isEditing: boolean;
  onClick: () => void;
  onDrag: (position: { x: number; y: number }) => void;
  onConnectStart: () => void;
  onConnectEnd: () => void;
}

/**
 * Workflow Node Component
 */
export const WorkflowNode: React.FC<WorkflowNodeProps> = ({
  node,
  isSelected,
  isEditing,
  onClick,
  onDrag,
  onConnectStart,
  onConnectEnd,
}) => {
  const nodeRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Handle drag start
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!isEditing) return;
      e.stopPropagation();
      setIsDragging(true);
      setDragOffset({
        x: e.clientX - node.position.x,
        y: e.clientY - node.position.y,
      });
    },
    [isEditing, node.position]
  );

  // Handle drag
  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isDragging) return;
      onDrag({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y,
      });
    },
    [isDragging, dragOffset, onDrag]
  );

  // Handle drag end
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Add/remove global listeners
  React.useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div
      ref={nodeRef}
      className={`apex-workflow-node apex-workflow-node--${node.type} ${
        isSelected ? 'apex-workflow-node--selected' : ''
      } ${isDragging ? 'apex-workflow-node--dragging' : ''}`}
      style={{
        left: node.position.x,
        top: node.position.y,
        borderColor: nodeColors[node.type],
      }}
      onClick={onClick}
      onMouseDown={handleMouseDown}
    >
      {/* Input Handle */}
      {node.type !== 'start' && (
        <div
          className="apex-workflow-node__handle apex-workflow-node__handle--input"
          onMouseUp={onConnectEnd}
        />
      )}

      {/* Content */}
      <div className="apex-workflow-node__content">
        <span className="apex-workflow-node__icon">
          {nodeIcons[node.type]}
        </span>
        <span className="apex-workflow-node__label">{node.label}</span>
      </div>

      {/* Output Handle */}
      {node.type !== 'end' && (
        <div
          className="apex-workflow-node__handle apex-workflow-node__handle--output"
          onMouseDown={(e) => {
            e.stopPropagation();
            onConnectStart();
          }}
        />
      )}
    </div>
  );
};
