/**
 * APEX Development Platform - Security View
 * Phase 6: Security Infrastructure
 * 
 * Security dashboard showing audit logs, RBAC status, and security scans
 */

import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle, Lock, Users, FileSearch, Clock } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { ScrollArea } from '../ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { cn } from '../../lib/utils';

/** Security scan status */
type ScanStatus = 'passing' | 'warning' | 'critical' | 'pending';

/** Audit log entry */
interface AuditLogEntry {
  id: string;
  timestamp: string;
  action: string;
  user: string;
  resource: string;
  status: 'success' | 'failure' | 'warning';
  details?: string;
}

/** Security finding */
interface SecurityFinding {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  category: string;
  detectedAt: string;
  resolved: boolean;
}

/** RBAC Role */
interface Role {
  id: string;
  name: string;
  permissions: string[];
  userCount: number;
}

/**
 * Security View Component
 */
const SecurityView: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [scanStatus, setScanStatus] = useState<ScanStatus>('passing');
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [findings, setFindings] = useState<SecurityFinding[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);

  // Load mock data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Mock audit logs
      setAuditLogs([
        { id: '1', timestamp: new Date().toISOString(), action: 'Project Access', user: 'admin', resource: 'Project A', status: 'success' },
        { id: '2', timestamp: new Date(Date.now() - 3600000).toISOString(), action: 'Security Scan', user: 'system', resource: 'All Projects', status: 'success' },
        { id: '3', timestamp: new Date(Date.now() - 7200000).toISOString(), action: 'Role Update', user: 'admin', resource: 'Developer Role', status: 'success' },
      ]);

      // Mock findings
      setFindings([
        { id: '1', severity: 'medium', title: 'Outdated Dependency', description: 'lodash@4.17.15 has known vulnerabilities', category: 'Dependencies', detectedAt: new Date().toISOString(), resolved: false },
      ]);

      // Mock roles
      setRoles([
        { id: '1', name: 'Admin', permissions: ['read', 'write', 'delete', 'admin'], userCount: 2 },
        { id: '2', name: 'Developer', permissions: ['read', 'write'], userCount: 5 },
        { id: '3', name: 'Viewer', permissions: ['read'], userCount: 10 },
      ]);

      setScanStatus(findings.length > 0 ? 'warning' : 'passing');
      setLoading(false);
    };
    loadData();
  }, []);

  const getStatusColor = (status: ScanStatus) => {
    switch (status) {
      case 'passing': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'critical': return 'text-red-500';
      default: return 'text-muted-foreground';
    }
  };

  const getSeverityBadge = (severity: SecurityFinding['severity']) => {
    const colors = {
      low: 'bg-blue-500/10 text-blue-500',
      medium: 'bg-yellow-500/10 text-yellow-500',
      high: 'bg-orange-500/10 text-orange-500',
      critical: 'bg-red-500/10 text-red-500',
    };
    return colors[severity];
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Shield className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-2xl font-bold">Security Dashboard</h1>
            <p className="text-muted-foreground">Phase 6: Security Infrastructure</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={cn("font-medium", getStatusColor(scanStatus))}>
            {scanStatus === 'passing' && <CheckCircle className="mr-1 h-4 w-4" />}
            {scanStatus === 'warning' && <AlertTriangle className="mr-1 h-4 w-4" />}
            {scanStatus.charAt(0).toUpperCase() + scanStatus.slice(1)}
          </Badge>
          <Button variant="outline" size="sm">
            <FileSearch className="mr-2 h-4 w-4" />
            Run Scan
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Security Score</CardDescription>
            <CardTitle className="text-3xl">95%</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Findings</CardDescription>
            <CardTitle className="text-3xl">{findings.filter(f => !f.resolved).length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Audit Events (24h)</CardDescription>
            <CardTitle className="text-3xl">{auditLogs.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Roles</CardDescription>
            <CardTitle className="text-3xl">{roles.length}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="audit">Audit Log</TabsTrigger>
          <TabsTrigger value="findings">Findings</TabsTrigger>
          <TabsTrigger value="rbac">Access Control</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="flex-1 mt-4">
          <div className="grid grid-cols-2 gap-4 h-full">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Recent Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {auditLogs.slice(0, 5).map(log => (
                    <div key={log.id} className="flex items-center justify-between py-2 border-b last:border-0">
                      <div>
                        <p className="font-medium">{log.action}</p>
                        <p className="text-sm text-muted-foreground">{log.resource}</p>
                      </div>
                      <Badge variant={log.status === 'success' ? 'default' : 'destructive'}>
                        {log.status}
                      </Badge>
                    </div>
                  ))}
                </ScrollArea>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Active Findings
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-64">
                  {findings.filter(f => !f.resolved).length === 0 ? (
                    <div className="flex items-center justify-center h-full text-muted-foreground">
                      <CheckCircle className="mr-2 h-5 w-5 text-green-500" />
                      No active security findings
                    </div>
                  ) : (
                    findings.filter(f => !f.resolved).map(finding => (
                      <div key={finding.id} className="py-2 border-b last:border-0">
                        <div className="flex items-center gap-2">
                          <Badge className={getSeverityBadge(finding.severity)}>
                            {finding.severity}
                          </Badge>
                          <p className="font-medium">{finding.title}</p>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{finding.description}</p>
                      </div>
                    ))
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="audit" className="flex-1 mt-4">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Audit Log</CardTitle>
              <CardDescription>Security events and access history</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-2">Time</th>
                      <th className="text-left py-2">Action</th>
                      <th className="text-left py-2">User</th>
                      <th className="text-left py-2">Resource</th>
                      <th className="text-left py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.map(log => (
                      <tr key={log.id} className="border-b last:border-0">
                        <td className="py-2 text-sm text-muted-foreground">
                          {new Date(log.timestamp).toLocaleString()}
                        </td>
                        <td className="py-2">{log.action}</td>
                        <td className="py-2">{log.user}</td>
                        <td className="py-2">{log.resource}</td>
                        <td className="py-2">
                          <Badge variant={log.status === 'success' ? 'default' : 'destructive'}>
                            {log.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="findings" className="flex-1 mt-4">
          <Card className="h-full">
            <CardHeader>
              <CardTitle>Security Findings</CardTitle>
              <CardDescription>Vulnerabilities and security issues detected</CardDescription>
            </CardHeader>
            <CardContent>
              {findings.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
                  <CheckCircle className="h-12 w-12 text-green-500 mb-4" />
                  <p className="text-lg font-medium">No security findings</p>
                  <p className="text-sm">All security scans passed</p>
                </div>
              ) : (
                <ScrollArea className="h-96">
                  {findings.map(finding => (
                    <div key={finding.id} className="p-4 border rounded-lg mb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge className={getSeverityBadge(finding.severity)}>
                            {finding.severity}
                          </Badge>
                          <span className="font-medium">{finding.title}</span>
                        </div>
                        {finding.resolved && <Badge variant="outline">Resolved</Badge>}
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">{finding.description}</p>
                      <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                        <span>Category: {finding.category}</span>
                        <span>Detected: {new Date(finding.detectedAt).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rbac" className="flex-1 mt-4">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Role-Based Access Control
              </CardTitle>
              <CardDescription>Manage user roles and permissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {roles.map(role => (
                  <Card key={role.id}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        {role.name}
                      </CardTitle>
                      <CardDescription>{role.userCount} users</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-1">
                        {role.permissions.map(perm => (
                          <Badge key={perm} variant="outline" className="text-xs">
                            {perm}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SecurityView;
