import { blobCount, growBlobs, hexToRgb } from "./blobs.js";
import { BACKGROUND, FPS, MAX_COUNT, SCALE } from "./config.js";
import { bindFullscreenTriangle, createProgram, loadShader } from "./webgl.js";

// starts the blob animation on a canvas
const startBlobs = async (canvas) => {
  const gl = canvas.getContext("webgl", { antialias: false, alpha: false });
  // without webgl, the hero background color is shown instead
  if (!gl) return;

  const [vertex, fragment] = await Promise.all([
    loadShader("blobs.vert"),
    loadShader("blobs.frag"),
  ]);
  if (!vertex || !fragment) return;
  // the maximum blob count sizes the uniform arrays, so it is set at compile time
  const program = createProgram(
    gl,
    vertex,
    `#define MAX_BLOBS ${MAX_COUNT}\n${fragment}`,
  );
  if (!program) return;
  gl.useProgram(program);
  bindFullscreenTriangle(gl, program, "a_position");

  const uniform = (name) => gl.getUniformLocation(program, name);
  const background = getComputedStyle(document.documentElement)
    .getPropertyValue("--hero-bg")
    .trim();
  gl.uniform3fv(uniform("u_background"), hexToRgb(background || BACKGROUND));
  const resolution = uniform("u_resolution");
  const time = uniform("u_time");
  const count = uniform("u_count");
  const colors = uniform("u_colors");
  const positions = uniform("u_blobs");

  // uploads enough blobs to cover the given aspect ratio
  const blobs = [];
  const setBlobs = (aspect) => {
    const n = blobCount(aspect);
    if (n > blobs.length) {
      growBlobs(blobs, n);
      gl.uniform3fv(colors, blobs.flatMap((b) => hexToRgb(b.hex)));
      gl.uniform4fv(
        positions,
        blobs.flatMap((b) => [b.x, b.y, b.radius, b.phase]),
      );
    }
    gl.uniform1i(count, n);
  };

  const draw = (seconds) => {
    gl.uniform1f(time, seconds);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  };

  // random starting time, so the first frame differs on each load
  const offset = Math.random() * 1000;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const resize = () => {
    canvas.width = Math.max(1, Math.round(canvas.clientWidth * SCALE));
    canvas.height = Math.max(1, Math.round(canvas.clientHeight * SCALE));
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform2f(resolution, canvas.width, canvas.height);
    setBlobs(canvas.width / canvas.height);
    draw(offset + performance.now() / 1000);
  };
  new ResizeObserver(resize).observe(canvas);

  let last = 0;
  const loop = (now) => {
    requestAnimationFrame(loop);
    if (reducedMotion.matches || now - last < 1000 / FPS) return;
    last = now;
    draw(offset + now / 1000);
  };
  requestAnimationFrame(loop);
};

// modules are deferred, so the canvas is already in the page
const canvas = document.getElementById("blobs");
if (canvas) startBlobs(canvas);
