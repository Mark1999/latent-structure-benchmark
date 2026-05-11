// @vitest-environment jsdom
/**
 * Tests for png-metadata.ts — injectTextMetadata().
 *
 * A minimal 1×1 transparent PNG (67 bytes) is used as the fixture. This is
 * the smallest valid PNG; it contains IHDR, IDAT, and IEND chunks.
 *
 * Tests verify:
 *   - Returns a Blob.
 *   - PNG signature is preserved in the output.
 *   - tEXt chunk(s) appear after IHDR and before IDAT.
 *   - tEXt chunk CRC is correct (re-parseable).
 *   - Re-parsing the output yields back the same kv pairs.
 *   - Empty kv produces a Blob byte-for-byte equal to the input.
 *   - Invalid PNG input throws a descriptive error.
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T11
 *         PNG spec RFC 2083 §§11.3.4.3, B
 */

import { describe, it, expect } from "vitest";
import { injectTextMetadata } from "../lib/png-metadata";

// ── Minimal 1×1 transparent PNG fixture ──────────────────────────────────────

/**
 * A 1×1 transparent PNG, base64-encoded.
 * Generated via: python3 -c "import base64; ..."
 * Exact bytes match the canonical 1×1 RGBA=0 PNG structure.
 *
 * Chunk layout:
 *   Offset  0: PNG signature (8 bytes)
 *   Offset  8: IHDR chunk (25 bytes: 4 len + 4 type + 13 data + 4 crc)
 *   Offset 33: IDAT chunk (22 bytes: 4 len + 4 type + 10 data + 4 crc)
 *   Offset 55: IEND chunk (12 bytes: 4 len + 4 type + 0 data + 4 crc)
 *   Total: 67 bytes
 */
const PNG_1X1_B64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==";

function make1x1Blob(): Blob {
  const binStr = atob(PNG_1X1_B64);
  const bytes = new Uint8Array(binStr.length);
  for (let i = 0; i < binStr.length; i++) {
    bytes[i] = binStr.charCodeAt(i);
  }
  return new Blob([bytes], { type: "image/png" });
}

// ── PNG chunk parser (test helper) ───────────────────────────────────────────

interface PngChunk {
  type: string;
  data: Uint8Array;
  offset: number; // byte offset of the length field in the file
}

async function parsePngChunks(blob: Blob): Promise<PngChunk[]> {
  const buf = await blob.arrayBuffer();
  const bytes = new Uint8Array(buf);
  const view = new DataView(buf);
  const chunks: PngChunk[] = [];

  let offset = 8; // skip signature
  while (offset + 12 <= bytes.length) {
    const len = view.getUint32(offset, false);
    const type = String.fromCharCode(
      bytes[offset + 4],
      bytes[offset + 5],
      bytes[offset + 6],
      bytes[offset + 7]
    );
    const data = bytes.slice(offset + 8, offset + 8 + len);
    chunks.push({ type, data, offset });
    offset += 12 + len;
  }
  return chunks;
}

/**
 * Parse a tEXt chunk's data field into keyword + text.
 * Data = keyword (latin-1) + NUL + text (latin-1).
 */
function parseTextChunkData(data: Uint8Array): { keyword: string; text: string } {
  const nullIdx = data.indexOf(0);
  if (nullIdx === -1) throw new Error("tEXt chunk has no NUL separator");
  const keyword = String.fromCharCode(...data.slice(0, nullIdx));
  const text = String.fromCharCode(...data.slice(nullIdx + 1));
  return { keyword, text };
}

/**
 * Compute CRC-32 over a Uint8Array (same algorithm as png-metadata.ts).
 * Used to verify the CRC stored in each chunk is correct.
 */
