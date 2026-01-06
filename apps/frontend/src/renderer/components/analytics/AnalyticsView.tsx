/**
 * APEX Development Platform - Analytics View
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useEffect } from 'react';
import { MetricsDashboard } from './MetricsDashboard';
import { UsageChart } from './UsageChart';
import { AgentPerformance } from './AgentPerformance';
import { TaskMetrics } from './TaskMetrics';
import { CostTracker } from './CostTracker';
import { Select, type SelectOption } from '../common/Select';
import { LoadingSpinner } from '../common/LoadingSpinner';

/** Time range options */
const timeRangeOptions: SelectOption<string>[] = [
  { value: '24h', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
  { value: '90d', label: 'Last 90 Days' },
  { value: 'all', label: 'All Time' },
];

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
  usage: {
    date: string;
    tokens: number;
    tasks: number;
    agentRuns: number;
  }[];
  agentPerformance: {
    agentType: string;
    runs: number;
    successRate: number;
    avgDuration: number;
    tokensUsed: number;
  }[];
  taskMetrics: {
    status: string;
    count: number;
    avgDuration: number;
  }[];
  costBreakdown: {
    provider: string;
    tokens: number;
    cost: number;
  }[];
}

/**
 * Analytics View Component
 */
const AnalyticsView: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Load analytics data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        // TODO: Replace with actual API call
        await new Promise((resolve) => setTimeout(resolve, 500));
        setData(getMockData(timeRange));
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Failed to load analytics'));
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [timeRange]);

  if (loading) {
    return (
      <div className="apex-analytics-view apex-analytics-view--loading">
        <LoadingSpinner label="Loading analytics..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="apex-analytics-view apex-analytics-view--error">
        <p>Error loading analytics: {error.message}</p>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="apex-analytics-view">
      {/* Header */}
      <div className="apex-analytics-view__header">
        <h2>📊 Analytics Dashboard</h2>
        <Select
          options={timeRangeOptions}
          value={timeRange}
          onChange={setTimeRange}
        />
      </div>

      {/* Summary Dashboard */}
      <MetricsDashboard summary={data.summary} />

      {/* Charts Grid */}
      <div className="apex-analytics-view__grid">
        <UsageChart data={data.usage} />
        <AgentPerformance data={data.agentPerformance} />
        <TaskMetrics data={data.taskMetrics} />
        <CostTracker data={data.costBreakdown} total={data.summary.estimatedCost} />
      </div>
    </div>
  );
};

/** Generate mock data based on time range */
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
      { agentType: 'analyst', runs: 30, successRate: 0.88, avgDuration: 300, tokensUsed: 100000 },
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
