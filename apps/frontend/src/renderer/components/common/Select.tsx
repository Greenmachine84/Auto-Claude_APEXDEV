/**
 * APEX Development Platform - Select Component
 * Phase 4: UI, Integrations & Analytics
 */

import React, { useState, useRef, useEffect, useCallback } from 'react';

/** Select option */
export interface SelectOption<T = string> {
  value: T;
  label: string;
  disabled?: boolean;
  icon?: React.ReactNode;
}

/** Select props */
export interface SelectProps<T = string> {
  options: SelectOption<T>[];
  value?: T;
  onChange?: (value: T) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  searchable?: boolean;
  clearable?: boolean;
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  className?: string;
}

/**
 * Select Component
 */
export function Select<T = string>({
  options,
  value,
  onChange,
  placeholder = 'Select...',
  label,
  error,
  disabled = false,
  searchable = false,
  clearable = false,
  size = 'medium',
  fullWidth = false,
  className = '',
}: SelectProps<T>): React.ReactElement {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Find selected option
  const selectedOption = options.find((opt) => opt.value === value);

  // Filter options by search
  const filteredOptions = searchable
    ? options.filter((opt) => opt.label.toLowerCase().includes(search.toLowerCase()))
    : options;

  // Handle outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle option select
  const handleSelect = useCallback(
    (option: SelectOption<T>) => {
      if (option.disabled) return;
      onChange?.(option.value);
      setIsOpen(false);
      setSearch('');
    },
    [onChange]
  );

  // Handle clear
  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.(undefined as T);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      setSearch('');
    } else if (e.key === 'Enter' && !isOpen) {
      setIsOpen(true);
    }
  };

  const wrapperClasses = [
    'apex-select-wrapper',
    fullWidth && 'apex-select-wrapper--full-width',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const selectClasses = [
    'apex-select',
    `apex-select--${size}`,
    isOpen && 'apex-select--open',
    disabled && 'apex-select--disabled',
    error && 'apex-select--error',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div ref={containerRef} className={wrapperClasses}>
      {label && <label className="apex-select__label">{label}</label>}
      <div
        className={selectClasses}
        onClick={() => !disabled && setIsOpen(!isOpen)}
        onKeyDown={handleKeyDown}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <div className="apex-select__value">
          {searchable && isOpen ? (
            <input
              ref={inputRef}
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="apex-select__search"
              placeholder={selectedOption?.label || placeholder}
              autoFocus
            />
          ) : selectedOption ? (
            <>
              {selectedOption.icon && (
                <span className="apex-select__option-icon">{selectedOption.icon}</span>
              )}
              <span>{selectedOption.label}</span>
            </>
          ) : (
            <span className="apex-select__placeholder">{placeholder}</span>
          )}
        </div>
        <div className="apex-select__actions">
          {clearable && value !== undefined && (
            <button className="apex-select__clear" onClick={handleClear} aria-label="Clear">
              ×
            </button>
          )}
          <span className={`apex-select__arrow ${isOpen ? 'apex-select__arrow--up' : ''}`}>▼</span>
        </div>
      </div>

      {isOpen && (
        <ul className="apex-select__dropdown" role="listbox">
          {filteredOptions.length === 0 ? (
            <li className="apex-select__no-options">No options</li>
          ) : (
            filteredOptions.map((option, idx) => (
              <li
                key={String(option.value)}
                className={[
                  'apex-select__option',
                  option.value === value && 'apex-select__option--selected',
                  option.disabled && 'apex-select__option--disabled',
                ]
                  .filter(Boolean)
                  .join(' ')}
                onClick={() => handleSelect(option)}
                role="option"
                aria-selected={option.value === value}
                aria-disabled={option.disabled}
              >
                {option.icon && <span className="apex-select__option-icon">{option.icon}</span>}
                <span>{option.label}</span>
              </li>
            ))
          )}
        </ul>
      )}

      {error && <span className="apex-select__error">{error}</span>}
    </div>
  );
}