function crc32(data: Uint8Array): number {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c;
  }
  let c = 0xffffffff;
  for (let i = 0; i < data.length; i++) {
    c = table[(c ^ data[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

/** Verify the CRC stored in a chunk matches what we compute. */
async function verifyChunkCrc(blob: Blob, chunk: PngChunk): Promise<boolean> {
  const buf = await blob.arrayBuffer();
  const bytes = new Uint8Array(buf);
  const view = new DataView(buf);

  const chunkStart = chunk.offset;
  const dataLen = view.getUint32(chunkStart, false);

  // CRC covers: type (4 bytes) + data (dataLen bytes)
  const crcInput = bytes.slice(chunkStart + 4, chunkStart + 8 + dataLen);
  const computed = crc32(crcInput);
  const stored = view.getUint32(chunkStart + 8 + dataLen, false);
  return computed === stored;
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("injectTextMetadata — return type", () => {
  it("returns a Blob", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    expect(result).toBeInstanceOf(Blob);
  });

  it("returns a Blob with type image/png", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    expect(result.type).toBe("image/png");
  });
});

describe("injectTextMetadata — PNG signature preserved", () => {
  it("output starts with the 8-byte PNG signature", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    const buf = await result.arrayBuffer();
    const bytes = new Uint8Array(buf);
    const sig = [137, 80, 78, 71, 13, 10, 26, 10];
    for (let i = 0; i < 8; i++) {
      expect(bytes[i]).toBe(sig[i]);
    }
  });
});

describe("injectTextMetadata — chunk ordering", () => {
  it("tEXt chunk appears before IDAT chunk", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    const chunks = await parsePngChunks(result);
    const textIdx = chunks.findIndex((c) => c.type === "tEXt");
    const idatIdx = chunks.findIndex((c) => c.type === "IDAT");
    expect(textIdx).toBeGreaterThan(-1);
    expect(idatIdx).toBeGreaterThan(-1);
    expect(textIdx).toBeLessThan(idatIdx);
  });

  it("tEXt chunk appears after IHDR chunk", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    const chunks = await parsePngChunks(result);
    const ihdrIdx = chunks.findIndex((c) => c.type === "IHDR");
    const textIdx = chunks.findIndex((c) => c.type === "tEXt");
    expect(ihdrIdx).toBeGreaterThan(-1);
    expect(textIdx).toBeGreaterThan(ihdrIdx);
  });

  it("IEND chunk is still last", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    const chunks = await parsePngChunks(result);
    expect(chunks[chunks.length - 1].type).toBe("IEND");
  });
});

describe("injectTextMetadata — CRC correctness", () => {
  it("tEXt chunk has a valid CRC", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    const chunks = await parsePngChunks(result);
    const textChunk = chunks.find((c) => c.type === "tEXt");
    expect(textChunk).toBeDefined();
    const valid = await verifyChunkCrc(result, textChunk!);
    expect(valid).toBe(true);
  });

  it("all original chunk CRCs are preserved", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Title: "Test" });
    const chunks = await parsePngChunks(result);
    for (const chunk of chunks.filter((c) => c.type !== "tEXt")) {
      const valid = await verifyChunkCrc(result, chunk);
      expect(valid).toBe(true);
    }
  });
});

describe("injectTextMetadata — round-trip kv recovery", () => {
  it("single key-value pair round-trips correctly", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Domain: "family" });
    const chunks = await parsePngChunks(result);
    const textChunk = chunks.find((c) => c.type === "tEXt");
    expect(textChunk).toBeDefined();
    const { keyword, text } = parseTextChunkData(textChunk!.data);
    expect(keyword).toBe("Domain");
    expect(text).toBe("family");
  });

  it("multiple kv pairs all appear as tEXt chunks", async () => {
    const kv = {
      Domain: "family",
      Models: "claude-opus-4-6,gpt-4o",
      "Generated-At": "2026-05-07T00:07:50.238646Z",
    };
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, kv);
    const chunks = await parsePngChunks(result);
    const textChunks = chunks.filter((c) => c.type === "tEXt");
    expect(textChunks).toHaveLength(3);

    const recovered: Record<string, string> = {};
    for (const tc of textChunks) {
      const { keyword, text } = parseTextChunkData(tc.data);
      recovered[keyword] = text;
    }
    expect(recovered["Domain"]).toBe("family");
    expect(recovered["Models"]).toBe("claude-opus-4-6,gpt-4o");
    expect(recovered["Generated-At"]).toBe("2026-05-07T00:07:50.238646Z");
  });

  it("full LSB metadata set round-trips", async () => {
    const kv = {
      Title: "Cognitive Structure Lab - family domain - MDS",
      Author: "Cognitive Structure Lab",
      Source: "cogstructurelab.com",
      Software: "LSB Dashboard v0.5.0",
      Domain: "family",
      Models: "claude-opus-4-6,gpt-4o-2025-01",
      "Analysis-Version": "0.2",
      "Generated-At": "2026-05-07T00:07:50.238646Z",
    };
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, kv);
    const chunks = await parsePngChunks(result);
    const textChunks = chunks.filter((c) => c.type === "tEXt");
    expect(textChunks).toHaveLength(8);

    const recovered: Record<string, string> = {};
    for (const tc of textChunks) {
      const { keyword, text } = parseTextChunkData(tc.data);
      recovered[keyword] = text;
    }
    for (const [k, v] of Object.entries(kv)) {
      expect(recovered[k]).toBe(v);
    }
  });
});

