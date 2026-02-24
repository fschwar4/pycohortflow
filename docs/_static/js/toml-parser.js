/**
 * Lightweight TOML parser for cohortflow style configs.
 *
 * Supports quoted strings (including hex colours like "#ffffff"),
 * section headers, booleans, and numbers.  Comments start with ``#``
 * but only *outside* of quoted strings.
 */
export function parseTOML(tomlString) {
  const result = {};
  let currentSection = result;

  const lines = tomlString.split(/\r?\n/);

  for (const rawLine of lines) {
    const line = _stripComment(rawLine).trim();

    if (!line) continue;

    // 1. Section header: [section] or [section.subsection]
    const sectionMatch = line.match(/^\[([\w.]+)\]$/);
    if (sectionMatch) {
      const parts = sectionMatch[1].split(".");
      let node = result;
      for (const part of parts) {
        if (!node[part]) node[part] = {};
        node = node[part];
      }
      currentSection = node;
      continue;
    }

    // 2. Key = value
    const kvMatch = line.match(/^([\w]+)\s*=\s*(.*)$/);
    if (!kvMatch) continue;

    const key = kvMatch[1].trim();
    let value = kvMatch[2].trim();

    // Parse basic types
    if (value === "true") {
      value = true;
    } else if (value === "false") {
      value = false;
    } else if (!isNaN(Number(value)) && value !== "") {
      value = Number(value);
    } else if ((value.startsWith('"') && value.endsWith('"')) ||
               (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1);
    }

    currentSection[key] = value;
  }

  return result;
}

/**
 * Strip a trailing comment from a TOML line while respecting quoted strings.
 *
 * Walks the line character-by-character.  A ``#`` that appears outside of
 * a single- or double-quoted string marks the start of a comment; everything
 * from that position onward is removed.
 */
function _stripComment(line) {
  let inSingle = false;
  let inDouble = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"' && !inSingle) {
      inDouble = !inDouble;
    } else if (ch === "'" && !inDouble) {
      inSingle = !inSingle;
    } else if (ch === '#' && !inSingle && !inDouble) {
      return line.substring(0, i);
    }
  }
  return line;
}