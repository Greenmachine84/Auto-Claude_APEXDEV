/**
 * APEX Development Platform - Analytics View
 * Phase 4: UI, Integrations & Analytics
 * Updated with shadcn/ui styling
 */

import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, Zap, DollarSign, Clock, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Progress } from '../ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

/** Analytics data types */
export interface AnalyticsData {
  summary: {
    totalTasks: number;
    completedTasks: number;
    totalAgentRuns: number;
    totalTokensUsed: number;
    estimatedCost: number;
    averageTaskDuration: number;
  };
  usage: { date: string; tokens: number; tasks: number; agentRuns: number; }[];
  agentPerformance: { agentType: string; runs: number; successRate: number; avgDuration: number; tokensUsed: number; }[];
  taskMetrics: { status: string; count: number; avgDuration: number; }[];
  costBreakdown: { provider: string; tokens: number; cost: number; }[];
}

const AnalyticsView: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setData(getMockData(timeRange));
      setLoading(false);
    };
    loadData();
  }, [timeRange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data) return null;

  const metrics = [
    { label: 'Total Tasks', value: data.summary.totalTasks, icon: BarChart3, color: 'text-blue-500' },
    { label: 'Completed', value: data.summary.completedTasks, icon: TrendingUp, color: 'text-green-500' },
    { label: 'Agent Runs', value: data.summary.totalAgentRuns, icon: Users, color: 'text-purple-500' },
    { label: 'Tokens Used', value: `${(data.summary.totalTokensUsed / 1000).toFixed(0)}K`, icon: Zap, color: 'text-yellow-500' },
    { label: 'Est. Cost', value: `$${data.summary.estimatedCost.toFixed(2)}`, icon: DollarSign, color: 'text-emerald-500' },
    { label: 'Avg Duration', value: `${Math.floor(data.summary.averageTaskDuration / 60)}m`, icon: Clock, color: 'text-orange-500' },
  ];

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
            <p className="text-muted-foreground">Track your development metrics</p>
          </div>
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select time range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
              <SelectItem value="90d">Last 90 Days</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {metrics.map((metric) => (
            <Card key={metric.label}>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <metric.icon className={`h-4 w-4 ${metric.color}`} />
                  <span className="text-sm text-muted-foreground">{metric.label}</span>
                </div>
                <p className="text-2xl font-bold mt-2">{metric.value}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Agent Performance</CardTitle>
              <CardDescription>Success rates by agent type</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.agentPerformance.map((agent) => (
                <div key={agent.agentType} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="capitalize font-medium">{agent.agentType}</span>
                    <Badge variant={agent.successRate >= 0.9 ? 'default' : 'secondary'}>
                      {(agent.successRate * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  <Progress value={agent.successRate * 100} />
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{agent.runs} runs</span>
                    <span>{(agent.tokensUsed / 1000).toFixed(0)}K tokens</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Task Metrics</CardTitle>
              <CardDescription>Task distribution by status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {data.taskMetrics.map((task) => (
                <div key={task.status} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${
                      task.status === 'completed' ? 'bg-green-500' :
                      task.status === 'in-progress' ? 'bg-blue-500' :
                      task.status === 'pending' ? 'bg-yellow-500' : 'bg-red-500'
                    }`} />
                    <span className="capitalize">{task.status}</span>
                  </div>
                  <span className="font-bold">{task.count}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Cost Breakdown</CardTitle>
              <CardDescription>Token usage and costs by provider</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {data.costBreakdown.map((provider) => (
                  <div key={provider.provider} className="p-4 rounded-lg bg-muted">
                    <p className="font-medium capitalize">{provider.provider}</p>
                    <p className="text-2xl font-bold">${provider.cost.toFixed(2)}</p>
                    <p className="text-sm text-muted-foreground">{(provider.tokens / 1000).toFixed(0)}K tokens</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </ScrollArea>
  );
};

function getMockData(timeRange: string): AnalyticsData {
  const days = timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
  return {
    summary: {
      totalTasks: Math.floor(Math.random() * 100 * days),
      completedTasks: Math.floor(Math.random() * 80 * days),
      totalAgentRuns: Math.floor(Math.random() * 200 * days),
      totalTokensUsed: Math.floor(Math.random() * 1000000 * days),
      estimatedCost: Math.random() * 50 * days,
      averageTaskDuration: 300 + Math.random() * 600,
    },
    usage: Array.from({ length: days }, (_, i) => ({
      date: new Date(Date.now() - (days - i) * 86400000).toISOString().split('T')[0],
      tokens: Math.floor(Math.random() * 50000),
      tasks: Math.floor(Math.random() * 20),
      agentRuns: Math.floor(Math.random() * 50),
    })),
    agentPerformance: [
      { agentType: 'coder', runs: 150, successRate: 0.92, avgDuration: 180, tokensUsed: 450000 },
      { agentType: 'reviewer', runs: 100, successRate: 0.98, avgDuration: 120, tokensUsed: 200000 },
      { agentType: 'fixer', runs: 75, successRate: 0.85, avgDuration: 240, tokensUsed: 180000 },
      { agentType: 'planner', runs: 50, successRate: 0.95, avgDuration: 90, tokensUsed: 120000 },
    ],
    taskMetrics: [
      { status: 'completed', count: 85, avgDuration: 420 },
      { status: 'in-progress', count: 12, avgDuration: 180 },
      { status: 'pending', count: 25, avgDuration: 0 },
      { status: 'failed', count: 5, avgDuration: 300 },
    ],
    costBreakdown: [
      { provider: 'openai', tokens: 500000, cost: 15.00 },
      { provider: 'anthropic', tokens: 300000, cost: 12.00 },
      { provider: 'copilot', tokens: 200000, cost: 0 },
      { provider: 'ollama', tokens: 150000, cost: 0 },
    ],
  };
}

export default AnalyticsView;
