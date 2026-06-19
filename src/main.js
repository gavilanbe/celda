const canvas = document.querySelector("#game");
const ctx = canvas.getContext("2d", { alpha: false });

ctx.imageSmoothingEnabled = false;

const config = await fetchJson("game.config.json");
const heroMeta = await fetchJson(config.hero.metadata);
const heroImage = await loadImage(config.hero.spriteSheet);

const world = {
  tileSize: config.world.tileSize,
  width: 18,
  height: 12,
  solids: new Set(["5,4", "6,4", "7,4", "12,5", "13,5", "3,8", "4,8", "14,8"]),
  decor: [
    { kind: "tree", x: 4, y: 3 },
    { kind: "tree", x: 13, y: 3 },
    { kind: "stone", x: 8, y: 6 },
    { kind: "stone", x: 10, y: 7 },
    { kind: "grass", x: 6, y: 7 },
    { kind: "grass", x: 11, y: 4 },
  ],
};

const hero = {
  x: 8 * world.tileSize,
  y: 6 * world.tileSize,
  speed: 126,
  facing: "down",
  moving: false,
  animation: "idle_down",
  animationTime: 0,
  attackTime: 0,
};

const keys = new Set();
let lastTime = performance.now();

addEventListener("keydown", (event) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "KeyW", "KeyA", "KeyS", "KeyD", "Space"].includes(event.code)) {
    event.preventDefault();
  }
  keys.add(event.code);
  if (event.code === "Space") hero.attackTime = 150;
});

addEventListener("keyup", (event) => {
  keys.delete(event.code);
});

requestAnimationFrame(tick);

async function fetchJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Could not load ${path}`);
  return response.json();
}

function loadImage(path) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Could not load ${path}`));
    image.src = path;
  });
}

function tick(now) {
  const dt = Math.min((now - lastTime) / 1000, 0.05);
  lastTime = now;
  update(dt);
  render();
  requestAnimationFrame(tick);
}

function update(dt) {
  const input = readInput();
  hero.moving = input.x !== 0 || input.y !== 0;

  if (hero.attackTime > 0) {
    hero.attackTime = Math.max(0, hero.attackTime - dt * 1000);
  }

  if (hero.moving) {
    if (Math.abs(input.x) > Math.abs(input.y)) hero.facing = input.x > 0 ? "right" : "left";
    else hero.facing = input.y > 0 ? "down" : "up";

    const length = Math.hypot(input.x, input.y) || 1;
    moveHero((input.x / length) * hero.speed * dt, 0);
    moveHero(0, (input.y / length) * hero.speed * dt);
  }

  const nextAnimation = chooseAnimation();
  if (nextAnimation !== hero.animation) {
    hero.animation = nextAnimation;
    hero.animationTime = 0;
  } else {
    hero.animationTime += dt * 1000;
  }
}

function readInput() {
  return {
    x: Number(keys.has("ArrowRight") || keys.has("KeyD")) - Number(keys.has("ArrowLeft") || keys.has("KeyA")),
    y: Number(keys.has("ArrowDown") || keys.has("KeyS")) - Number(keys.has("ArrowUp") || keys.has("KeyW")),
  };
}

function chooseAnimation() {
  if (hero.attackTime > 0 && (hero.facing === "left" || hero.facing === "right")) return `attack_${hero.facing}`;
  return `${hero.moving ? "walk" : "idle"}_${hero.facing}`;
}

function moveHero(dx, dy) {
  const oldX = hero.x;
  const oldY = hero.y;
  hero.x = clamp(hero.x + dx, 24, world.width * world.tileSize - 24);
  hero.y = clamp(hero.y + dy, 32, world.height * world.tileSize - 8);
  if (collides(heroFootRect())) {
    hero.x = oldX;
    hero.y = oldY;
  }
}

function heroFootRect() {
  const hb = heroMeta.hitbox;
  const origin = heroMeta.origin;
  return {
    x: hero.x - origin.x + hb.x,
    y: hero.y - origin.y + hb.y,
    w: hb.width,
    h: hb.height,
  };
}

function collides(rect) {
  const minX = Math.floor(rect.x / world.tileSize);
  const minY = Math.floor(rect.y / world.tileSize);
  const maxX = Math.floor((rect.x + rect.w - 1) / world.tileSize);
  const maxY = Math.floor((rect.y + rect.h - 1) / world.tileSize);

  for (let y = minY; y <= maxY; y++) {
    for (let x = minX; x <= maxX; x++) {
      if (world.solids.has(`${x},${y}`)) return true;
    }
  }
  return false;
}

