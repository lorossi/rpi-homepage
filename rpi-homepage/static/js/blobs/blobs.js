import {
  COLORS,
  MAX_COUNT,
  RADIUS_MAX,
  RADIUS_MIN,
  SPACING,
} from "./config.js";

// converts a hex color to an [r, g, b] array in [0, 1]
export const hexToRgb = (hex) => {
  const value = parseInt(hex.replace("#", ""), 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255].map(
    (c) => c / 255,
  );
};

// number of blobs needed to cover a hero with the given aspect ratio
export const blobCount = (aspect) =>
  Math.min(MAX_COUNT, Math.ceil(aspect / SPACING) + 1);

// picks a random color, different from the previous one
const pickColor = (previous) => {
  const choices = COLORS.filter((color) => color != previous);
  return choices[Math.floor(Math.random() * choices.length)];
};

// adds blobs to the list until it has the given count, keeping the existing
// ones; positions are in hero heights, starting from the left edge
export const growBlobs = (blobs, count) => {
  while (blobs.length < count) {
    const i = blobs.length;
    blobs.push({
      hex: pickColor(blobs[i - 1]?.hex),
      x: (i - 0.3 + Math.random() * 0.6) * SPACING,
      y: 0.15 + Math.random() * 0.7,
      radius: RADIUS_MIN + Math.random() * (RADIUS_MAX - RADIUS_MIN),
      phase: Math.random() * Math.PI * 2,
    });
  }
  return blobs;
};
