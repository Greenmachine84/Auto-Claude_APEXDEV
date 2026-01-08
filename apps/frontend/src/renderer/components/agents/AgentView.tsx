/**
 * APEX Development Platform - Agents View
 * Phase 5: Multi-Agent Collaboration
 * Updated with shadcn/ui styling
 */

import React, { useState, useEffect } from 'react';
import { Bot, Power, Settings, Activity, MessageSquare, Zap, RefreshCw, Plus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Progress } from '../ui/progress';

interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy' | 'offline';
  capabilities: string[];
  tasksCompleted: number;
  successRate: number;
  lastActive: string;
}

const AgentView: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      const mockAgents = getMockAgents();
      setAgents(mockAgents);
      setSelectedAgent(mockAgents[0]);
      setLoading(false);
    };
    loadData();
  }, []);

  const statusColors = {
    active: 'bg-green-500',
    idle: 'bg-yellow-500',
    busy: 'bg-blue-500',
    offline: 'bg-gray-500',
  };

  const statusBadgeVariants = {
    active: 'default' as const,
    idle: 'secondary' as const,
    busy: 'default' as const,
    offline: 'outline' as const,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Bot className="h-6 w-6" />
              Agent Collaboration
            </h2>
            <p className="text-muted-foreground">Manage AI agents and their interactions</p>
          </div>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Deploy Agent
          </Button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-500/10">
                  <Activity className="h-5 w-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{agents.filter(a => a.status === 'active').length}</p>
                  <p className="text-xs text-muted-foreground">Active Agents</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-500/10">
                  <Zap className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{agents.reduce((sum, a) => sum + a.tasksCompleted, 0)}</p>
                  <p className="text-xs text-muted-foreground">Tasks Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-purple-500/10">
                  <MessageSquare className="h-5 w-5 text-purple-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">156</p>
                  <p className="text-xs text-muted-foreground">Messages Today</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-500/10">
                  <Bot className="h-5 w-5 text-orange-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold">{agents.length}</p>
                  <p className="text-xs text-muted-foreground">Total Agents</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h3 className="font-semibold">Agent Registry</h3>
            {agents.map((agent) => (
              <Card
                key={agent.id}
                className={`cursor-pointer transition-colors hover:bg-muted/50 ${selectedAgent?.id === agent.id ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedAgent(agent)}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                        <Bot className="h-5 w-5" />
                      </div>
                      <div className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-background ${statusColors[agent.status]}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium truncate">{agent.name}</h4>
                      <p className="text-xs text-muted-foreground">{agent.role}</p>
                    </div>
                    <Badge variant={statusBadgeVariants[agent.status]} className="capitalize">
                      {agent.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="lg:col-span-2 space-y-4">
            {selectedAgent && (
              <>
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                          <Bot className="h-6 w-6" />
                        </div>
                        <div>
                          <CardTitle>{selectedAgent.name}</CardTitle>
                          <CardDescription>{selectedAgent.role}</CardDescription>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4 mr-2" />
                          Configure
                        </Button>
                        <Button variant="outline" size="sm">
                          <Power className="h-4 w-4 mr-2" />
                          {selectedAgent.status === 'offline' ? 'Start' : 'Stop'}
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Success Rate</span>
                        <span className="font-medium">{selectedAgent.successRate}%</span>
                      </div>
                      <Progress value={selectedAgent.successRate} />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Tasks Completed</span>
                        <p className="font-medium">{selectedAgent.tasksCompleted}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Last Active</span>
                        <p className="font-medium">{selectedAgent.lastActive}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm">Capabilities</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {selectedAgent.capabilities.map((cap) => (
                        <Badge key={cap} variant="secondary">{cap}</Badge>
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

function getMockAgents(): Agent[] {
  return [
    {
      id: '1',
      name: 'CodeAssist',
      role: 'Code Generation & Review',
      status: 'active',
      capabilities: ['Code Generation', 'Code Review', 'Refactoring', 'Documentation'],
      tasksCompleted: 156,
      successRate: 94,
      lastActive: '2 minutes ago',
    },
    {
      id: '2',
      name: 'TestBot',
      role: 'Testing & QA',
      status: 'busy',
      capabilities: ['Unit Testing', 'Integration Testing', 'Test Coverage', 'Bug Detection'],
      tasksCompleted: 89,
      successRate: 91,
      lastActive: 'now',
    },
    {
      id: '3',
      name: 'DocuGen',
      role: 'Documentation',
      status: 'idle',
      capabilities: ['API Docs', 'README Generation', 'Changelog', 'Type Definitions'],
      tasksCompleted: 45,
      successRate: 98,
      lastActive: '15 minutes ago',
    },
    {
      id: '4',
      name: 'SecuScan',
      role: 'Security Analysis',
      status: 'offline',
      capabilities: ['Vulnerability Scan', 'Dependency Audit', 'SAST', 'Secret Detection'],
      tasksCompleted: 23,
      successRate: 87,
      lastActive: '2 hours ago',
    },
  ];
}

export default AgentView;
