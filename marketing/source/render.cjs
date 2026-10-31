// Renders the listing artwork in marketing/images/ from real in-game screenshots, the mod's own textures and the
// bundled OFL fonts (Fraunces, Spectral).
// Usage (from the repository root): NODE_PATH="$(npm root -g)" node marketing/source/render.cjs [name...]
// Requires the `playwright` package with a Chromium build available.
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

// The release and the supported Minecraft versions. Adding a version is one line here
// (plus one row in the compatibility table of curseforge/description.md).
const RELEASE = { version: '1.0', name: 'First Bloom' };
const VERSIONS = [
  { minecraft: '1.21.1', loaders: ['Fabric', 'NeoForge'] },
];
const LOADERS = ['Fabric', 'Forge', 'NeoForge'].filter((loader) => VERSIONS.some((v) => v.loaders.includes(loader)));

const root = path.resolve(__dirname, '..', '..');
const out = process.env.SS_OUT || path.join(root, 'marketing', 'images');
const shots = process.env.SS_SHOTS || path.join(root, 'marketing', 'images', 'screenshots');
const fonts = path.join(__dirname, 'fonts');
// The mod's textures, straight from the generated resources of the reference workspace.
const textures = path.join(root, '1.21.1', 'common', 'src', 'generated', 'resources', 'assets', 'spore_and_stem', 'textures');
const url = (file) => 'file://' + file;
const shot = (name) => url(path.join(shots, name));
const source = (name) => url(path.join(__dirname, name));
const tex = (name) => url(path.join(textures, name + '.png'));
const need = (file) => { if (!fs.existsSync(file)) throw new Error('missing ' + path.relative(root, file)); return file; };

const css = `
@font-face { font-family: SsBody; src: url('${url(path.join(fonts, 'spectral.ttf'))}'); }
@font-face { font-family: SsBody; font-style: italic; src: url('${url(path.join(fonts, 'spectral-italic.ttf'))}'); }
@font-face { font-family: SsBody; font-weight: 600; src: url('${url(path.join(fonts, 'spectral-semibold.ttf'))}'); }
@font-face { font-family: SsDisplay; font-weight: 100 900; src: url('${url(path.join(fonts, 'fraunces.ttf'))}'); }
@font-face { font-family: SsDisplay; font-style: italic; font-weight: 100 900; src: url('${url(path.join(fonts, 'fraunces-italic.ttf'))}'); }
:root { --text:#e9e4d6; --dim:#93a8a4; --faint:#5d726f; --header:#f6f1e4; --glow:#6bf2e3; --teal:#3fc7c0; --deep:#1b7272;
        --gold:#f2d08a; --rose:#ef8eae; --ink:#463d57; --bg:#061113; --line:rgba(107,242,227,.35); }
* { box-sizing: border-box; }
html, body { margin: 0; background: var(--bg); color: var(--text); font-family: SsBody, serif; }
.stage { position: relative; overflow: hidden; background: radial-gradient(ellipse at 30% 40%, #0f2b2d 0%, #061113 72%); }
.display { font-family: SsDisplay, serif; font-weight: 700; font-variation-settings: "SOFT" 100, "WONK" 1, "opsz" 144; letter-spacing: -.01em; }
.bio { background: linear-gradient(180deg, #f4fffd 0%, #c8fff6 26%, #7ff3e6 58%, #35b3ac 100%);
       -webkit-background-clip: text; background-clip: text; color: transparent; }
.glow { filter: drop-shadow(0 0 22px rgba(63,199,192,.45)); }
.kicker { font-family: SsBody, serif; font-weight: 600; color: var(--gold); letter-spacing: .24em; font-size: 21px; text-transform: uppercase;
          display: flex; align-items: center; gap: 14px; }
.orn { width: 28px; height: 28px; image-rendering: pixelated; flex: none; filter: drop-shadow(0 0 6px rgba(107,242,227,.55)); }
.rule { height: 1px; background: linear-gradient(90deg, rgba(107,242,227,0), rgba(107,242,227,.85) 20%, rgba(107,242,227,.85) 70%, rgba(107,242,227,0)); }
.frame { position: relative; border: 1px solid rgba(107,242,227,.42); box-shadow: 0 0 0 1px rgba(0,0,0,.6), 0 30px 80px rgba(0,0,0,.7), 0 0 70px rgba(63,199,192,.14); background: #000; }
.frame > img { display: block; width: 100%; }
canvas.motes { position: absolute; left: 0; top: 0; width: 100%; height: 100%; pointer-events: none; }
.vignette { position: absolute; inset: 0; background: radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,.78) 100%); }
.backdrop { position: absolute; inset: -40px; background-size: cover; background-position: center; filter: blur(16px) brightness(.34) saturate(1.2); }
.pill { display: inline-block; border: 1px solid rgba(107,242,227,.55); padding: 6px 15px 5px; margin-right: 10px;
        font-family: SsBody, serif; font-weight: 600; font-size: 19px; letter-spacing: .14em; text-transform: uppercase; color: var(--header); background: rgba(0,0,0,.35); }
.label { position: absolute; font-family: SsBody, serif; font-weight: 600; font-size: 19px; letter-spacing: .14em; text-transform: uppercase; color: var(--header);
         background: rgba(6,17,19,.88); border: 1px solid rgba(107,242,227,.8); padding: 7px 14px 6px; white-space: nowrap;
         box-shadow: 0 8px 26px rgba(0,0,0,.6); z-index: 2; }
.label small { display: block; font-weight: 400; letter-spacing: 0; text-transform: none; font-size: 18px; color: var(--dim); margin-top: 1px; }
ul.points { list-style: none; padding: 0; margin: 0; }
ul.points li { position: relative; padding-left: 34px; margin: 0 0 14px; font-size: 26px; line-height: 1.33; color: var(--text); }
ul.points li::before { content: ''; position: absolute; left: 0; top: 7px; width: 20px; height: 20px; background: url('${tex('item/glowcap')}') center / contain no-repeat; image-rendering: pixelated;
                       filter: drop-shadow(0 0 4px rgba(107,242,227,.6)); }
.stats { display: flex; margin-top: 22px; border: 1px solid rgba(107,242,227,.32); background: rgba(6,17,19,.84); box-shadow: 0 18px 50px rgba(0,0,0,.55); }
.stats > div { flex: 1; padding: 14px 24px 12px; border-left: 1px solid rgba(107,242,227,.18); }
.stats > div:first-child { border-left: 0; }
.stats .t { font-family: SsBody, serif; font-weight: 600; font-size: 15px; letter-spacing: .2em; text-transform: uppercase; color: var(--dim); }
.stats .v { font-family: SsBody, serif; font-weight: 600; font-size: 30px; color: var(--header); margin-top: 4px; white-space: nowrap; }
b.hi { color: var(--header); font-weight: 600; }
.px { image-rendering: pixelated; }
`;

