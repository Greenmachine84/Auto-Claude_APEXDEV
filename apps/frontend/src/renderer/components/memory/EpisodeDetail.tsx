/**
 * APEX Development Platform - Episode Detail
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import { Button } from '../common/Button';
import type { Episode } from '../../../preload/api/memory-api';

/** Episode detail props */
export interface EpisodeDetailProps {
  episode: Episode;
  onClose: () => void;
}

/**
 * Episode Detail Component
 */
export const EpisodeDetail: React.FC<EpisodeDetailProps> = ({
  episode,
  onClose,
}) => {
  const [activeTab, setActiveTab] = useState<'content' | 'metadata' | 'embedding'>(
    'content'
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleCopyContent = () => {
    navigator.clipboard.writeText(episode.content);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this episode?')) {
      await window.apex.memory.delete(episode.id);
      onClose();
    }
  };

  return (
    <div className="apex-episode-detail">
      {/* Header */}
      <div className="apex-episode-detail__header">
        <h3>Episode Details</h3>
        <button
          className="apex-episode-detail__close"
          onClick={onClose}
          aria-label="Close"
        >
          ✕
        </button>
      </div>

      {/* Tabs */}
      <div className="apex-episode-detail__tabs">
        {(['content', 'metadata', 'embedding'] as const).map((tab) => (
          <button
            key={tab}
            className={`apex-episode-detail__tab ${
              activeTab === tab ? 'apex-episode-detail__tab--active' : ''
            }`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="apex-episode-detail__content">
        {activeTab === 'content' && (
          <div className="apex-episode-detail__text">
            <pre>{episode.content}</pre>
          </div>
        )}

        {activeTab === 'metadata' && (
          <div className="apex-episode-detail__metadata">
            <dl>
              <dt>ID</dt>
              <dd>{episode.id}</dd>
              <dt>Type</dt>
              <dd>{episode.metadata.type}</dd>
              <dt>Source</dt>
              <dd>{episode.metadata.source || 'N/A'}</dd>
              <dt>Task ID</dt>
              <dd>{episode.metadata.taskId || 'N/A'}</dd>
              <dt>Agent ID</dt>
              <dd>{episode.metadata.agentId || 'N/A'}</dd>
              <dt>Importance</dt>
              <dd>{episode.metadata.importance || 'N/A'}</dd>
              <dt>Tags</dt>
              <dd>{episode.metadata.tags?.join(', ') || 'None'}</dd>
              <dt>Created</dt>
              <dd>{formatDate(episode.createdAt)}</dd>
              <dt>Updated</dt>
              <dd>{formatDate(episode.updatedAt)}</dd>
            </dl>
          </div>
        )}

        {activeTab === 'embedding' && (
          <div className="apex-episode-detail__embedding">
            {episode.embedding ? (
              <>
                <p>Embedding dimensions: {episode.embedding.length}</p>
                <div className="apex-episode-detail__embedding-preview">
                  [{episode.embedding.slice(0, 10).map((v) => v.toFixed(4)).join(', ')}...]
                </div>
              </>
            ) : (
              <p>No embedding available</p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="apex-episode-detail__footer">
        <Button variant="ghost" onClick={handleCopyContent}>
          📋 Copy Content
        </Button>
        <Button variant="danger" onClick={handleDelete}>
          🗑️ Delete
        </Button>
      </div>
    </div>
  );
};
