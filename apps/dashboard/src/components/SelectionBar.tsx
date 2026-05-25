/**
 * SelectionBar — "SHOWING: model1 × model2 × +N more"
 * Shows up to 4 chips + "+N more" overflow chip.
 */

const MAX_CHIPS = 4;

interface ModelInfo {
  id: string;
  shortName: string;
  providerColor: string;
}

interface SelectionBarProps {
  selected: ModelInfo[];
  onRemove: (id: string) => void;
}

export function SelectionBar({ selected, onRemove }: SelectionBarProps) {
  if (selected.length === 0) {
    return (
      <div className="selection-bar" aria-live="polite">
        <span className="selection-bar__label">No models selected</span>
      </div>
    );
  }

  const visible = selected.slice(0, MAX_CHIPS);
  const overflow = selected.length - MAX_CHIPS;

  return (
    <div className="selection-bar" aria-live="polite">
      <span className="selection-bar__label">Showing</span>
      {visible.map((m) => (
        <span key={m.id} className="selection-chip">
          <span
            className="selection-chip__dot"
            style={{ background: m.providerColor }}
            aria-hidden="true"
          />
          {m.shortName}
          <button
            className="selection-chip__remove"
            onClick={() => onRemove(m.id)}
            aria-label={`Remove ${m.shortName}`}
            title={`Remove ${m.shortName}`}
          >
            &times;
          </button>
        </span>
      ))}
      {overflow > 0 && (
        <span className="selection-chip selection-chip--overflow">
          +{overflow} more
        </span>
      )}
    </div>
  );
}