function render() {
  const camera = cameraForHero();
  ctx.fillStyle = "#eff1cf";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  drawGround(camera);

  const drawables = [
    ...world.decor.map((item) => ({ y: (item.y + 1) * world.tileSize, draw: () => drawDecor(item, camera) })),
    { y: hero.y, draw: () => drawHero(camera) },
  ].sort((a, b) => a.y - b.y);

  for (const item of drawables) item.draw();
  drawVignette();
}

function cameraForHero() {
  const maxX = world.width * world.tileSize - canvas.width;
  const maxY = world.height * world.tileSize - canvas.height;
  return {
    x: Math.round(clamp(hero.x - canvas.width / 2, 0, maxX)),
    y: Math.round(clamp(hero.y - canvas.height / 2, 0, maxY)),
  };
}

function drawGround(camera) {
  const ts = world.tileSize;
  const startX = Math.floor(camera.x / ts) - 1;
  const startY = Math.floor(camera.y / ts) - 1;
  const endX = Math.ceil((camera.x + canvas.width) / ts) + 1;
  const endY = Math.ceil((camera.y + canvas.height) / ts) + 1;

  for (let y = startY; y <= endY; y++) {
    for (let x = startX; x <= endX; x++) {
      const sx = x * ts - camera.x;
      const sy = y * ts - camera.y;
      const solid = world.solids.has(`${x},${y}`);
      ctx.fillStyle = solid ? "#4a5744" : (x + y) % 2 ? "#d6dbb8" : "#c8cfa8";
      ctx.fillRect(sx, sy, ts, ts);
      if (!solid) {
        ctx.fillStyle = "#8f9a78";
        if ((x * 5 + y * 7) % 6 === 0) ctx.fillRect(sx + 10, sy + 45, 18, 4);
        if ((x * 3 + y * 11) % 8 === 0) ctx.fillRect(sx + 42, sy + 18, 10, 4);
      } else {
        ctx.fillStyle = "#17211b";
        ctx.fillRect(sx, sy + ts - 8, ts, 8);
        ctx.fillStyle = "#8f9a78";
        ctx.fillRect(sx + 8, sy + 8, ts - 16, 8);
      }
    }
  }
}

function drawDecor(item, camera) {
  const x = item.x * world.tileSize - camera.x;
  const y = item.y * world.tileSize - camera.y;
  if (item.kind === "tree") {
    ctx.fillStyle = "#17211b";
    ctx.fillRect(x + 12, y + 8, 40, 48);
    ctx.fillStyle = "#4a5744";
    ctx.fillRect(x + 16, y + 4, 32, 44);
    ctx.fillStyle = "#8f9a78";
    ctx.fillRect(x + 24, y + 12, 18, 12);
    ctx.fillStyle = "#17211b";
    ctx.fillRect(x + 26, y + 44, 12, 20);
  } else if (item.kind === "stone") {
    ctx.fillStyle = "#17211b";
    ctx.fillRect(x + 18, y + 34, 28, 18);
    ctx.fillStyle = "#8f9a78";
    ctx.fillRect(x + 20, y + 30, 24, 18);
    ctx.fillStyle = "#eff1cf";
    ctx.fillRect(x + 26, y + 32, 10, 4);
  } else {
    ctx.fillStyle = "#4a5744";
    ctx.fillRect(x + 8, y + 46, 16, 5);
    ctx.fillRect(x + 34, y + 40, 20, 5);
    ctx.fillStyle = "#8f9a78";
    ctx.fillRect(x + 14, y + 38, 7, 12);
    ctx.fillRect(x + 43, y + 30, 7, 15);
  }
}

function drawHero(camera) {
  const frame = currentFrame();
  const origin = heroMeta.origin;
  const x = Math.round(hero.x - origin.x - camera.x);
  const y = Math.round(hero.y - origin.y - camera.y);
  ctx.drawImage(heroImage, frame.x, frame.y, frame.width, frame.height, x, y, frame.width, frame.height);
}

function currentFrame() {
  const animation = heroMeta.animations[hero.animation] || heroMeta.animations.idle_down;
  const total = animation.reduce((sum, item) => sum + item.durationMs, 0);
  let t = hero.animationTime % total;
  for (const item of animation) {
    if (t < item.durationMs) return frameByName(item.frame);
    t -= item.durationMs;
  }
  return frameByName(animation[0].frame);
}

function frameByName(name) {
  return heroMeta.frames.find((frame) => frame.name === name) || heroMeta.frames[0];
}

function drawVignette() {
  ctx.strokeStyle = "#17211b";
  ctx.lineWidth = 8;
  ctx.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}
