// palette of the blobs, as hex colors
export const COLORS = ["#e0653f", "#ffb454", "#2a8fa6", "#c04a8c", "#7a5ad6"];
// distance between blobs, as a fraction of the hero height; wider heroes get
// more blobs, so the coverage does not depend on the aspect ratio
export const SPACING = 1.1;
// upper bound on the number of blobs, sizes the shader arrays
export const MAX_COUNT = 16;
// blob radius range, as a fraction of the hero height
export const RADIUS_MIN = 0.5;
export const RADIUS_MAX = 0.75;
// the shader output is blurry, so it is rendered at a fraction of the size
export const SCALE = 0.25;
// frame rate cap, to keep the load low
export const FPS = 30;
// fallback background, used if the --hero-bg css variable is missing
export const BACKGROUND = "#12161d";
