/**
 * PNG tEXt chunk injector — pure DOM/stdlib, no third-party dependencies.
 *
 * Splices one or more tEXt chunks into a PNG Blob, inserting them immediately
 * before the first IDAT chunk per PNG spec (RFC 2083 §11.3.4.3 ordering).
 *
 * tEXt chunk format (PNG spec §11.3.4.3):
 *   [Length: u32 BE]                   — byte count of data field (keyword + null + text)
 *   [Type:   4 bytes ASCII "tEXt"]
 *   [Data:   keyword (Latin-1, 1–79 bytes) + NUL (1 byte) + text (Latin-1, 0–N bytes)]
 *   [CRC:    u32 BE]                   — CRC-32 over Type field + Data field
 *
 * CRC-32 uses the standard CCITT-32 polynomial (0xEDB88320, reflected/LSB-first form),
 * identical to the polynomial PNG uses for all its chunk CRCs (RFC 2083 §B).
 *
 * No third-party PNG libraries used (forbidden per task spec).
 *
 * Source: docs/status/2026-05-09-phase5-architect-plan.md §4 T11
 *         PNG spec (RFC 2083) §§11.3.4.3, B
 */

// ── CRC-32 table (CCITT-32, reflected polynomial 0xEDB88320) ─────────────────

/**
 * Precomputed CRC-32 lookup table.
 * Generated once at module load. Standard PNG CRC algorithm per RFC 2083 §B.
 */
const CRC_TABLE: Uint32Array = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      if (c & 1) {
        c = 0xedb88320 ^ (c >>> 1);
      } else {
        c = c >>> 1;
      }
    }
    table[n] = c;
  }
  return table;
})();

/**
 * Compute CRC-32 over a Uint8Array slice.
 *
 * @param data  Byte array.
 * @param crc   Initial CRC value (0xffffffff for a fresh computation).
 * @returns     CRC-32 value (to be XOR'd with 0xffffffff to finalise).
 */
function crc32Update(data: Uint8Array, crc: number): number {
  let c = crc;
  for (let i = 0; i < data.length; i++) {
    c = CRC_TABLE[(c ^ data[i]) & 0xff] ^ (c >>> 8);
  }
  return c;
}

/**
 * Compute final CRC-32 for a Uint8Array.
 * Returns a 32-bit unsigned integer.
 */
function crc32(data: Uint8Array): number {
  return (crc32Update(data, 0xffffffff) ^ 0xffffffff) >>> 0;
}

// ── PNG constants ─────────────────────────────────────────────────────────────

/** Standard PNG file signature (8 bytes). */
const PNG_SIGNATURE = new Uint8Array([137, 80, 78, 71, 13, 10, 26, 10]);

/** ASCII codes for chunk type names. */
const CHUNK_IDAT = [73, 68, 65, 84]; // "IDAT"
const CHUNK_TEXT = [116, 69, 88, 116]; // "tEXt"

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Write a big-endian u32 into a DataView at a given byte offset. */
function writeU32BE(view: DataView, offset: number, value: number): void {
  view.setUint32(offset, value >>> 0, false /* big-endian */);
}

/** Read a big-endian u32 from a DataView at a given byte offset. */
function readU32BE(view: DataView, offset: number): number {
  return view.getUint32(offset, false);
}

/** Latin-1 encode a string into a Uint8Array (one byte per code point, 0x00–0xFF). */
function latin1Encode(str: string): Uint8Array {
  const bytes = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) {
    bytes[i] = str.charCodeAt(i) & 0xff;
  }
  return bytes;
}

// ── tEXt chunk builder ────────────────────────────────────────────────────────

/**
 * Build a complete PNG tEXt chunk (length + type + data + crc).
 *
 * @param keyword  Keyword: 1–79 Latin-1 characters, no NUL.
 * @param text     Value: Latin-1 text (may be empty; no NUL allowed).
 * @returns        Uint8Array representing the full chunk (length-fieldable in host PNG).
 */
