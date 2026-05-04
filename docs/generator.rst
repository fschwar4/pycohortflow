Interactive Generator
=====================

Build a cohort flow diagram directly in the browser. Enter your cohort
data as JSON, choose a style and optionally paste TOML overrides. The
preview updates as you type. The resulting diagram can be downloaded as
SVG, PNG or PDF. The Generate button below the inputs forces a manual
refresh.

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

     async function generate() {
       hideError();
       let data;
       try { data = JSON.parse(dataEl.value); }
       catch (e) { showError("Invalid JSON: " + e.message); return; }
       if (!Array.isArray(data) || !data.length) { showError("Data must be a non-empty JSON array."); return; }
       for (let i = 0; i < data.length; i++) {
         if (typeof data[i].N !== "number") { showError("Node " + i + ' is missing a numeric "N" field.'); return; }
       }
       try {
         const svg = await plotCfd(data, {
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
