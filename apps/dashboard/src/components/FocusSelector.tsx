/**
 * FocusSelector — pill toggle between analysis focus levels.
 *
 * Two pills: Focus 3 (cross-model) and Focus 1 (individual model).
 * Focus 2 deferred — do not render a disabled stub.
 * DESIGN_SYSTEM.md §13.1
 */

import '../styles/focus-selector.css';
import type { ActiveFocus } from './VizTabs';

interface FocusSelectorProps {
  active: ActiveFocus;
  onChange: (focus: ActiveFocus) => void;
}

const FOCUS_OPTIONS: Array<{ id: ActiveFocus; label: string }> = [
  { id: 'focus-3', label: 'Focus 3: Cross-model' },
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
