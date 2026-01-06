/**
 * APEX Development Platform - Workflow Canvas
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useRef, useState, useCallback, useEffect } from 'react';
import { WorkflowNode, WorkflowNodeProps } from './WorkflowNode';
import { WorkflowEdge, WorkflowEdgeProps } from './WorkflowEdge';
import type { WorkflowNode as NodeType, WorkflowEdge as EdgeType } from './types';

/** Canvas props */
export interface WorkflowCanvasProps {
  nodes: NodeType[];
  edges: EdgeType[];
  zoom: number;
  selectedNode: NodeType | null;
  selectedEdge: EdgeType | null;
  isEditing: boolean;
  onSelectNode: (node: NodeType | null) => void;
  onSelectEdge: (edge: EdgeType | null) => void;
  onUpdateNode: (nodeId: string, updates: Partial<NodeType>) => void;
  onAddEdge: (source: string, target: string) => void;
}

/**
 * Workflow Canvas Component
 */
export const WorkflowCanvas: React.FC<WorkflowCanvasProps> = ({
  nodes,
  edges,
  zoom,
  selectedNode,
  selectedEdge,
  isEditing,
  onSelectNode,
  onSelectEdge,
  onUpdateNode,
  onAddEdge,
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);

  // Handle canvas pan
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === canvasRef.current) {
        setIsDragging(true);
        setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
        onSelectNode(null);
        onSelectEdge(null);
      }
    },
    [offset, onSelectNode, onSelectEdge]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isDragging) {
        setOffset({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        });
      }
    },
    [isDragging, dragStart]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Handle node drag
  const handleNodeDrag = useCallback(
    (nodeId: string, position: { x: number; y: number }) => {
      if (!isEditing) return;
      onUpdateNode(nodeId, { position });
    },
    [isEditing, onUpdateNode]
  );

  // Handle connection start
  const handleConnectStart = useCallback((nodeId: string) => {
    setConnectingFrom(nodeId);
  }, []);

  // Handle connection end
  const handleConnectEnd = useCallback(
    (nodeId: string) => {
      if (connectingFrom && connectingFrom !== nodeId) {
        onAddEdge(connectingFrom, nodeId);
      }
      setConnectingFrom(null);
    },
    [connectingFrom, onAddEdge]
  );

  // Calculate SVG path for edges
  const getEdgePath = useCallback(
    (source: NodeType, target: NodeType) => {
      const sx = source.position.x + 100;
      const sy = source.position.y + 30;
      const tx = target.position.x;
      const ty = target.position.y + 30;
      const mx = (sx + tx) / 2;
      return `M ${sx} ${sy} C ${mx} ${sy}, ${mx} ${ty}, ${tx} ${ty}`;
    },
    []
  );

  return (
    <div
      ref={canvasRef}
      className="apex-workflow-canvas"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <div
        className="apex-workflow-canvas__inner"
        style={{
          transform: `translate(${offset.x}px, ${offset.y}px) scale(${zoom})`,
          transformOrigin: '0 0',
        }}
      >
        {/* Edges SVG */}
        <svg className="apex-workflow-canvas__edges">
          {edges.map((edge) => {
            const sourceNode = nodes.find((n) => n.id === edge.source);
            const targetNode = nodes.find((n) => n.id === edge.target);
            if (!sourceNode || !targetNode) return null;
            return (
              <WorkflowEdge
                key={edge.id}
                edge={edge}
                path={getEdgePath(sourceNode, targetNode)}
                isSelected={selectedEdge?.id === edge.id}
                onClick={() => onSelectEdge(edge)}
              />
            );
          })}
        </svg>

        {/* Nodes */}
        {nodes.map((node) => (
          <WorkflowNode
            key={node.id}
            node={node}
            isSelected={selectedNode?.id === node.id}
            isEditing={isEditing}
            onClick={() => onSelectNode(node)}
            onDrag={(pos) => handleNodeDrag(node.id, pos)}
            onConnectStart={() => handleConnectStart(node.id)}
            onConnectEnd={() => handleConnectEnd(node.id)}
          />
        ))}
      </div>

      {/* Grid Background */}
      <div className="apex-workflow-canvas__grid" />
    </div>
  );
};
