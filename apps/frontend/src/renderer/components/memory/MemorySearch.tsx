/**
 * APEX Development Platform - Memory Search
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState } from 'react';
import { Input } from '../common/Input';
import { Select, type SelectOption } from '../common/Select';
import { Button } from '../common/Button';
import type { MemorySearchOptions, EpisodeMetadata } from '../../../preload/api/memory-api';

/** Memory search props */
export interface MemorySearchProps {
  onSearch: (options: MemorySearchOptions) => void;
  onClear: () => void;
  isSearchActive: boolean;
}

/** Type options */
const typeOptions: SelectOption<EpisodeMetadata['type'] | ''>[] = [
  { value: '', label: 'All Types' },
  { value: 'task', label: '📝 Task' },
  { value: 'conversation', label: '💬 Conversation' },
  { value: 'code', label: '💻 Code' },
  { value: 'decision', label: '⚖️ Decision' },
  { value: 'insight', label: '💡 Insight' },
];

/**
 * Memory Search Component
 */
export const MemorySearch: React.FC<MemorySearchProps> = ({
  onSearch,
  onClear,
  isSearchActive,
}) => {
  const [query, setQuery] = useState('');
  const [type, setType] = useState<EpisodeMetadata['type'] | ''>('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [limit, setLimit] = useState(50);
  const [threshold, setThreshold] = useState(0.7);

  const handleSearch = () => {
    if (!query.trim()) return;

    const options: MemorySearchOptions = {
      query: query.trim(),
      limit,
      threshold,
    };

    if (type) {
      options.types = [type];
    }

    onSearch(options);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleClear = () => {
    setQuery('');
    setType('');
    onClear();
  };

  return (
    <div className="apex-memory-search">
      {/* Main Search */}
      <div className="apex-memory-search__main">
        <Input
          placeholder="Search memories semantically..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          leftIcon="🔍"
          fullWidth
        />
        <Select
          options={typeOptions}
          value={type}
          onChange={(val) => setType(val as EpisodeMetadata['type'] | '')}
          placeholder="Type"
        />
        <Button variant="primary" onClick={handleSearch} disabled={!query.trim()}>
          Search
        </Button>
        {isSearchActive && (
          <Button variant="ghost" onClick={handleClear}>
            Clear
          </Button>
        )}
      </div>

      {/* Advanced Toggle */}
      <button
        className="apex-memory-search__advanced-toggle"
        onClick={() => setShowAdvanced(!showAdvanced)}
      >
        {showAdvanced ? '▲' : '▼'} Advanced Options
      </button>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="apex-memory-search__advanced">
          <div className="apex-memory-search__option">
            <label>Results Limit</label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 50)}
              min={1}
              max={200}
            />
          </div>
          <div className="apex-memory-search__option">
            <label>Similarity Threshold</label>
            <input
              type="range"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              min={0}
              max={1}
              step={0.1}
            />
            <span>{threshold.toFixed(1)}</span>
          </div>
        </div>
      )}
    </div>
  );
};
