Interactive Generator
=====================

Build a cohort flow diagram directly in the browser. Enter your cohort
data as JSON, choose a style and optionally paste TOML overrides. The
preview updates as you type. The resulting diagram can be downloaded as
SVG, PNG or PDF. The Generate button below the inputs forces a manual
refresh.

.. note::

   Please cite `pycohortflow` if you use a generated diagram in
   published work. Cite both the descriptive paper and the specific
   software version used to create the figure. For reproducibility,
   open the Zenodo concept DOI and select the version-specific DOI
   corresponding to the release you used.

   - **Paper** (methodology and design):
     Schwarz, F. (2026). *pycohortflow: Lightweight, customisable
     cohort flow diagrams in Python and JavaScript.* MetaArXiv.
     https://doi.org/10.31222/osf.io/ncya2
   - **Software version** (for reproducibility):
     Schwarz, Friedrich. *Pycohortflow.* Zenodo, 2026.
     https://doi.org/10.5281/zenodo.20052730

.. raw:: html

   <!-- ── Generator UI ──────────────────────────────────────────── -->
   <div id="cfgen-app">

     <!-- Input row -->
     <div class="cfgen-row">
       <div class="cfgen-col cfgen-col-main">
         <label for="cfgen-data"><strong>Cohort data (JSON)</strong></label>
         <textarea id="cfgen-data" rows="18" spellcheck="false"></textarea>
       </div>
       <div class="cfgen-col cfgen-col-side">
         <label for="cfgen-style"><strong>Style</strong></label>
         <select id="cfgen-style">
           <option value="white" selected>White (default)</option>
           <option value="colorful">Colorful</option>
           <option value="minimal">Minimal</option>
         </select>

         <label for="cfgen-title"><strong>Figure title</strong></label>
         <input id="cfgen-title" type="text" placeholder="(optional)">

         <label class="cfgen-cb-label">
           <input id="cfgen-transparent" type="checkbox"> Transparent background
         </label>

         <label for="cfgen-toml"><strong>TOML overrides</strong></label>
         <textarea id="cfgen-toml" rows="6" spellcheck="false"
                   placeholder="[colors]&#10;main_start = &quot;#dbeafe&quot;"></textarea>

         <button id="cfgen-generate" class="cfgen-btn cfgen-btn-primary">Generate</button>
       </div>
     </div>

     <!-- Error -->
     <div id="cfgen-error" class="cfgen-error"></div>

     <!-- Preview -->
     <div id="cfgen-preview" class="cfgen-preview"></div>

     <!-- Export buttons -->
     <div class="cfgen-export-row">
       <button id="cfgen-btn-svg" class="cfgen-btn" disabled>Download SVG</button>
       <button id="cfgen-btn-png" class="cfgen-btn" disabled>Download PNG</button>
       <button id="cfgen-btn-pdf" class="cfgen-btn" disabled>Download PDF</button>
     </div>
   </div>

   <!-- ── Inline module script ──────────────────────────────────── -->
   <script type="module">
     import { plotCfd } from "./_static/js/cohortflow.js";
     import { downloadSVG, downloadPNG, downloadPDF } from "./_static/js/exporter.js";

     const EXAMPLE = [
       { heading: "Registered Patients",
         description: "Total patients registered in database", N: 350 },
       { heading: "Screening",
         description: "Underwent initial screening", N: 150,
         exclusion_description: "Did not meet inclusion criteria" },
       { heading: "Eligible",
         description: "Medically cleared for procedure", N: 120,
         exclusion_description: "Declined to participate / Lost to follow-up" },
       { heading: "Final Analysis", N: 115,
         exclusion_description: "Data incomplete" },
     ];

     const $ = (id) => document.getElementById(id);
     const dataEl    = $("cfgen-data");
     const styleEl   = $("cfgen-style");
     const titleEl   = $("cfgen-title");
     const transpEl  = $("cfgen-transparent");
     const tomlEl    = $("cfgen-toml");
     const genBtn    = $("cfgen-generate");
     const errorEl   = $("cfgen-error");
     const previewEl = $("cfgen-preview");
     const btnSVG    = $("cfgen-btn-svg");
     const btnPNG    = $("cfgen-btn-png");
     const btnPDF    = $("cfgen-btn-pdf");

     let currentSVG = null;

     function showError(msg) { errorEl.textContent = msg; errorEl.style.display = "block"; }
     function hideError()    { errorEl.textContent = ""; errorEl.style.display = "none"; }
     function setExport(on)  {
       [btnSVG, btnPNG, btnPDF].forEach(b => { b.disabled = !on; b.style.opacity = on ? 1 : 0.4; });
     }

     // Parse the data textarea. Accepts two shapes:
     //
     //   1. Bare list (legacy):              [ {...}, {...} ]
     //   2. Envelope (pycohortflow >= 0.1.4): { "_meta": {...}, "data": [...] }
     //
     // Returns { data, meta } on success, null on error (and sets the
     // error banner via showError).
     function parseCohortInput() {
       let parsed;
       try { parsed = JSON.parse(dataEl.value); }
       catch (e) { showError("Invalid JSON: " + e.message); return null; }

       let data, meta = null;
       if (Array.isArray(parsed)) {
         data = parsed;
       } else if (parsed && typeof parsed === "object" && Array.isArray(parsed.data)) {
         data = parsed.data;
         meta = parsed._meta || null;
       } else {
         showError("Data must be a JSON array or an envelope object with a 'data' array.");
         return null;
       }

       if (!data.length) { showError("Data must be non-empty."); return null; }
       // Per-node validation, mirroring the Python guards in cfd.py so
       // both runtimes reject the same inputs with the same diagnosis.
       for (let i = 0; i < data.length; i++) {
         if (typeof data[i].N !== "number") {
           showError("Node " + i + ' is missing a numeric "N" field.'); return null;
         }
         if (data[i].N < 0) {
           showError("Node " + i + " has a negative N value (" + data[i].N + ").");
           return null;
         }
         if (i > 0 && data[i].N > data[i - 1].N) {
           showError(
             "Node " + i + " has more patients (" + data[i].N +
             ") than the previous step (" + data[i - 1].N + ")."
           );
           return null;
         }
       }
       return { data, meta };
     }

     // Track the last-applied envelope by its _meta.exported_at value.
     // When generate() sees a different value, it auto-populates the
     // title and transparent inputs from the envelope's _meta block.
     // This handles BOTH paste events and programmatic loads (e.g. a
     // future "Load file" button assigning to dataEl.value), without
     // overwriting manual edits during normal typing/re-renders.
     const NEVER_SEEN = Symbol("never");
     let lastSeenExportedAt = NEVER_SEEN;

     async function generate() {
       hideError();
       const parsed = parseCohortInput();
       if (!parsed) return;

       // Auto-populate from a fresh envelope's _meta block. The
       // freshness key is _meta.exported_at; matching previous value
       // means the user is editing or just re-rendering, so we leave
       // their title/transparent inputs alone.
       if (parsed.meta) {
         const at = parsed.meta.exported_at ?? null;
         if (at !== lastSeenExportedAt) {
           lastSeenExportedAt = at;
           if ("figure_title" in parsed.meta) {
             titleEl.value = parsed.meta.figure_title || "";
           }
           if (typeof parsed.meta.transparent === "boolean") {
             transpEl.checked = parsed.meta.transparent;
           }
         }
       }

       try {
         const svg = await plotCfd(parsed.data, {
           style: styleEl.value,
           figureTitle: titleEl.value.trim() || null,
           transparent: transpEl.checked,
           customToml: tomlEl.value.trim() || null,
           basePath: "_static",
         });
         previewEl.innerHTML = "";
         previewEl.appendChild(svg);
         currentSVG = svg;
         setExport(true);
       } catch (e) { showError(e.message); currentSVG = null; setExport(false); }
     }

     dataEl.value = JSON.stringify(EXAMPLE, null, 2);

     // Auto-update: re-render whenever any input changes. Text fields
     // are debounced so we don't re-render on every keystroke; the
     // style select and transparent checkbox fire immediately. The
     // Generate button remains for an explicit refresh.
     function debounce(fn, ms) {
       let t = null;
       return function (...args) {
         clearTimeout(t);
         t = setTimeout(() => fn.apply(this, args), ms);
       };
     }
     const generateDebounced = debounce(generate, 300);

     dataEl.addEventListener("input", generateDebounced);
     tomlEl.addEventListener("input", generateDebounced);
     titleEl.addEventListener("input", generateDebounced);
     styleEl.addEventListener("change", generate);
     transpEl.addEventListener("change", generate);

     genBtn.addEventListener("click", generate);
     btnSVG.addEventListener("click", () => currentSVG && downloadSVG(currentSVG));
     btnPNG.addEventListener("click", () => currentSVG && downloadPNG(currentSVG));
     btnPDF.addEventListener("click", () => currentSVG && downloadPDF(currentSVG));
     generate();
   </script>