// Drifting spores: mostly pale motes, some glowing teal ones. Deterministic.
const motes = `<canvas class="motes"></canvas><script>
(() => { const c = document.querySelector('canvas.motes'); const r = c.getBoundingClientRect();
  c.width = r.width; c.height = r.height; const g = c.getContext('2d'); let s = 7;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 90; i++) { const x = rnd() * c.width, y = rnd() * c.height, a = .18 + rnd() * .5, z = 1 + rnd() * 2.2;
    const glow = rnd() < .45; const col = glow ? '107,242,227' : '233,223,199';
    const h = g.createRadialGradient(x, y, 0, x, y, z * 6); h.addColorStop(0, 'rgba(' + col + ',' + a * (glow ? .55 : .3) + ')'); h.addColorStop(1, 'rgba(' + col + ',0)');
    g.fillStyle = h; g.beginPath(); g.arc(x, y, z * 6, 0, Math.PI * 2); g.fill();
    g.fillStyle = glow ? 'rgba(220,255,250,' + a + ')' : 'rgba(246,240,226,' + a * .8 + ')'; g.fillRect(Math.round(x - z / 2), Math.round(y - z / 2), Math.ceil(z), Math.ceil(z)); } })();
</script>`;

const page = (width, height, body, transparent = false) => `<!doctype html><html><head><meta charset="utf-8"><style>${css}
body { width: ${width}px; height: ${height}px; } .stage { width: ${width}px; height: ${height}px; }
${transparent ? 'html, body, .stage { background: transparent; }' : ''}</style></head>
<body><div class="stage">${body}</div></body></html>`;

const ornament = (size = 28, style = '') => `<img class="orn" src="${tex('item/glowcap')}" style="width:${size}px;height:${size}px;${style}">`;

const header = (title) => page(1400, 120, `
  <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:26px;background:linear-gradient(90deg,rgba(0,0,0,0),rgba(6,20,22,.92) 30%,rgba(6,20,22,.92) 70%,rgba(0,0,0,0))">
    <div class="rule" style="width:300px;transform:scaleX(-1)"></div>
    ${ornament(30)}
    <div class="display bio glow" style="font-size:56px;white-space:nowrap;line-height:1.1;padding-bottom:4px">${title}</div>
    ${ornament(30, 'transform:scaleX(-1)')}
    <div class="rule" style="width:300px"></div>
  </div>`, true);