function buildTextChunk(keyword: string, text: string): Uint8Array {
  // Truncate keyword to 79 characters per PNG spec.
  const kw = keyword.slice(0, 79);

  const kwBytes = latin1Encode(kw);
  const textBytes = latin1Encode(text);

  // Data = keyword + NUL + text
  const dataLength = kwBytes.length + 1 + textBytes.length;
  const data = new Uint8Array(dataLength);
  data.set(kwBytes, 0);
  data[kwBytes.length] = 0; // NUL separator
  data.set(textBytes, kwBytes.length + 1);

  // Type bytes: "tEXt"
  const typeBytes = new Uint8Array(CHUNK_TEXT);

  // CRC is computed over type + data.
  const crcInput = new Uint8Array(4 + dataLength);
  crcInput.set(typeBytes, 0);
  crcInput.set(data, 4);
  const crcValue = crc32(crcInput);

  // Total chunk: 4 (length) + 4 (type) + N (data) + 4 (crc) = 12 + N bytes.
  const chunk = new Uint8Array(12 + dataLength);
  const view = new DataView(chunk.buffer);
  writeU32BE(view, 0, dataLength); // length field = data only
  chunk.set(typeBytes, 4);         // type
  chunk.set(data, 8);              // data
  writeU32BE(view, 8 + dataLength, crcValue); // crc
  return chunk;
}

// ── Main export ───────────────────────────────────────────────────────────────

/**
 * Splice tEXt chunks into a PNG Blob with the given key-value pairs.
 *
 * The chunks are inserted immediately before the first IDAT chunk, which
 * is the correct position for ancillary metadata per the PNG chunk ordering
 * rules (RFC 2083 §5.6 and §11.3.4).
 *
 * If `kv` is empty, returns the input Blob unchanged.
 * Throws if the Blob does not have a valid PNG signature.
 *
 * @param blob  Input PNG Blob.
 * @param kv    Key-value pairs to embed as tEXt chunks.
 * @returns     A new Blob with the tEXt chunks spliced in.
 */
export async function injectTextMetadata(
  blob: Blob,
  kv: Record<string, string>
): Promise<Blob> {
  const keys = Object.keys(kv);

  // Fast path: nothing to inject.
  if (keys.length === 0) {
    return blob;
  }

  const buffer = await blob.arrayBuffer();
  const bytes = new Uint8Array(buffer);
  const view = new DataView(buffer);

  // ── Validate PNG signature ────────────────────────────────────────────────

  if (bytes.length < 8) {
    throw new Error("injectTextMetadata: input is too short to be a valid PNG.");
  }
  for (let i = 0; i < 8; i++) {
    if (bytes[i] !== PNG_SIGNATURE[i]) {
      throw new Error(
        "injectTextMetadata: input does not have a valid PNG signature."
      );
    }
  }

  // ── Walk chunks to find the first IDAT ───────────────────────────────────

  let offset = 8; // Skip the 8-byte signature.
  let idatOffset = -1;

  while (offset + 12 <= bytes.length) {
    const dataLength = readU32BE(view, offset);
    // Chunk type is 4 bytes at offset + 4.
    const isIdat =
      bytes[offset + 4] === CHUNK_IDAT[0] &&
      bytes[offset + 5] === CHUNK_IDAT[1] &&
      bytes[offset + 6] === CHUNK_IDAT[2] &&
      bytes[offset + 7] === CHUNK_IDAT[3];

    if (isIdat) {
      idatOffset = offset;
      break;
    }

    // Advance past this chunk: 4 (length) + 4 (type) + dataLength (data) + 4 (crc).
    offset += 12 + dataLength;
  }

  if (idatOffset === -1) {
    throw new Error(
      "injectTextMetadata: no IDAT chunk found — PNG may be malformed."
    );
  }

  // ── Build tEXt chunks ─────────────────────────────────────────────────────

  const textChunks: Uint8Array[] = keys.map((key) =>
    buildTextChunk(key, kv[key])
  );

  const totalTextBytes = textChunks.reduce((sum, c) => sum + c.length, 0);

  // ── Reassemble: prefix + tEXt chunks + suffix ─────────────────────────────

  // prefix = everything from byte 0 up to (not including) the IDAT chunk.
  const prefix = bytes.subarray(0, idatOffset);
  // suffix = everything from the IDAT chunk to the end.
  const suffix = bytes.subarray(idatOffset);

  const result = new Uint8Array(prefix.length + totalTextBytes + suffix.length);
  let pos = 0;
  result.set(prefix, pos);
  pos += prefix.length;
  for (const chunk of textChunks) {
    result.set(chunk, pos);
    pos += chunk.length;
  }
  result.set(suffix, pos);

  return new Blob([result], { type: "image/png" });
}
