/**
 * APEX Development Platform - Dashboard View
 * Overview of all platform features and quick stats
 */

import React, { useState, useEffect } from 'react';
import { 
  LayoutGrid, Brain, GitBranch, BarChart3, Bot, Shield, Scale,
  Activity, Zap, CheckCircle, Clock, TrendingUp, AlertTriangle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Progress } from '../ui/progress';

interface DashboardStats {
  activeTasks: number;
  completedTasks: number;
  activeAgents: number;
  memoryEpisodes: number;
  workflowsRunning: number;
  securityScore: number;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ElementType;
  action: string;
}

interface DashboardViewProps {
  onNavigate?: (view: string) => void;
}

const DashboardView: React.FC<DashboardViewProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats>({
    activeTasks: 0,
    completedTasks: 0,
    activeAgents: 0,
    memoryEpisodes: 0,
    workflowsRunning: 0,
    securityScore: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 300));
      setStats({
        activeTasks: 12,
        completedTasks: 47,
        activeAgents: 3,
        memoryEpisodes: 156,
        workflowsRunning: 2,
        securityScore: 94,
      });
      setLoading(false);
    };
    loadStats();
  }, []);

  const phaseCards = [
    { id: 'memory', title: 'Memory & Context', description: 'Persistent memory with Graphiti', icon: Brain, phase: 2, status: 'active', view: 'memory' },
    { id: 'workflow', title: 'Workflow Orchestration', description: 'Automated CI/CD pipelines', icon: GitBranch, phase: 3, status: 'active', view: 'workflow' },
    { id: 'analytics', title: 'Analytics Dashboard', description: 'Performance metrics & insights', icon: BarChart3, phase: 4, status: 'active', view: 'analytics' },
    { id: 'agents', title: 'Multi-Agent Collaboration', description: 'AI agents working together', icon: Bot, phase: 5, status: 'active', view: 'agents' },
    { id: 'security', title: 'Security & Compliance', description: 'Vulnerability scanning & policies', icon: Shield, phase: 6, status: 'active', view: 'security' },
    { id: 'governance', title: 'Governance Framework', description: 'Policies & audit trails', icon: Scale, phase: 7, status: 'active', view: 'governance' },
  ];

  const handleNavigate = (view: string) => {
    if (onNavigate) {
      onNavigate(view);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold">APEX Development Platform</h1>
          <p className="text-muted-foreground">AI-powered development with 10-phase architecture</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <Activity className="h-6 w-6 mx-auto text-blue-500 mb-2" />
              <p className="text-2xl font-bold">{stats.activeTasks}</p>
              <p className="text-xs text-muted-foreground">Active Tasks</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <CheckCircle className="h-6 w-6 mx-auto text-green-500 mb-2" />
              <p className="text-2xl font-bold">{stats.completedTasks}</p>
              <p className="text-xs text-muted-foreground">Completed</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Bot className="h-6 w-6 mx-auto text-purple-500 mb-2" />
              <p className="text-2xl font-bold">{stats.activeAgents}</p>
              <p className="text-xs text-muted-foreground">Active Agents</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Brain className="h-6 w-6 mx-auto text-orange-500 mb-2" />
              <p className="text-2xl font-bold">{stats.memoryEpisodes}</p>
              <p className="text-xs text-muted-foreground">Memory Episodes</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Zap className="h-6 w-6 mx-auto text-yellow-500 mb-2" />
              <p className="text-2xl font-bold">{stats.workflowsRunning}</p>
              <p className="text-xs text-muted-foreground">Workflows</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Shield className="h-6 w-6 mx-auto text-emerald-500 mb-2" />
              <p className="text-2xl font-bold">{stats.securityScore}%</p>
              <p className="text-xs text-muted-foreground">Security Score</p>
            </CardContent>
          </Card>
        </div>

        {/* Phase Features */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Platform Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {phaseCards.map((phase) => (
              <Card 
                key={phase.id} 
                className="cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => handleNavigate(phase.view)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <phase.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-sm">{phase.title}</CardTitle>
                        <CardDescription className="text-xs">{phase.description}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="secondary">Phase {phase.phase}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-xs text-muted-foreground capitalize">{phase.status}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" onClick={() => handleNavigate('kanban')}>
              <LayoutGrid className="h-6 w-6" />
              <span>View Tasks</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" onClick={() => handleNavigate('agents')}>
              <Bot className="h-6 w-6" />
              <span>Manage Agents</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" onClick={() => handleNavigate('workflow')}>
              <GitBranch className="h-6 w-6" />
              <span>Run Workflow</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex flex-col gap-2" onClick={() => handleNavigate('security')}>
              <Shield className="h-6 w-6" />
              <span>Security Scan</span>
            </Button>
          </div>
        </div>
      </div>
    </ScrollArea>
  );
};

export default DashboardView;