// A feature card: copy on the left, artwork on the right. Bullets never end on a one-word line.
const card = ({ kicker, title, points, art, width = 1600, height = 900, artWidth = 980 }) => page(width, height, `
  <div class="backdrop" style="background-image:url('${source('backdrop.jpg')}');opacity:.6"></div>
  <div class="vignette"></div>${motes}
  <div style="position:absolute;left:80px;top:0;bottom:0;width:${width - artWidth - 150}px;display:flex;flex-direction:column;justify-content:center">
    <div class="kicker"${kicker.length > 24 ? ' style="font-size:18px;letter-spacing:.16em"' : ''}>${ornament(26)}${kicker}</div>
    <div class="display bio glow" style="font-size:72px;line-height:1.02;margin:18px 0 24px">${title}</div>
    <div class="rule" style="width:80%;margin-bottom:30px"></div>
    <ul class="points">${points.map((point) => `<li>${point.replace(/ (\S+)$/, '&nbsp;$1')}</li>`).join('')}</ul>
  </div>
  <div style="position:absolute;right:60px;top:50%;transform:translateY(-50%);width:${artWidth}px">${art}</div>`);

// An exact region (x, y, w, h in 1920x1080 pixels) of a capture, scaled to W pixels wide.
const region = (file, x, y, w, h, W) => `<div style="position:relative;width:${W}px;height:${Math.round(W * h / w)}px;overflow:hidden">
    <img src="${shot(file)}" style="position:absolute;max-width:none;width:${W * 1920 / w}px;left:${-x * W / w}px;top:${-y * W / w}px"></div>`;
const framed = (inner, style = '', color = '') => `<div class="frame" style="${color ? `border-color:${color}99;` : ''}${style}">${inner}</div>`;
const label = (text, style, small = '') => `<div class="label" style="${style}">${text}${small ? `<small>${small}</small>` : ''}</div>`;
const stats = (items, color) => `<div class="stats"${color ? ` style="border-top:2px solid ${color}"` : ''}>${items.map(([t, v, flex]) =>
  `<div${flex ? ` style="flex:${flex}"` : ''}><div class="t">${t}</div><div class="v">${v}</div></div>`).join('')}</div>`;
// Two overlapping captures.
const pair = (first, second, firstLabel, secondLabel, firstSpot = 'left:20px;top:20px', height = 700) => `<div style="position:relative;height:${height}px">
    <div class="frame" style="position:absolute;left:0;top:0;width:74%"><img src="${shot(first)}" style="display:block;width:100%"></div>
    <div class="frame" style="position:absolute;right:0;bottom:0;width:74%"><img src="${shot(second)}" style="display:block;width:100%"></div>
    ${label(firstLabel, firstSpot)}${label(secondLabel, 'right:20px;bottom:20px')}</div>`;
// A large capture with a smaller one overlapping its corner.
const inset = (main, small, crop, mainLabel, smallLabel, smallWidth = 420) => `<div style="position:relative">
    ${framed(`<img src="${shot(main)}">`)}
    <div class="frame" style="position:absolute;right:-24px;bottom:-40px;width:${smallWidth}px">${region(small, ...crop, smallWidth)}</div>
    ${mainLabel ? label(mainLabel, 'left:20px;top:20px') : ''}${smallLabel ? label(smallLabel, `right:-24px;bottom:${Math.round(smallWidth * crop[3] / crop[2]) - 20}px`) : ''}</div>`;
// A grid of item sprites with a name and a line each (fungi, food).
const itemGrid = (items, columns = 2, size = 72) => `<div class="frame" style="background:rgba(6,17,19,.93);padding:30px 38px;display:grid;grid-template-columns:repeat(${columns},1fr);gap:20px 34px">
  ${items.map(([id, name, line]) => `<div style="display:flex;align-items:center;gap:20px">
    <div style="width:${size + 8}px;height:${size + 8}px;flex:none;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(63,199,192,.22),rgba(63,199,192,0) 70%)">
      <img class="px" src="${tex('item/' + id)}" style="width:${size}px;height:${size}px"></div>
    <div><div class="display" style="font-size:32px;color:var(--header);line-height:1.05">${name}</div>
      <div style="font-size:20px;color:var(--dim);margin-top:3px">${line}</div></div></div>`).join('')}</div>`;

