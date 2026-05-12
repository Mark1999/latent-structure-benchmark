/**
 * InspectTable — reusable table component for the operator inspection page.
 *
 * Renders a fully accessible <table> with:
 *   - <caption> (required prop — WCAG 2.0 SC 1.3.1)
 *   - <th scope="col"> for every column header
 *   - mono font for numeric columns
 *   - pre-wrapped JSON for nested objects/arrays
 *
 * Design system tokens: DESIGN_SYSTEM.md §1.
 * UI/UX binding F-T0-B2: uses --font-mono for monospace rendering.
 *
 * No sort, filter, search, or pagination — T0 is a viewer, not a tool.
 * Any future interactive affordance must be proposed to the Architect.
 */

import type { ReactNode } from "react";

export interface ColumnDef {
  key: string;
  label: string;
}

interface InspectTableProps {
  caption: string;
  columns: ColumnDef[];
  rows: Record<string, unknown>[];
}

/**
 * Render a single cell value.
 * - null/undefined → "null"
 * - string, number, boolean → stringified
 * - arrays/objects → JSON-stringified in a <pre> block
 */
function renderCell(value: unknown): ReactNode {
  if (value === null || value === undefined) {
    return <span style={{ color: "var(--color-text-caption)" }}>null</span>;
  }
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  // Array or object: render as pre-wrapped JSON.
  const json = JSON.stringify(value, null, 2);
  return (
    <pre
      style={{
        margin: 0,
        fontFamily: "var(--font-mono)",
        fontSize: "var(--font-size-xs)",
        whiteSpace: "pre-wrap",
        wordBreak: "break-word",
        maxWidth: "60ch",
      }}
    >
      {json}
    </pre>
  );
}

export function InspectTable({ caption, columns, rows }: InspectTableProps) {
  return (
    <table className="inspect-table">
      <caption>{caption}</caption>
      <thead>
        <tr>
          {columns.map((col) => (
            <th key={col.key} scope="col">
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.length === 0 ? (
          <tr>
            <td
              colSpan={columns.length}
              style={{ color: "var(--color-text-caption)", fontStyle: "italic" }}
            >
              (no rows)
            </td>
          </tr>
        ) : (
          rows.map((row, rowIdx) => (
            <tr key={rowIdx}>
              {columns.map((col) => (
                <td
                  key={col.key}
                  style={{
                    fontFamily:
                      typeof row[col.key] === "number"
                        ? "var(--font-mono)"
                        : undefined,
                  }}
                >
                  {renderCell(row[col.key])}
                </td>
              ))}
            </tr>
          ))
        )}
      </tbody>
    </table>
  );
}
