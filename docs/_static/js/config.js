import { parseTOML } from "./toml-parser.js";

const BUILTIN_STYLES = {
  white: "styles/default_style_white.toml",
  colorful: "styles/default_style_colorful.toml",
  minimal: "styles/default_style_minimal.toml",
};

const FALLBACK_CONFIG = Object.freeze({
  figure: {
    figsize_width: 12, figsize_height: 8, dpi: 200,
    title_fontsize: 16, title_fontweight: "bold", title_pad: 20,
  },
  layout: {
    main_title_width: 26, main_text_width: 34, exclusion_text_width: 30,
    main_box_width: 2.8, exclusion_box_width: 2.6,
    base_gap: 0.8, side_gap: 1.2, top_margin: 0.8, bottom_margin: 0.8, x_padding: 0.6,
  },
  box_geometry: {
    padding: 0.52, title_line_height: 0.42, body_line_height: 0.33,
    title_body_gap: 0.16, text_top_padding: 0.24,
    min_main_height: 1.6, min_exclusion_height: 1.2,
    clearance: 0.2, corner_radius: 0.05, pad_factor: 0.03,
  },
  text: {
    fontsize_title: 12, fontsize_main: 10, fontsize_exclusion: 9,
    heading_fontweight: "bold",
  },
  lines: {
    box_linewidth: 1, connector_linewidth: 1,
    arrow_mutation_scale: 20, junction_radius: 0.004,
  },
  colors: {
    allow_named_colors: true,
    main_start: "#ffffff", main_end: "#ffffff",
    exclusion_start: "#ffffff", exclusion_end: "#ffffff",
  },
  exclusion: {
    mode: "box",
  },
});

export function recursiveUpdate(base, override) {
  const result = { ...base };
  for (const [key, value] of Object.entries(override)) {
    if (
      value !== null && typeof value === "object" && !Array.isArray(value) &&
      key in result && typeof result[key] === "object"
    ) {
      result[key] = recursiveUpdate(result[key], value);
    } else {
      result[key] = value;
    }
  }
  return result;
}

export async function loadStyleConfig({ style = "white", customToml = null, customConfig = null, basePath = "" } = {}) {
  // 1. Try to fetch external TOML
  let config = { ...FALLBACK_CONFIG };
  
  if (style in BUILTIN_STYLES) {
    try {
      const url = basePath ? `${basePath.replace(/\/$/, "")}/${BUILTIN_STYLES[style]}` : BUILTIN_STYLES[style];
      const response = await fetch(url);
      if (response.ok) {
        const tomlText = await response.text();
        config = recursiveUpdate(config, parseTOML(tomlText));
      } else {
        throw new Error("Style file fetch failed");
      }
    } catch (e) {
      console.warn("Falling back to internal default styles:", e);
      config = loadStyleConfigSync({ style });
    }
  }

  // 2. Apply user overrides
  if (customToml) {
    try {
        config = recursiveUpdate(config, parseTOML(customToml));
    } catch (e) {
        console.error("Error parsing Custom TOML:", e);
    }
  }
  
  if (customConfig) config = recursiveUpdate(config, customConfig);
  return config;
}

export function loadStyleConfigSync({ style = "white", customToml = null, customConfig = null } = {}) {
  let config = JSON.parse(JSON.stringify(FALLBACK_CONFIG));

  if (style === "colorful") {
    config.colors = {
      ...config.colors,
      main_start: "#dff1ff", main_end: "#dff7e8",
      exclusion_start: "#f8cccc", exclusion_end: "#fee8e8",
    };
  }

  if (style === "minimal") {
    config.text = { ...config.text, heading_fontweight: "normal" };
    config.exclusion = { ...config.exclusion, mode: "text" };
  }

  if (customToml) {
      try {
        config = recursiveUpdate(config, parseTOML(customToml));
      } catch (e) { console.error(e); }
  }
  if (customConfig) config = recursiveUpdate(config, customConfig);
  return config;
}