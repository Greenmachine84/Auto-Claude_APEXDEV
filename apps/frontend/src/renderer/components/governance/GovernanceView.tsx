/**
 * APEX Development Platform - Governance View
 * Phase 9: Governance Architecture
 * 
 * Dashboard for policies, compliance, and governance controls
 */

import React, { useState, useEffect } from 'react';
import { Scale, FileCheck, AlertCircle, CheckCircle2, BookOpen, Settings2, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Progress } from '../ui/progress';
import { cn } from '../../lib/utils';

/** Policy status */
type PolicyStatus = 'active' | 'inactive' | 'pending' | 'expired';

/** Policy interface */
interface Policy {
  id: string;
  name: string;
  description: string;
  category: string;
  status: PolicyStatus;
  compliance: number;
  lastReviewed: string;
  nextReview: string;
}

/** Compliance check */
interface ComplianceCheck {
  id: string;
  name: string;
  category: string;
  status: 'passing' | 'failing' | 'warning';
  lastRun: string;
  details: string;
}

/** Governance metric */
interface GovernanceMetric {
  name: string;
  value: number;
  target: number;
  trend: 'up' | 'down' | 'stable';
}

/**
 * Governance View Component
 */
const GovernanceView: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [checks, setChecks] = useState<ComplianceCheck[]>([]);
  const [metrics, setMetrics] = useState<GovernanceMetric[]>([]);
  const [loading, setLoading] = useState(true);

  // Load mock data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock policies
      setPolicies([
        { id: '1', name: 'Code Review Policy', description: 'All code changes must be reviewed before merging', category: 'Development', status: 'active', compliance: 95, lastReviewed: new Date(Date.now() - 7 * 24 * 3600000).toISOString(), nextReview: new Date(Date.now() + 23 * 24 * 3600000).toISOString() },
        { id: '2', name: 'Security Scanning', description: 'Automated security scans on every commit', category: 'Security', status: 'active', compliance: 100, lastReviewed: new Date(Date.now() - 3 * 24 * 3600000).toISOString(), nextReview: new Date(Date.now() + 27 * 24 * 3600000).toISOString() },
        { id: '3', name: 'Data Retention', description: 'Data must be retained for 90 days', category: 'Data', status: 'active', compliance: 88, lastReviewed: new Date(Date.now() - 14 * 24 * 3600000).toISOString(), nextReview: new Date(Date.now() + 16 * 24 * 3600000).toISOString() },
      ]);

      // Mock compliance checks
      setChecks([
        { id: '1', name: 'Branch Protection', category: 'Git', status: 'passing', lastRun: new Date().toISOString(), details: 'All branches have required reviews' },
        { id: '2', name: 'Secret Scanning', category: 'Security', status: 'passing', lastRun: new Date().toISOString(), details: 'No secrets detected in codebase' },
        { id: '3', name: 'License Compliance', category: 'Legal', status: 'warning', lastRun: new Date().toISOString(), details: '2 dependencies with GPL licenses detected' },
      ]);

      // Mock metrics
      setMetrics([
        { name: 'Policy Compliance', value: 94, target: 95, trend: 'up' },
        { name: 'Security Score', value: 88, target: 90, trend: 'stable' },
        { name: 'Code Coverage', value: 76, target: 80, trend: 'up' },
        { name: 'Review Cycle Time', value: 4, target: 8, trend: 'down' },
      ]);

      setLoading(false);
    };
    loadData();
  }, []);

  const getStatusBadge = (status: PolicyStatus) => {
    const styles = {
      active: 'bg-green-500/10 text-green-500',
      inactive: 'bg-gray-500/10 text-gray-500',
      pending: 'bg-yellow-500/10 text-yellow-500',
      expired: 'bg-red-500/10 text-red-500',
    };
    return styles[status];
  };

  const getCheckStatusIcon = (status: ComplianceCheck['status']) => {
    switch (status) {
      case 'passing': return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failing': return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'warning': return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const overallCompliance = Math.round(policies.reduce((acc, p) => acc + p.compliance, 0) / policies.length);

  return (
    <div className="flex flex-col h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Scale className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">Governance Dashboard</h1>
            <p className="text-muted-foreground">Phase 9: Governance Architecture</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="font-medium text-lg px-4 py-1">
            {overallCompliance}% Compliant
          </Badge>
          <Button variant="outline" size="sm">
            <Settings2 className="mr-2 h-4 w-4" />
            Configure
          </Button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-4 gap-4">
        {metrics.map(metric => (
          <Card key={metric.name}>
            <CardHeader className="pb-2">
              <CardDescription className="flex items-center justify-between">
                {metric.name}
                <TrendingUp className={cn(
                  "h-4 w-4",
                  metric.trend === 'up' && "text-green-500",
                  metric.trend === 'down' && "text-red-500",
                  metric.trend === 'stable' && "text-muted-foreground"
                )} />
              </CardDescription>
              <CardTitle className="text-3xl">{metric.value}{metric.name.includes('Time') ? 'h' : '%'}</CardTitle>
            </CardHeader>
            <CardContent>
              <Progress value={(metric.value / metric.target) * 100} className="h-2" />
              <p className="text-xs text-muted-foreground mt-1">Target: {metric.target}{metric.name.includes('Time') ? 'h' : '%'}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="policies">Policies</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="flex-1 mt-4">
          <div className="grid grid-cols-2 gap-4 h-full">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Active Policies
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {policies.filter(p => p.status === 'active').map(policy => (
                    <div key={policy.id} className="flex items-center justify-between py-3 border-b last:border-0">
                      <div>
                        <p className="font-medium">{policy.name}</p>
                        <p className="text-sm text-muted-foreground">{policy.category}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Progress value={policy.compliance} className="w-20 h-2" />
                        <span className="text-sm font-medium">{policy.compliance}%</span>
                      </div>
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileCheck className="h-5 w-5" />
                  Recent Checks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {checks.map(check => (
                    <div key={check.id} className="flex items-center gap-3 py-3 border-b last:border-0">
                      {getCheckStatusIcon(check.status)}
                      <div className="flex-1">
                        <p className="font-medium">{check.name}</p>
                        <p className="text-sm text-muted-foreground">{check.details}</p>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {check.category}
                      </Badge>
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="policies" className="flex-1 mt-4">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Policy Management</CardTitle>
              <CardDescription>Configure and manage governance policies</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {policies.map(policy => (
                    <div key={policy.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{policy.name}</span>
                          <Badge className={getStatusBadge(policy.status)}>
                            {policy.status}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={policy.compliance} className="w-32 h-2" />
                          <span className="text-sm font-medium">{policy.compliance}%</span>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">{policy.description}</p>
                      <div className="flex items-center gap-6 text-xs text-muted-foreground">
                        <span>Category: {policy.category}</span>
                        <span>Last Reviewed: {new Date(policy.lastReviewed).toLocaleDateString()}</span>
                        <span>Next Review: {new Date(policy.nextReview).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance" className="flex-1 mt-4">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Compliance Checks</CardTitle>
              <CardDescription>Automated governance and compliance validation</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Status</th>
                      <th className="text-left py-2">Check Name</th>
                      <th className="text-left py-2">Category</th>
                      <th className="text-left py-2">Last Run</th>
                      <th className="text-left py-2">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {checks.map(check => (
                      <tr key={check.id} className="border-b last:border-0">
                        <td className="py-3">{getCheckStatusIcon(check.status)}</td>
                        <td className="py-3 font-medium">{check.name}</td>
                        <td className="py-3">
                          <Badge variant="outline">{check.category}</Badge>
                        </td>
                        <td className="py-3 text-sm text-muted-foreground">
                          {new Date(check.lastRun).toLocaleString()}
                        </td>
                        <td className="py-3 text-sm text-muted-foreground">{check.details}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default GovernanceView;
