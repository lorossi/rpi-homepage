// MAX_BLOBS is defined by main.js, before compiling
precision mediump float;

uniform vec2 u_resolution;
uniform float u_time;
uniform vec3 u_background;
// number of blobs in use, at most MAX_BLOBS
uniform int u_count;
uniform vec3 u_colors[MAX_BLOBS];
// xy: anchor in hero heights, z: radius, w: phase
uniform vec4 u_blobs[MAX_BLOBS];

// cheap per-pixel noise, used as dithering to avoid banding
float hash(vec2 p) {
  return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
  // in hero heights, from the bottom left corner
  vec2 p = gl_FragCoord.xy / u_resolution.y;

  // warp the space, so blobs are not perfect circles
  float t = u_time;
  p += 0.06 * vec2(sin(p.y * 4.0 + t * 0.35), cos(p.x * 3.0 - t * 0.27));

  vec3 color = vec3(0.0);
  float total = 0.0;
  // loops need a constant bound, so stop early on the blobs in use
  for (int i = 0; i < MAX_BLOBS; i++) {
    if (i >= u_count) break;
    vec4 blob = u_blobs[i];
    vec2 center = blob.xy;
    // slow orbit around the anchor
    center += 0.12 * vec2(
      sin(t * 0.11 + blob.w),
      cos(t * 0.09 + blob.w * 1.7)
    );
    vec2 d = p - center;
    float w = exp(-dot(d, d) / (blob.z * blob.z));
    color += u_colors[i] * w;
    total += w;
  }

  color /= max(total, 1e-4);
  float coverage = smoothstep(0.0, 0.9, total);
  vec3 result = mix(u_background, color, coverage);
  result += (hash(gl_FragCoord.xy + t) - 0.5) / 255.0;
  gl_FragColor = vec4(result, 1.0);
}
