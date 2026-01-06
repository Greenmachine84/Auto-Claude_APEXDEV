/**
 * APEX Development Platform - Workflow Types
 * Phase 4: UI, Integrations & Analytics
 */

/** Workflow node type */
export type NodeType = 'start' | 'end' | 'task' | 'condition' | 'parallel' | 'agent';

/** Workflow node */
export interface WorkflowNode {
  id: string;
  type: NodeType;
  label: string;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

/** Workflow edge */
export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  condition?: string;
}
