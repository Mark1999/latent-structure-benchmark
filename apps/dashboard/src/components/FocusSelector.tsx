/**
 * FocusSelector — pill toggle between analysis focus levels.
 *
 * Three pills (broadest to narrowest): Focus 3, Focus 2, Focus 1.
 * Order: [Focus 3: Cross-model] [Focus 2: Within-family] [Focus 1: Individual model]
 * DESIGN_SYSTEM.md §14.1 (Focus 2 added v0.7.0)
 */

import '../styles/focus-selector.css';
import type { ActiveFocus } from './VizTabs';

interface FocusSelectorProps {
  active: ActiveFocus;
  onChange: (focus: ActiveFocus) => void;
}

const FOCUS_OPTIONS: Array<{ id: ActiveFocus; label: string }> = [
  { id: 'focus-3', label: 'Focus 3: Cross-model' },
  { id: 'focus-2', label: 'Focus 2: Within-family' },
  { id: 'focus-1', label: 'Focus 1: Individual model' },
];

export function FocusSelector({ active, onChange }: FocusSelectorProps) {
  return (
    <div
      className="focus-selector"
      role="radiogroup"
      aria-label="Analysis focus"
    >
      <span className="focus-selector__label">Focus</span>
      {FOCUS_OPTIONS.map((opt) => (
        <button
          key={opt.id}
          role="radio"
          aria-checked={active === opt.id}
          className={`focus-selector__pill${active === opt.id ? ' focus-selector__pill--active' : ''}`}
          onClick={() => onChange(opt.id)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
