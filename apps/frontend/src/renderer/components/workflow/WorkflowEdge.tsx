/**
 * APEX Development Platform - Workflow Edge
 * Phase 4: UI, Integrations & Analytics
 */

import React from 'react';
import type { WorkflowEdge as EdgeType } from './types';

/** Edge props */
export interface WorkflowEdgeProps {
  edge: EdgeType;
  path: string;
  isSelected: boolean;
  onClick: () => void;
}

/**
 * Workflow Edge Component
 */
export const WorkflowEdge: React.FC<WorkflowEdgeProps> = ({
  edge,
  path,
  isSelected,
  onClick,
}) => {
  return (
    <g
      className={`apex-workflow-edge ${isSelected ? 'apex-workflow-edge--selected' : ''}`}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    >
      {/* Background for easier clicking */}
      <path
        d={path}
        className="apex-workflow-edge__hitbox"
        strokeWidth="12"
        stroke="transparent"
        fill="none"
      />
      {/* Visible edge */}
      <path
        d={path}
        className="apex-workflow-edge__line"
        strokeWidth={isSelected ? 3 : 2}
        stroke={isSelected ? '#3b82f6' : '#64748b'}
        fill="none"
        markerEnd="url(#arrowhead)"
      />
      {/* Arrow marker definition */}
      <defs>
        <marker
          id="arrowhead"
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill={isSelected ? '#3b82f6' : '#64748b'}
          />
        </marker>
      </defs>
      {/* Label if present */}
      {edge.label && (
        <text className="apex-workflow-edge__label">
          <textPath href={`#edge-${edge.id}`} startOffset="50%">
            {edge.label}
          </textPath>
        </text>
      )}
    </g>
  );
};
