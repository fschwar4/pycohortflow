import { loadStyleConfig } from "./config.js";

const SCALE = 100;

// --- Utilities ---

/**
 * Robustly resolves any CSS color string (hex, named, rgb) to a Hex string
 * using the browser's native canvas engine.
 */
function colorToHex(color) {
  const ctx = document.createElement("canvas").getContext("2d");
  ctx.fillStyle = "#ffffff"; // Default fallback
  ctx.fillStyle = color;
  return ctx.fillStyle;
}

function hexToRgb(hex) {
  const clean = colorToHex(hex).replace(/^#/, "");
  const bigint = parseInt(clean, 16);
  return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
}

function rgbToHex([r, g, b]) {
  return "#" + [r, g, b].map(x => Math.round(x).toString(16).padStart(2, "0")).join("");
}

export function resolveColor(value, fallback) {
  if (!value) return colorToHex(fallback);
  return colorToHex(value);
}

export function gradientPalette(start, end, n) {
  const startHex = resolveColor(start, "#ffffff");
  const endHex = resolveColor(end, "#ffffff");

  if (n <= 1) return [startHex];

  const s = hexToRgb(startHex);
  const e = hexToRgb(endHex);

  return Array.from({ length: n }, (_, i) => {
    const t = i / (n - 1);
    return rgbToHex([
      s[0] + (e[0] - s[0]) * t,
      s[1] + (e[1] - s[1]) * t,
      s[2] + (e[2] - s[2]) * t
    ]);
  });
}

export function wrapLines(text, width) {
  if (!text) return [];
  const words = text.split(/\s+/);
  const lines = [];
  let current = words[0] || "";
  for (let i = 1; i < words.length; i++) {
    if (current.length + 1 + words[i].length <= width) current += " " + words[i];
    else { lines.push(current); current = words[i]; }
  }
  if (current) lines.push(current);
  return lines;
}

// --- SVG Drawing ---
function svgEl(tag, attrs = {}) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function drawArrow(parent, x1, y1, x2, y2, width, headSize) {
  const dx = x2 - x1, dy = y2 - y1;
  const len = Math.sqrt(dx * dx + dy * dy);
  if (len < 0.1) return;

  const ux = dx / len, uy = dy / len;
  const baseX = x2 - ux * headSize, baseY = y2 - uy * headSize;
  const perpX = -uy * headSize * 0.4, perpY = ux * headSize * 0.4;

  const g = svgEl("g", { stroke: "#000", fill: "#000" });
  g.appendChild(svgEl("line", { x1, y1, x2: baseX, y2: baseY, "stroke-width": width }));
  g.appendChild(svgEl("polygon", {
    points: `${x2},${y2} ${baseX + perpX},${baseY + perpY} ${baseX - perpX},${baseY - perpY}`,
    stroke: "none"
  }));
  parent.appendChild(g);
}

// --- Render ---
export async function plotCohortFlowDiagram(data, options = {}) {
  const cfg = await loadStyleConfig(options);
  return renderInternal(data, cfg, options);
}

function renderInternal(data, cfg, { figureTitle, transparent, mainPalette, exclusionPalette }) {
  const { layout, box_geometry: geom, text: txt, lines, colors } = cfg;
  const S = SCALE;

  const mColors = mainPalette || gradientPalette(colors.main_start, colors.main_end, data.length);
  const eColors = exclusionPalette || gradientPalette(colors.exclusion_start, colors.exclusion_end, data.length);

  // 1. Process Nodes
  const nodes = data.map((d, i) => {
    const nPrev = i > 0 ? data[i-1].N : d.N;
    const exclN = nPrev - d.N;
    const tLines = wrapLines(d.heading || `Step ${i+1}`, layout.main_title_width);
    const bLines = [`(n = ${d.N})`, ...(d.description ? ["", ...wrapLines(d.description, layout.main_text_width)] : [])];
    const eLines = [...wrapLines(d.exclusion_description || "Excluded", layout.exclusion_text_width), `(n = ${exclN})`];

    const mainH = Math.max(geom.min_main_height,
      geom.padding + (tLines.length * geom.title_line_height) + geom.title_body_gap + (bLines.length * geom.body_line_height));
    const exclH = Math.max(geom.min_exclusion_height, geom.padding + (eLines.length * geom.body_line_height));

    return {
      ...d, exclN, tLines, bLines, eLines, mainH, exclH,
      color: resolveColor(d.color, mColors[i]),
      exclColor: resolveColor(d.exclusion_color, eColors[i])
    };
  });

  // 2. Layout
  const gaps = nodes.slice(1).map((n, i) =>
    Math.max(layout.base_gap, n.exclN > 0 ? n.exclH + 2 * geom.clearance : 0));

  const yCenters = [layout.top_margin + nodes[0].mainH / 2];
  for (let i = 1; i < nodes.length; i++) {
    yCenters.push(yCenters[i-1] + nodes[i-1].mainH/2 + gaps[i-1] + nodes[i].mainH/2);
  }

  // Convert title_pad (Matplotlib points) to abstract layout units (≈ inches)
  const titleH = figureTitle ? (cfg.figure.title_pad ?? 20) / 72 : 0;
  const totalH = yCenters[nodes.length-1] + nodes[nodes.length-1].mainH/2 + layout.bottom_margin + titleH;

  // Calculate Widths
  const centerX = 0;
  const exclX = centerX + layout.main_box_width/2 + layout.side_gap + layout.exclusion_box_width/2;
  const leftX = centerX - layout.main_box_width/2 - layout.x_padding;
  const rightX = exclX + layout.exclusion_box_width/2 + layout.x_padding;

  const wPx = (rightX - leftX) * S;
  const hPx = totalH * S;

  const tx = (v) => (v - leftX) * S;
  const ty = (v) => (v + titleH) * S;

  // 3. Draw
  const svg = svgEl("svg", { width: wPx, height: hPx, viewBox: `0 0 ${wPx} ${hPx}`, xmlns: "http://www.w3.org/2000/svg" });
  if (!transparent) svg.appendChild(svgEl("rect", { width: wPx, height: hPx, fill: "#fff" }));

  if (figureTitle) {
    const t = svgEl("text", { x: wPx/2, y: 30, "text-anchor": "middle", "font-weight": "bold", "font-size": 24, "font-family": "sans-serif" });
    t.textContent = figureTitle;
    svg.appendChild(t);
  }

  nodes.forEach((n, i) => {
    const yc = yCenters[i];

    // Main Box
    const boxG = svgEl("g");
    boxG.appendChild(svgEl("rect", {
      x: tx(centerX - layout.main_box_width/2), y: ty(yc - n.mainH/2),
      width: layout.main_box_width * S, height: n.mainH * S,
      rx: geom.corner_radius * S, ry: geom.corner_radius * S,
      fill: n.color, stroke: "#000", "stroke-width": lines.box_linewidth
    }));
    svg.appendChild(boxG);

    // Text Helper
    const text = (lines, x, startY, sz, weight="normal", style="normal") => {
      const g = svgEl("g", { "font-family": "Arial, sans-serif", "text-anchor": "middle", fill: "#000" });
      lines.forEach((l, idx) => {
        const t = svgEl("text", {
          x: tx(x), y: ty(startY) + idx * sz * 1.2,
          "font-size": sz, "font-weight": weight, "font-style": style, "dominant-baseline": "hanging"
        });
        t.textContent = l;
        g.appendChild(t);
      });
      svg.appendChild(g);
    };

    const tSz = txt.fontsize_title * 1.33;
    const bSz = txt.fontsize_main * 1.33;

    const textTop = yc - n.mainH/2 + geom.text_top_padding;
    text(n.tLines, centerX, textTop, tSz, "bold");
    text(n.bLines, centerX, textTop + (n.tLines.length * tSz * 1.2 / S) + geom.title_body_gap, bSz);

    // Arrows & Exclusions
    if (i > 0) {
      const prevY = yCenters[i-1] + nodes[i-1].mainH/2;
      const currY = yc - n.mainH/2;
      drawArrow(svg, tx(centerX), ty(prevY), tx(centerX), ty(currY), lines.connector_linewidth, lines.arrow_mutation_scale/2);

      if (n.exclN > 0) {
        const midY = (prevY + currY) / 2;
        const eLeft = exclX - layout.exclusion_box_width/2;

        // Excl Box
        svg.appendChild(svgEl("rect", {
          x: tx(eLeft), y: ty(midY - n.exclH/2),
          width: layout.exclusion_box_width * S, height: n.exclH * S,
          rx: geom.corner_radius * S, ry: geom.corner_radius * S,
          fill: n.exclColor, stroke: "#000", "stroke-width": lines.box_linewidth
        }));

        // Junction & Arrow
        svg.appendChild(svgEl("circle", { cx: tx(centerX), cy: ty(midY), r: 4, fill: "#000" }));
        drawArrow(svg, tx(centerX), ty(midY), tx(eLeft), ty(midY), lines.connector_linewidth, lines.arrow_mutation_scale/2);

        // Excl Text
        const eSz = txt.fontsize_exclusion * 1.33;
        const eTextH = n.eLines.length * eSz * 1.2 / S;
        text(n.eLines, exclX, midY - eTextH/2, eSz, "normal", "italic");
      }
    }
  });

  return svg;
}