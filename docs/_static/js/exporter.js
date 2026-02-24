/**
 * Handles exporting the generated SVG to file.
 *
 * - SVG: direct serialisation
 * - PNG: SVG → data URI → Image → Canvas → Blob
 * - PDF: loads jsPDF UMD from CDN (self-contained build), then Canvas → PDF
 *
 * Both PNG and PDF use data URIs (not Blob URLs) for the SVG → Canvas step
 * to avoid tainted-canvas security restrictions.
 */

// ─── Shared helpers ─────────────────────────────────────────────────────────

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Render an SVG element onto a Canvas using a data URI.
 * Data URIs avoid the tainted-canvas problem that Blob URLs cause.
 */
function svgToCanvas(svgElement, scale = 2) {
  const width = parseInt(svgElement.getAttribute("width")) || 800;
  const height = parseInt(svgElement.getAttribute("height")) || 600;

  const canvas = document.createElement("canvas");
  canvas.width = width * scale;
  canvas.height = height * scale;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.scale(scale, scale);

  const svgStr = new XMLSerializer().serializeToString(svgElement);
  const dataUri = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgStr);
  const img = new Image();

  return new Promise((resolve, reject) => {
    img.onload = () => {
      ctx.drawImage(img, 0, 0, width, height);
      resolve({ canvas, width, height });
    };
    img.onerror = () => reject(new Error("Failed to render SVG to canvas"));
    img.src = dataUri;
  });
}

/**
 * Load a script by URL (returns a Promise). Skips if already loaded.
 */
function loadScript(src) {
  return new Promise((resolve, reject) => {
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.onload = resolve;
    script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
    document.head.appendChild(script);
  });
}

// ─── SVG Export ─────────────────────────────────────────────────────────────

export function downloadSVG(svgElement) {
  const serializer = new XMLSerializer();
  let source = serializer.serializeToString(svgElement);

  if (!source.match(/^<svg[^>]+xmlns="http:\/\/www\.w3\.org\/2000\/svg"/)) {
    source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  }

  const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
  triggerDownload(blob, "cohort_flow.svg");
}

// ─── PNG Export ─────────────────────────────────────────────────────────────

export async function downloadPNG(svgElement) {
  try {
    const { canvas } = await svgToCanvas(svgElement, 2);
    canvas.toBlob((blob) => {
      if (blob) triggerDownload(blob, "cohort_flow.png");
    }, "image/png");
  } catch (e) {
    console.error("PNG export failed:", e);
    alert("PNG export failed. See browser console for details.");
  }
}

// ─── PDF Export ─────────────────────────────────────────────────────────────

// Local UMD build (self-contained, all deps bundled, registers window.jspdf).
// Falls back to CDN if local file is missing.
const JSPDF_LOCAL = "_static/js/jspdf.umd.min.js";
const JSPDF_CDN = "https://cdnjs.cloudflare.com/ajax/libs/jspdf/3.0.3/jspdf.umd.min.js";

export async function downloadPDF(svgElement) {
  try {
    // Load jsPDF UMD build if not already available.
    if (!window.jspdf) {
      try {
        await loadScript(JSPDF_LOCAL);
      } catch {
        console.warn("Local jsPDF not found, trying CDN...");
        await loadScript(JSPDF_CDN);
      }
    }

    if (!window.jspdf || !window.jspdf.jsPDF) {
      throw new Error("jsPDF failed to initialise. Check that jspdf.umd.min.js exists.");
    }

    const { canvas, width, height } = await svgToCanvas(svgElement, 2);
    const imgData = canvas.toDataURL("image/png");

    const wMm = width * 0.264583;
    const hMm = height * 0.264583;

    const pdf = new window.jspdf.jsPDF({
      orientation: wMm > hMm ? "l" : "p",
      unit: "mm",
      format: [wMm + 10, hMm + 10],
    });
    pdf.addImage(imgData, "PNG", 5, 5, wMm, hMm);
    pdf.save("cohort_flow.pdf");

  } catch (e) {
    console.error("PDF export failed:", e);
    alert("PDF export failed: " + e.message);
  }
}