const versionText = VERSIONS.map((v) => 'Minecraft ' + v.minecraft).join(' · ');

const assets = {
  banner: () => page(1800, 600, `
    <img src="${shot(BANNER_SHOT)}" style="position:absolute;left:520px;top:-220px;width:1560px;-webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 30%);mask-image:linear-gradient(90deg,transparent 0%,#000 30%)">
    <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,17,19,.97) 0%,rgba(6,17,19,.9) 30%,rgba(6,17,19,.35) 56%,rgba(6,17,19,0) 76%)"></div>
    <div style="position:absolute;inset:0;background:linear-gradient(0deg,rgba(6,17,19,.75) 0%,rgba(6,17,19,0) 32%)"></div>
    <div class="vignette"></div>${motes}
    <img class="px" src="${url(need(LOGO))}" style="position:absolute;left:84px;top:96px;width:192px;height:192px;box-shadow:0 20px 60px rgba(0,0,0,.6),0 0 60px rgba(63,199,192,.28)">
    <div style="position:absolute;left:310px;top:70px;width:960px">
      <div class="kicker">${ornament(24)}${RELEASE.version} · ${RELEASE.name}</div>
      <div class="display bio glow" style="font-size:138px;line-height:1.06;margin:4px 0 12px;white-space:nowrap">Spore <span style="font-style:italic;font-weight:500">&amp;</span> Stem</div>
      <div class="rule" style="width:640px;margin-bottom:22px"></div>
      <div style="font-size:34px;color:var(--header);line-height:1.3;font-style:italic">A whole kingdom of fungi, glowing in the dark.</div>
    </div>
    <div style="position:absolute;left:88px;bottom:70px">${LOADERS.map((l) => `<span class="pill">${l}</span>`).join('')}
      <span style="font-size:24px;color:var(--dim);margin-left:8px">${versionText}</span></div>`),

  icon: () => page(512, 512, `<img class="px" src="${url(need(LOGO))}" style="position:absolute;inset:0;width:512px;height:512px">`, true),
};

// The banner screenshot and the mod icon.
const BANNER_SHOT = process.env.SS_BANNER_SHOT || 'glowcap-grove.jpg';
const LOGO = process.env.SS_LOGO || path.join(root, '1.21.1', 'common', 'src', 'main', 'resources', 'logo.png');

const headers = {
  'header-giants': 'The Giants', 'header-woods': 'Fungal Woods', 'header-fungi': 'Nine Mushrooms', 'header-world': 'Into the Undergrowth',
  'header-cultivation': 'Grow Your Own', 'header-kitchen': 'The Forager’s Kitchen', 'header-mycosis': 'Mycosis', 'header-creatures': 'Creatures',
  'header-boss': 'The Myceliarch', 'header-spoils': 'Spoils', 'header-config': 'Configuration', 'header-everything': 'Everything Else',
  'header-compatibility': 'Downloads & Compatibility', 'header-faq': 'Questions', 'header-gallery': 'Gallery',
};
for (const [name, title] of Object.entries(headers)) assets[name] = () => header(title.replace('&', '&amp;'));
assets.divider = () => page(1400, 40, `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:18px">
  <div class="rule" style="width:520px;transform:scaleX(-1)"></div>${ornament(22)}<div class="rule" style="width:520px"></div></div>`, true);

// Feature cards live in cards.cjs (they depend on the captures); merged here.
if (fs.existsSync(path.join(__dirname, 'cards.cjs'))) {
  Object.assign(assets, require('./cards.cjs')({ card, framed, region, label, stats, pair, inset, itemGrid, shot, tex, source }));
}

(async () => {
  const wanted = process.argv.slice(2);
  const browser = await chromium.launch();
  fs.mkdirSync(out, { recursive: true });
  for (const [name, build] of Object.entries(assets)) {
    if (wanted.length && !wanted.includes(name)) continue;
    const html = build();
    const size = html.match(/body \{ width: (\d+)px; height: (\d+)px; \}/);
    const tab = await browser.newPage({ viewport: { width: +size[1], height: +size[2] }, deviceScaleFactor: 1 });
    const file = path.join(__dirname, `.render-${name}.html`);
    fs.writeFileSync(file, html);
    await tab.goto(url(file));
    await tab.evaluate(() => document.fonts.ready);
    await tab.waitForLoadState('networkidle');
    await tab.screenshot({ path: path.join(out, `${name}.png`), omitBackground: name === 'divider' || name === 'icon' || name.startsWith('header-') });
    fs.unlinkSync(file);
    await tab.close();
    console.log('rendered', name);
  }
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
