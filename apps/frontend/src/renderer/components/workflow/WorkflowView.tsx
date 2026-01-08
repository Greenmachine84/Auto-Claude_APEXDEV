/**
 * APEX Development Platform - Workflow View
 * Phase 3: Workflow & Orchestration
 * Updated with shadcn/ui styling
 */

import React, { useState, useEffect } from 'react';
import { GitBranch, Play, Pause, RotateCcw, Plus, CheckCircle, XCircle, Clock, Loader2 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Progress } from '../ui/progress';

interface WorkflowNode {
  id: string;
  name: string;
  type: 'start' | 'task' | 'decision' | 'parallel' | 'end';
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration?: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  progress: number;
  nodes: WorkflowNode[];
  lastRun: string;
}

const WorkflowView: React.FC = () => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      const mockWorkflows = getMockWorkflows();
      setWorkflows(mockWorkflows);
      setSelectedWorkflow(mockWorkflows[0]);
      setLoading(false);
    };
    loadData();
  }, []);

  const statusColors = {
    active: 'bg-green-500',
    paused: 'bg-yellow-500',
    completed: 'bg-blue-500',
    failed: 'bg-red-500',
  };

  const nodeStatusIcons = {
    pending: <Clock className="h-4 w-4 text-muted-foreground" />,
    running: <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />,
    completed: <CheckCircle className="h-4 w-4 text-green-500" />,
    failed: <XCircle className="h-4 w-4 text-red-500" />,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <GitBranch className="h-6 w-6" />
              Workflow Orchestration
            </h2>
            <p className="text-muted-foreground">Manage and monitor automated workflows</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Workflow
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h3 className="font-semibold">Workflows ({workflows.length})</h3>
            {workflows.map((workflow) => (
              <Card
                key={workflow.id}
                className={`cursor-pointer transition-colors hover:bg-muted/50 ${selectedWorkflow?.id === workflow.id ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedWorkflow(workflow)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${statusColors[workflow.status]}`} />
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium truncate">{workflow.name}</h4>
                      <p className="text-xs text-muted-foreground">{workflow.lastRun}</p>
                    </div>
                    <Badge variant="secondary" className="capitalize">{workflow.status}</Badge>
                  </div>
                  <Progress value={workflow.progress} className="mt-3 h-1" />
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="lg:col-span-2 space-y-4">
            {selectedWorkflow && (
              <>
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>{selectedWorkflow.name}</CardTitle>
                        <CardDescription>{selectedWorkflow.description}</CardDescription>
                      </div>
                      <div className="flex gap-2">
                        {selectedWorkflow.status === 'active' ? (
                          <Button variant="outline" size="sm">
                            <Pause className="h-4 w-4 mr-2" />
                            Pause
                          </Button>
                        ) : (
                          <Button variant="outline" size="sm">
                            <Play className="h-4 w-4 mr-2" />
                            Resume
                          </Button>
                        )}
                        <Button variant="outline" size="sm">
                          <RotateCcw className="h-4 w-4 mr-2" />
                          Restart
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium">{selectedWorkflow.progress}%</span>
                      </div>
                      <Progress value={selectedWorkflow.progress} />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Workflow Nodes</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {selectedWorkflow.nodes.map((node, index) => (
                        <div
                          key={node.id}
                          className="flex items-center gap-3 p-3 rounded-lg bg-muted"
                        >
                          <span className="text-xs text-muted-foreground w-6">{index + 1}</span>
                          {nodeStatusIcons[node.status]}
                          <div className="flex-1">
                            <span className="font-medium">{node.name}</span>
                            <Badge variant="outline" className="ml-2 text-xs capitalize">{node.type}</Badge>
                          </div>
                          {node.duration && (
                            <span className="text-xs text-muted-foreground">{node.duration}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </ScrollArea>
  );
};

function getMockWorkflows(): Workflow[] {
  return [
    {
      id: '1',
      name: 'CI/CD Pipeline',
      description: 'Automated build, test, and deployment workflow',
      status: 'active',
      progress: 65,
      lastRun: '5 minutes ago',
      nodes: [
        { id: 'n1', name: 'Checkout Code', type: 'start', status: 'completed', duration: '2s' },
        { id: 'n2', name: 'Install Dependencies', type: 'task', status: 'completed', duration: '45s' },
        { id: 'n3', name: 'Run Tests', type: 'parallel', status: 'running' },
        { id: 'n4', name: 'Build Application', type: 'task', status: 'pending' },
        { id: 'n5', name: 'Deploy to Staging', type: 'decision', status: 'pending' },
        { id: 'n6', name: 'Deploy to Production', type: 'end', status: 'pending' },
      ],
    },
    {
      id: '2',
      name: 'Data Processing',
      description: 'ETL pipeline for analytics data',
      status: 'completed',
      progress: 100,
      lastRun: '1 hour ago',
      nodes: [
        { id: 'n1', name: 'Extract Data', type: 'start', status: 'completed', duration: '30s' },
        { id: 'n2', name: 'Transform Data', type: 'task', status: 'completed', duration: '2m' },
        { id: 'n3', name: 'Load to Warehouse', type: 'end', status: 'completed', duration: '15s' },
      ],
    },
    {
      id: '3',
      name: 'Security Scan',
      description: 'Automated security vulnerability scanning',
      status: 'failed',
      progress: 45,
      lastRun: '2 hours ago',
      nodes: [
        { id: 'n1', name: 'Static Analysis', type: 'start', status: 'completed', duration: '1m' },
        { id: 'n2', name: 'Dependency Check', type: 'task', status: 'failed' },
        { id: 'n3', name: 'Generate Report', type: 'end', status: 'pending' },
      ],
    },
  ];
}

export default WorkflowView;
