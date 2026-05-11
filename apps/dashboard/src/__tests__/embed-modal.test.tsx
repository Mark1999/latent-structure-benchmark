// @vitest-environment jsdom
/**
 * EmbedModal component tests.
 *
 * Per T12 acceptance criteria:
 *   - Modal renders / hides per isOpen.
 *   - Snippet contains iframe with correct domain + models query params.
 *   - embed=true present in snippet URL.
 *   - Copy button works.
 *   - Escape + backdrop close behaviors.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T12
 */

import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { createElement } from "react";
import { createRoot } from "react-dom/client";
import { act } from "react";
import { EmbedModal } from "../components/EmbedModal";
import type { EmbedModalProps } from "../components/EmbedModal";

// ── Test setup ─────────────────────────────────────────────────────────────────

let container: HTMLElement;
let root: ReturnType<typeof createRoot>;

beforeEach(() => {
  container = document.createElement("div");
  document.body.appendChild(container);
  root = createRoot(container);

  Object.defineProperty(navigator, "clipboard", {
    value: {
      writeText: vi.fn().mockResolvedValue(undefined),
    },
    writable: true,
    configurable: true,
  });
});

afterEach(() => {
  act(() => {
    root.unmount();
  });
  document.body.removeChild(container);
  vi.restoreAllMocks();
  vi.useRealTimers();
});

function render(props: EmbedModalProps): void {
  act(() => {
    root.render(createElement(EmbedModal, props));
  });
}

// ── Tests ──────────────────────────────────────────────────────────────────────

describe("EmbedModal — open/close state", () => {
  it("renders the dialog when isOpen=true", () => {
    render({
      domain: "family",
      selectedModels: ["model-a", "model-b"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog).not.toBeNull();
  });

  it("does not render when isOpen=false", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: false,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog).toBeNull();
  });

  it("dialog has role='dialog' and aria-modal='true'", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.getAttribute("aria-modal")).toBe("true");
  });

  it("dialog has aria-labelledby referencing the heading", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const dialog = document.body.querySelector('[role="dialog"]');
    const labelledBy = dialog?.getAttribute("aria-labelledby");
    expect(labelledBy).toBeTruthy();
    const heading = document.getElementById(labelledBy!);
    expect(heading).not.toBeNull();
  });
});

describe("EmbedModal — snippet content", () => {
  it("snippet contains <iframe>", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain("<iframe");
  });

  it("snippet URL contains domain param", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain("domain=family");
  });

  it("snippet URL contains models param", () => {
    render({
      domain: "family",
      selectedModels: ["model-a", "model-b"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain("model-a");
    expect(snippet?.textContent).toContain("model-b");
  });

  it("snippet URL contains embed=true", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain("embed=true");
  });

  it("snippet contains cogstructurelab.com", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain("cogstructurelab.com");
  });

  it("snippet title contains 'LSB' and domain title-case", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    const snippet = document.body.querySelector(".embed-modal__snippet");
    expect(snippet?.textContent).toContain("LSB");
    expect(snippet?.textContent).toContain("Family");
  });

  it("snippet contains CC-BY attribution note", () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });
    // The note is outside the <pre> block
    const dialog = document.body.querySelector('[role="dialog"]');
    expect(dialog?.textContent).toContain("CC-BY 4.0");
    expect(dialog?.textContent).toContain("LSB attribution");
  });
});

describe("EmbedModal — close behavior", () => {
  it("Escape key calls onClose", async () => {
    const onClose = vi.fn();
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
    });

    await act(async () => {
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
    });

    expect(onClose).toHaveBeenCalledOnce();
  });

  it("backdrop click calls onClose", async () => {
    const onClose = vi.fn();
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
    });

    const backdrop = document.body.querySelector("[data-testid='embed-modal-backdrop']") as HTMLElement;
    expect(backdrop).not.toBeNull();

    await act(async () => {
      const event = new MouseEvent("click", { bubbles: true });
      Object.defineProperty(event, "target", { value: backdrop, enumerable: true });
      Object.defineProperty(event, "currentTarget", { value: backdrop, enumerable: true });
      backdrop.dispatchEvent(event);
    });

    expect(onClose).toHaveBeenCalled();
  });

  it("close button calls onClose", async () => {
    const onClose = vi.fn();
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose,
    });

    const closeBtn = document.body.querySelector(".embed-modal__close-btn") as HTMLButtonElement;
    expect(closeBtn).not.toBeNull();

    await act(async () => {
      closeBtn.click();
    });

    expect(onClose).toHaveBeenCalledOnce();
  });
});

describe("EmbedModal — copy button", () => {
  it("copy button calls navigator.clipboard.writeText", async () => {
    render({
      domain: "family",
      selectedModels: ["model-a", "model-b"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const copyBtn = document.body.querySelector(".embed-modal__copy-btn") as HTMLButtonElement;
    expect(copyBtn).not.toBeNull();

    await act(async () => {
      copyBtn.click();
    });

    expect(navigator.clipboard.writeText).toHaveBeenCalledOnce();
  });

  it("clipboard receives the snippet text", async () => {
    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const copyBtn = document.body.querySelector(".embed-modal__copy-btn") as HTMLButtonElement;

    await act(async () => {
      copyBtn.click();
    });

    const written = (navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mock.calls[0][0] as string;
    expect(written).toContain("<iframe");
    expect(written).toContain("embed=true");
    expect(written).toContain("domain=family");
  });

  it("copy button shows 'Copied!' feedback after click", async () => {
    vi.useFakeTimers();

    render({
      domain: "family",
      selectedModels: ["model-a"],
      isOpen: true,
      onClose: vi.fn(),
    });

    const copyBtn = document.body.querySelector(".embed-modal__copy-btn") as HTMLButtonElement;

    await act(async () => {
      copyBtn.click();
      await Promise.resolve();
    });

    expect(copyBtn.textContent).toContain("Copied!");

    await act(async () => {
      vi.advanceTimersByTime(1600);
    });

    expect(copyBtn.textContent).not.toContain("Copied!");

    vi.useRealTimers();
  });
});

describe("EmbedModal — focus return on close", () => {
  it("returns focus to triggerRef on close", async () => {
    const triggerBtn = document.createElement("button");
    triggerBtn.textContent = "Open Embed";
    document.body.appendChild(triggerBtn);

    const triggerRef = { current: triggerBtn } as React.RefObject<HTMLButtonElement>;
    const onClose = vi.fn();

    act(() => {
      root.render(
        createElement(EmbedModal, {
          domain: "family",
          selectedModels: ["model-a"],
          isOpen: true,
          onClose,
          triggerRef,
        })
      );
    });

    // Re-render closed.
    act(() => {
      root.render(
        createElement(EmbedModal, {
          domain: "family",
          selectedModels: ["model-a"],
          isOpen: false,
          onClose,
          triggerRef,
        })
      );
    });

    expect(document.activeElement).toBe(triggerBtn);

    document.body.removeChild(triggerBtn);
  });
});