describe("injectTextMetadata — empty kv", () => {
  it("empty kv returns a Blob with the same byte length as input", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, {});
    expect(result.size).toBe(png.size);
  });

  it("empty kv output has identical bytes to input", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, {});
    const inputBuf = await png.arrayBuffer();
    const resultBuf = await result.arrayBuffer();
    expect(new Uint8Array(resultBuf)).toEqual(new Uint8Array(inputBuf));
  });
});

describe("injectTextMetadata — invalid input", () => {
  it("throws on input that is too short to be a PNG", async () => {
    const tiny = new Blob([new Uint8Array([0x89, 0x50])], { type: "image/png" });
    await expect(injectTextMetadata(tiny, { Domain: "family" })).rejects.toThrow(
      /too short/
    );
  });

  it("throws on input with wrong PNG signature", async () => {
    const notPng = new Blob([new Uint8Array(67).fill(0x00)], { type: "image/png" });
    await expect(injectTextMetadata(notPng, { Domain: "family" })).rejects.toThrow(
      /PNG signature/
    );
  });

  it("throws when no IDAT chunk is found", async () => {
    // Construct a buffer with valid PNG signature but no chunks.
    const sig = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]);
    const padded = new Uint8Array(20);
    padded.set(sig, 0);
    const blob = new Blob([padded], { type: "image/png" });
    await expect(injectTextMetadata(blob, { Domain: "family" })).rejects.toThrow(
      /IDAT/
    );
  });
});

// ── Gap-fill tests (T11 tester audit) ─────────────────────────────────────────

describe("injectTextMetadata — keyword truncation at 79 chars (Latin-1 spec)", () => {
  /**
   * PNG tEXt spec (RFC 2083 §11.3.4.3): keyword is 1–79 Latin-1 characters.
   * png-metadata.ts truncates keywords longer than 79 chars with .slice(0, 79).
   * Verify: a 100-char keyword is stored as exactly 79 chars in the chunk.
   */
  it("keyword longer than 79 chars is truncated to 79 chars", async () => {
    const longKey = "K".repeat(100); // 100-char keyword
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { [longKey]: "value" });
    const chunks = await parsePngChunks(result);
    const textChunk = chunks.find((c) => c.type === "tEXt");
    expect(textChunk).toBeDefined();
    const { keyword } = parseTextChunkData(textChunk!.data);
    expect(keyword.length).toBe(79);
    expect(keyword).toBe("K".repeat(79));
  });

  it("keyword of exactly 79 chars is stored verbatim (no truncation)", async () => {
    const exactKey = "K".repeat(79);
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { [exactKey]: "value" });
    const chunks = await parsePngChunks(result);
    const textChunk = chunks.find((c) => c.type === "tEXt");
    expect(textChunk).toBeDefined();
    const { keyword } = parseTextChunkData(textChunk!.data);
    expect(keyword.length).toBe(79);
    expect(keyword).toBe(exactKey);
  });
});

describe("injectTextMetadata — Latin-1 byte masking", () => {
  /**
   * latin1Encode in png-metadata.ts uses `charCodeAt(i) & 0xff`, which masks
   * multi-byte Unicode characters to their low 8 bits.  Verify:
   *   - U+0100 (Ā, "Latin Extended-A") is encoded as 0x00 (masked to low byte).
   *   - U+00E9 (é) encodes as 0xE9 and round-trips correctly.
   */
  it("U+00E9 (é) is preserved in round-trip through Latin-1 encoding", async () => {
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Author: "café" });
    const chunks = await parsePngChunks(result);
    const textChunk = chunks.find((c) => c.type === "tEXt");
    expect(textChunk).toBeDefined();
    // The data bytes for "café": 'c'=0x63, 'a'=0x61, 'f'=0x66, 'é'=0xE9
    const afterNull = textChunk!.data.slice(textChunk!.data.indexOf(0) + 1);
    expect(afterNull[3]).toBe(0xe9); // é encodes as 0xE9
  });

  it("high-codepoint character is masked to low 8 bits by latin1Encode", async () => {
    // U+0141 (Ł) has charCode 0x141; & 0xff = 0x41 = 'A'.
    const png = make1x1Blob();
    const result = await injectTextMetadata(png, { Tag: "Ł" });
    const chunks = await parsePngChunks(result);
    const textChunk = chunks.find((c) => c.type === "tEXt");
    expect(textChunk).toBeDefined();
    const afterNull = textChunk!.data.slice(textChunk!.data.indexOf(0) + 1);
    // 0x141 & 0xFF = 0x41 = 65 = 'A'
    expect(afterNull[0]).toBe(0x41);
  });
});
