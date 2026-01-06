/**
 * APEX Development Platform - Workflow View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useCallback } from 'react';
import { WorkflowCanvas } from './WorkflowCanvas';
import { WorkflowToolbar } from './WorkflowToolbar';
import { WorkflowSidebar } from './WorkflowSidebar';
import type { WorkflowNode, WorkflowEdge } from './types';

/** Workflow node types */
export type NodeType = 'start' | 'end' | 'task' | 'condition' | 'parallel' | 'agent';

/** Workflow definition */
export interface Workflow {
  id: string;
  name: string;
  description: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  createdAt: string;
  updatedAt: string;
}

/**
 * Workflow View Component
 */
const WorkflowView: React.FC = () => {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [selectedNode, setSelectedNode] = useState<WorkflowNode | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<WorkflowEdge | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [zoom, setZoom] = useState(1);

  // Handle node selection
  const handleSelectNode = useCallback((node: WorkflowNode | null) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);

  // Handle edge selection
  const handleSelectEdge = useCallback((edge: WorkflowEdge | null) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);

  // Handle node update
  const handleUpdateNode = useCallback(
    (nodeId: string, updates: Partial<WorkflowNode>) => {
      if (!workflow) return;
      setWorkflow({
        ...workflow,
        nodes: workflow.nodes.map((n) =>
          n.id === nodeId ? { ...n, ...updates } : n
        ),
      });
    },
    [workflow]
  );

  // Handle add node
  const handleAddNode = useCallback(
    (type: NodeType, position: { x: number; y: number }) => {
      if (!workflow) return;
      const newNode: WorkflowNode = {
        id: `node-${Date.now()}`,
        type,
        label: `New ${type}`,
        position,
        data: {},
      };
      setWorkflow({
        ...workflow,
        nodes: [...workflow.nodes, newNode],
      });
    },
    [workflow]
  );

  // Handle delete node
  const handleDeleteNode = useCallback(
    (nodeId: string) => {
      if (!workflow) return;
      setWorkflow({
        ...workflow,
        nodes: workflow.nodes.filter((n) => n.id !== nodeId),
        edges: workflow.edges.filter(
          (e) => e.source !== nodeId && e.target !== nodeId
        ),
      });
      setSelectedNode(null);
    },
    [workflow]
  );

  // Handle add edge
  const handleAddEdge = useCallback(
    (source: string, target: string) => {
      if (!workflow) return;
      const newEdge: WorkflowEdge = {
        id: `edge-${Date.now()}`,
        source,
        target,
      };
      setWorkflow({
        ...workflow,
        edges: [...workflow.edges, newEdge],
      });
    },
    [workflow]
  );

  // Create new workflow
  const handleNewWorkflow = useCallback(() => {
    setWorkflow({
      id: `workflow-${Date.now()}`,
      name: 'New Workflow',
      description: '',
      nodes: [
        { id: 'start', type: 'start', label: 'Start', position: { x: 100, y: 200 }, data: {} },
        { id: 'end', type: 'end', label: 'End', position: { x: 600, y: 200 }, data: {} },
      ],
      edges: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    });
    setIsEditing(true);
  }, []);

  // No workflow loaded
  if (!workflow) {
    return (
      <div className="apex-workflow-view apex-workflow-view--empty">
        <h2>🔄 Workflow Designer</h2>
        <p>Create visual workflows to orchestrate agent tasks</p>
        <button
          className="apex-workflow-view__new-btn"
          onClick={handleNewWorkflow}
        >
          + New Workflow
        </button>
      </div>
    );
  }

  return (
    <div className="apex-workflow-view">
      {/* Toolbar */}
      <WorkflowToolbar
        workflow={workflow}
        zoom={zoom}
        isEditing={isEditing}
        onZoomChange={setZoom}
        onToggleEdit={() => setIsEditing(!isEditing)}
        onSave={() => console.log('Save workflow')}
      />

      {/* Main Content */}
      <div className="apex-workflow-view__content">
        {/* Canvas */}
        <WorkflowCanvas
          nodes={workflow.nodes}
          edges={workflow.edges}
          zoom={zoom}
          selectedNode={selectedNode}
          selectedEdge={selectedEdge}
          isEditing={isEditing}
          onSelectNode={handleSelectNode}
          onSelectEdge={handleSelectEdge}
          onUpdateNode={handleUpdateNode}
          onAddEdge={handleAddEdge}
        />

        {/* Sidebar */}
        {isEditing && (
          <WorkflowSidebar
            selectedNode={selectedNode}
            onAddNode={handleAddNode}
            onUpdateNode={handleUpdateNode}
            onDeleteNode={handleDeleteNode}
          />
        )}
      </div>
    </div>
  );
};

export default WorkflowView;
