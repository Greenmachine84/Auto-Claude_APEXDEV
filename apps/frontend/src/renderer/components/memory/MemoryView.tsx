/**
 * APEX Development Platform - Memory View
 * Phase 2: Memory & LLM Architecture
 * Updated with shadcn/ui styling
 */

import React, { useState, useEffect } from 'react';
import { Brain, Search, Clock, Tag, FileText, RefreshCw, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { ScrollArea } from '../ui/scroll-area';

interface Episode {
  id: string;
  title: string;
  summary: string;
  timestamp: string;
  tags: string[];
  type: 'task' | 'conversation' | 'code' | 'decision';
}

interface MemoryInsight {
  id: string;
  content: string;
  confidence: number;
  source: string;
}

const MemoryView: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [insights, setInsights] = useState<MemoryInsight[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await new Promise((resolve) => setTimeout(resolve, 500));
      setEpisodes(getMockEpisodes());
      setInsights(getMockInsights());
      setLoading(false);
    };
    loadData();
  }, []);

  const filteredEpisodes = episodes.filter(ep =>
    ep.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    ep.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
    ep.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const typeColors = {
    task: 'bg-blue-500',
    conversation: 'bg-purple-500',
    code: 'bg-green-500',
    decision: 'bg-orange-500',
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
              <Brain className="h-6 w-6" />
              Memory & Context
            </h2>
            <p className="text-muted-foreground">Persistent memory across sessions with Graphiti</p>
          </div>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Sync Memory
          </Button>
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search episodes, tags, or content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <h3 className="font-semibold">Recent Episodes ({filteredEpisodes.length})</h3>
            {filteredEpisodes.map((episode) => (
              <Card 
                key={episode.id} 
                className={`cursor-pointer transition-colors hover:bg-muted/50 ${selectedEpisode?.id === episode.id ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedEpisode(episode)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${typeColors[episode.type]}`} />
                      <div>
                        <h4 className="font-medium">{episode.title}</h4>
                        <p className="text-sm text-muted-foreground line-clamp-2">{episode.summary}</p>
                      </div>
                    </div>
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <Clock className="h-3 w-3 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">{episode.timestamp}</span>
                    <div className="flex gap-1 ml-auto">
                      {episode.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">{tag}</Badge>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold">Memory Insights</h3>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Pattern Recognition</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {insights.map((insight) => (
                  <div key={insight.id} className="p-3 rounded-lg bg-muted">
                    <p className="text-sm">{insight.content}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-muted-foreground">{insight.source}</span>
                      <Badge variant="outline" className="text-xs">
                        {(insight.confidence * 100).toFixed(0)}% confidence
                      </Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Memory Stats</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Episodes</span>
                    <span className="font-medium">{episodes.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Active Contexts</span>
                    <span className="font-medium">3</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Memory Size</span>
                    <span className="font-medium">2.4 MB</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </ScrollArea>
  );
};

function getMockEpisodes(): Episode[] {
  return [
    { id: '1', title: 'Implemented user authentication', summary: 'Added JWT-based authentication with refresh tokens and secure cookie storage.', timestamp: '2 hours ago', tags: ['auth', 'security', 'backend'], type: 'code' },
    { id: '2', title: 'Discussed API architecture', summary: 'Decided to use REST with GraphQL for complex queries. Team agreed on pagination strategy.', timestamp: '5 hours ago', tags: ['architecture', 'api'], type: 'decision' },
    { id: '3', title: 'Bug fix: Memory leak in worker', summary: 'Fixed memory leak caused by unclosed database connections in background workers.', timestamp: '1 day ago', tags: ['bugfix', 'performance'], type: 'task' },
    { id: '4', title: 'Code review feedback', summary: 'Reviewed pull request for the new dashboard component. Suggested improvements for accessibility.', timestamp: '2 days ago', tags: ['review', 'frontend'], type: 'conversation' },
  ];
}

function getMockInsights(): MemoryInsight[] {
  return [
    { id: '1', content: 'You frequently work on authentication-related tasks on Mondays', confidence: 0.85, source: 'Pattern Analysis' },
    { id: '2', content: 'Your code reviews typically focus on accessibility and performance', confidence: 0.92, source: 'Activity Analysis' },
    { id: '3', content: 'Backend tasks take 30% longer when database changes are involved', confidence: 0.78, source: 'Duration Analysis' },
  ];
}

export default MemoryView;
