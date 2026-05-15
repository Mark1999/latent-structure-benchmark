// DESIGN_SYSTEM.md §8.2.14 — confirmed accessibility strings for the mobile model selector drawer.

export const MOBILE_MODEL_DRAWER_TRIGGER_LABEL_CLOSED = "Open model selector";
export const MOBILE_MODEL_DRAWER_TRIGGER_LABEL_OPEN = "Close model selector";
export const MOBILE_MODEL_DRAWER_PANEL_LABEL = "Model selector";
export const MOBILE_MODEL_DRAWER_TRIGGER_TEXT = (n: number): string =>
  `Select models (${n} selected)`;
