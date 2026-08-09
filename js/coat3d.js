/* CDS ceramic-coating cinematic experience.
   A scroll-scrubbed Range Rover that educates the customer through the four
   stages of a ceramic job with a continuous, bounding-box-relative camera
   journey (wide -> macro -> clinical -> hero), per-stage lighting + photoreal
   gloss progression, restrained decontamination / inspection effects, click-to
   -scrub stage nav and drag-to-spin on the final reveal.
   Vanilla Three.js, rAF scroll (no GSAP / R3F). Mounts on [data-coat3d].
   Add ?tune to nudge the live camera pose and read the multipliers back. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const root = document.querySelector('[data-coat3d]');
if (root) init(root);

function init(root) {
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MOBILE = matchMedia('(max-width: 760px)').matches;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, t) => a + (b - a) * t;
  const smooth = t => t * t * (3 - 2 * t);
  const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; // cinematic

  const MODEL   = root.dataset.model || 'assets/rover.glb';
  const stage   = root.querySelector('.coat3d-stage');
  const loading  = root.querySelector('.coat3d-loading');
  const steps   = Array.prototype.slice.call(root.querySelectorAll('.coat3d-step'));
  const tuneEl  = root.querySelector('.coat3d-tune');
  const setField = (n, v, html) => root.querySelectorAll('[data-field="' + n + '"]').forEach(el => { if (html) el.innerHTML = v; else el.textContent = v; });

  // Four stages. gloss drives the meter; roughness/env drive the paint state.
  const STAGES = [
    { n: '01', title: 'Deep clean & decontaminate', desc: 'Strip-wash, an iron fallout remover and a clay bar pull embedded grime out of the pores of the paint.', gloss: 0.18 },
    { n: '02', title: 'Paint correction',           desc: 'Staged machine polishing removes the swirls and haze. Ceramic magnifies the surface, so it has to be right first.', gloss: 0.5 },
    { n: '03', title: 'Panel prep',                 desc: 'A full alcohol wipe-down strips every polishing oil so the coating can bond directly to the bare clear coat.', gloss: 0.72 },
    { n: '04', title: 'Ceramic coating',            desc: 'Graphene ceramic bonds to the clear coat, panel by panel, for a deep, protected, high-gloss finish.', gloss: 1.0, product: 'Graphene ceramic, up to 10H' },
  ];
  // progress window per stage (for the nav / card / badge)
  const STAGE_AT = [0.0, 0.30, 0.54, 0.75, 1.001];
  const stageOf = p => p < STAGE_AT[1] ? 0 : p < STAGE_AT[2] ? 1 : p < STAGE_AT[3] ? 2 : 3;
  const stageScroll = [0.14, 0.42, 0.65, 0.9]; // where a nav click lands

  function fail() { if (loading) loading.hidden = true; root.dataset.failed = '1'; }

  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' }); }
  catch (e) { fail(); return; }

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.05, 200);
  renderer.setPixelRatio(Math.min(devicePixelRatio, MOBILE ? 1.6 : 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  stage.appendChild(renderer.domElement);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;

  // --- premium studio lighting rig (reused, animated per stage) ---
  const key    = new THREE.DirectionalLight(0xffffff, 2.4); key.position.set(4, 9, 6); scene.add(key);
  const rim    = new THREE.DirectionalLight(0xcfe0ff, 1.4); rim.position.set(-7, 5, -6); scene.add(rim);
  const fill   = new THREE.DirectionalLight(0xffffff, 0.6); fill.position.set(0, 4, 8); scene.add(fill);
  const ambient = new THREE.AmbientLight(0xffffff, 0.2); scene.add(ambient);
  // narrow inspection strip that sweeps during correction
  const inspect = new THREE.DirectionalLight(0xffffff, 0.0); inspect.position.set(0, 6, 4); scene.add(inspect);

  const carGroup = new THREE.Group(); scene.add(carGroup);
  const paints = [];           // cloned paint materials
  let L = 4.8, W = 1.9, H = 1.7, center = new THREE.Vector3(0, 0.85, 0);
  let POSES = [];
  let contamination = null, shadow = null;
  let ready = false;

  // paint mesh detection (Range Rover: Car_Paint, Carbon). Never coat glass/tyres/etc.
  const PAINT = new Set(['Car_Paint', 'Carbon', 'body_paint']);
  const isPaint = n => PAINT.has(n) || /car[_ ]?paint|body[_ ]?paint/i.test(n || '');

  function buildPoses() {
    // pos: [x,y,z] with x,z in units of L (length), y in units of H (height).
    // tgt: [x,y,z] with x in units of W/2, y in units of H, z in units of L/2.
    const DEF = [
      { p: 0.00, pos: [0.95, 0.34, 1.55], tgt: [0.0, 0.42, 0.0], fov: 34 }, // intro low front 3/4
      { p: 0.16, pos: [0.80, 1.02, 1.30], tgt: [0.0, 0.50, 0.1], fov: 37 }, // clean high front 3/4
      { p: 0.30, pos: [0.68, 0.46, 1.02], tgt: [0.6, 0.55, 0.7], fov: 44 }, // dive toward front quarter
      { p: 0.44, pos: [0.55, 0.55, 0.60], tgt: [0.2, 0.58, 0.5], fov: 30 }, // macro grazing inspection
      { p: 0.60, pos: [0.56, 0.53, -0.15], tgt: [0.2, 0.56, -0.6], fov: 30 }, // track along the panel
      { p: 0.68, pos: [0.38, 1.35, 0.80], tgt: [0.0, 0.28, 0.0], fov: 42 }, // clinical high prep
      { p: 0.82, pos: [1.00, 0.55, 0.98], tgt: [0.0, 0.50, 0.2], fov: 36 }, // coating orbit
      { p: 0.92, pos: [1.16, 0.36, 0.55], tgt: [0.0, 0.46, 0.0], fov: 34 }, // orbit descend
      { p: 1.00, pos: [1.10, 0.28, 1.62], tgt: [0.0, 0.45, 0.0], fov: 32 }, // final hero
    ];
    const hx = W / 2, hz = L / 2;
    POSES = DEF.map(d => ({
      p: d.p, fov: d.fov,
      pos: new THREE.Vector3(d.pos[0] * L, d.pos[1] * H, d.pos[2] * L),
      tgt: new THREE.Vector3(d.tgt[0] * hx, d.tgt[1] * H, d.tgt[2] * hz),
    }));
  }

  // interpolate the camera along the pose timeline
  const _pos = new THREE.Vector3(), _tgt = new THREE.Vector3();
  let dragYaw = 0;
  function applyCamera(p) {
    let a = POSES[0], b = POSES[POSES.length - 1];
    for (let i = 0; i < POSES.length - 1; i++) { if (p <= POSES[i + 1].p || i === POSES.length - 2) { a = POSES[i]; b = POSES[i + 1]; break; } }
    const t = easeInOut(clamp((p - a.p) / (b.p - a.p || 1), 0, 1));
    _pos.lerpVectors(a.pos, b.pos, t);
    _tgt.lerpVectors(a.tgt, b.tgt, t);
    camera.fov = lerp(a.fov, b.fov, t); camera.updateProjectionMatrix();
    camera.position.copy(_pos);
    camera.lookAt(_tgt);
  }

  // paint state: dull/contaminated -> corrected -> prepped -> glossy coated
  function paintKey(p, key) {
    const K = { rough: [[0, 0.52], [0.30, 0.52], [0.54, 0.22], [0.75, 0.24], [1.0, 0.05]],
                env:   [[0, 0.7],  [0.30, 0.8],  [0.54, 1.1],  [0.75, 1.2],  [1.0, 1.9]] }[key];
    for (let i = 0; i < K.length - 1; i++) { if (p <= K[i + 1][0] || i === K.length - 2) { const t = smooth(clamp((p - K[i][0]) / (K[i + 1][0] - K[i][0] || 1), 0, 1)); return lerp(K[i][1], K[i + 1][1], t); } }
    return K[K.length - 1][1];
  }

  function applyLighting(p) {
    // exposure lifts subtly into the final reveal; inspection strip peaks in stage 2
    renderer.toneMappingExposure = lerp(0.96, 1.08, smooth(clamp((p - 0.6) / 0.4, 0, 1)));
    const insp = Math.sin(clamp((p - 0.30) / 0.24, 0, 1) * Math.PI); // 0->1->0 across correction
    inspect.intensity = insp * 3.2;
    inspect.position.x = lerp(-L * 0.6, L * 0.6, clamp((p - 0.30) / 0.24, 0, 1));
    rim.intensity = lerp(1.2, 1.9, smooth(clamp((p - 0.75) / 0.25, 0, 1))); // richer reflections at the end
  }

  function applyEffects(p) {
    if (contamination) {
      // decontamination clears across stage 1
      const vis = 1 - smooth(clamp((p - 0.08) / 0.19, 0, 1));
      contamination.material.opacity = vis * 0.6;
      contamination.visible = vis > 0.02;
      contamination.rotation.y += 0.0008;
    }
  }

  function updateUI(p) {
    const s = stageOf(p), S = STAGES[s];
    steps.forEach((b, j) => { b.classList.toggle('active', j === s); b.classList.toggle('done', j < s); });
    setField('num', S.n);
    setField('title', S.title);
    setField('desc', S.desc);
    // meter reflects continuous gloss, not just the stage
    const gloss = clamp((paintKey(p, 'env') - 0.7) / (1.9 - 0.7), 0, 1);
    root.querySelectorAll('[data-field="meter"]').forEach(el => { el.style.width = Math.round(clamp(lerp(S.gloss - 0.12, S.gloss, 0.5) * 100 + gloss * 8, 6, 100)) + '%'; });
    const pw = root.querySelector('[data-field="product-wrap"]');
    if (pw) { if (S.product) { pw.hidden = false; setField('product', S.product); } else pw.hidden = true; }
  }

  function loadModel() {
    new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load(MODEL, (gltf) => {
      const car = gltf.scene; carGroup.add(car);
      const seen = new Set();
      car.traverse(o => {
        if (!o.isMesh || !o.material) return;
        if (isPaint(o.material.name)) {
          if (!seen.has(o.material)) {
            seen.add(o.material);
            const m = o.material.clone();            // preserve source material
            m.color.setHex(0x171b21); m.metalness = 0.62; m.roughness = 0.52; m.envMapIntensity = 0.7;
            o.material = m; paints.push(m);
          }
        }
      });

      // auto-fit: centre on floor, derive bounds
      const box = new THREE.Box3().setFromObject(car);
      const size = new THREE.Vector3(); box.getSize(size);
      const ctr = new THREE.Vector3(); box.getCenter(ctr);
      car.position.x -= ctr.x; car.position.z -= ctr.z; car.position.y -= box.min.y;
      L = size.z || size.x; W = size.x; H = size.y; center.set(0, H / 2, 0);
      buildPoses();

      // contact shadow
      shadow = new THREE.Mesh(new THREE.CircleGeometry(Math.max(L, W) * 0.62, 64),
        new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.55 }));
      shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.003; scene.add(shadow);

      // restrained decontamination indicators floating just above the top surfaces
      contamination = makeContamination(size);
      carGroup.add(contamination);

      ready = true;
      if (loading) loading.hidden = true;
      resize();
      requestAnimationFrame(loop);
    }, undefined, () => fail());
  }

  function makeContamination(size) {
    const n = MOBILE ? 90 : 200, arr = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      arr[i * 3] = (Math.random() - 0.5) * size.x * 0.9;
      arr[i * 3 + 1] = size.y * (0.55 + Math.random() * 0.45) + 0.03;
      arr[i * 3 + 2] = (Math.random() - 0.5) * size.z * 0.9;
    }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const mat = new THREE.PointsMaterial({ color: 0xb08a5a, size: Math.max(L, 1) * 0.012, transparent: true, opacity: 0.5, depthWrite: false, sizeAttenuation: true });
    return new THREE.Points(g, mat);
  }

  function progress() {
    const total = root.offsetHeight - innerHeight;
    if (total <= 0) return 0;
    return clamp(-root.getBoundingClientRect().top / total, 0, 1);
  }

  let visible = false;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold: 0 }).observe(stage);

  function loop() {
    if (visible && ready) {
      const p = progress();
      applyCamera(p);
      applyLighting(p);
      const rough = paintKey(p, 'rough'), env = paintKey(p, 'env');
      for (const m of paints) { m.roughness = rough; m.envMapIntensity = env; }
      applyEffects(p);
      updateUI(p);
      // drag-to-spin only on the settled final reveal
      if (p > 0.97) carGroup.rotation.y = dragYaw; else { dragYaw = 0; carGroup.rotation.y = 0; }
      renderer.render(scene, camera);
    }
    requestAnimationFrame(loop);
  }

  // stage nav -> scrub to that stage
  steps.forEach((b, i) => b.addEventListener('click', () => {
    const total = root.offsetHeight - innerHeight;
    const y = root.getBoundingClientRect().top + scrollY + stageScroll[i] * total;
    scrollTo({ top: y, behavior: REDUCED ? 'auto' : 'smooth' });
  }));

  // drag to spin (final reveal only)
  let dragging = false, startX = 0, startYaw = 0;
  stage.addEventListener('pointerdown', e => { if (progress() > 0.97) { dragging = true; startX = e.clientX; startYaw = dragYaw; try { stage.setPointerCapture(e.pointerId); } catch (_) {} } });
  stage.addEventListener('pointermove', e => { if (dragging) dragYaw = startYaw + (e.clientX - startX) * 0.006; });
  const endDrag = () => { dragging = false; };
  stage.addEventListener('pointerup', endDrag); stage.addEventListener('pointercancel', endDrag);

  const arm = () => { const pre = new IntersectionObserver(es => { if (es[0].isIntersecting) { pre.disconnect(); loadModel(); } }, { rootMargin: '900px 0px' }); pre.observe(stage); };
  if (document.readyState === 'complete') arm(); else addEventListener('load', arm, { once: true });

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage); resize();

  /* ---------- live pose tuner (?tune) ---------- */
  if (/[?&]tune\b/.test(location.search) && tuneEl) {
    tuneEl.classList.add('on');
    const nudge = { px: 0, py: 0, pz: 0, tx: 0, ty: 0, fov: 0 };
    const _ac = applyCamera;
    applyCamera = function (p) { _ac(p); camera.position.x += nudge.px * L; camera.position.y += nudge.py * H; camera.position.z += nudge.pz * L; camera.fov += nudge.fov; camera.updateProjectionMatrix(); camera.lookAt(_tgt.x + nudge.tx * W, _tgt.y + nudge.ty * H, _tgt.z); };
    const show = () => { tuneEl.textContent = 'p=' + progress().toFixed(2) + '  nudge px' + nudge.px.toFixed(2) + ' py' + nudge.py.toFixed(2) + ' pz' + nudge.pz.toFixed(2) + ' fov' + nudge.fov.toFixed(0) + '\nkeys: arrows=pos x/z  w/s=pos y  q/e=fov  scroll to a stage first'; };
    show();
    addEventListener('keydown', e => {
      const k = e.key;
      if (k === 'ArrowLeft') nudge.px -= 0.03; else if (k === 'ArrowRight') nudge.px += 0.03;
      else if (k === 'ArrowUp') nudge.pz -= 0.03; else if (k === 'ArrowDown') nudge.pz += 0.03;
      else if (k === 'w') nudge.py += 0.03; else if (k === 's') nudge.py -= 0.03;
      else if (k === 'q') nudge.fov -= 1; else if (k === 'e') nudge.fov += 1; else return;
      e.preventDefault(); show();
    });
  }
}
