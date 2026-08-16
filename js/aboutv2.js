/* =========================================================================
   CDS · About v2 — cinematic interactive Hilux
   A sticky, scroll-scrubbed studio: the camera orbits the truck as you scroll,
   giant type fades in BEHIND the subject, and you can grab the truck and spin
   it at any point. Scroll sets the base pose; a drag adds an offset that eases
   back so the choreography reasserts. Vanilla three.js, rAF, no GSAP/R3F.
   Mounts on [data-a3d].
   ========================================================================= */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const root = document.querySelector('[data-a3d]');
if (root) init(root);

function init(root) {
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MOBILE  = matchMedia('(max-width: 760px)').matches;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const lerp  = (a, b, t) => a + (b - a) * t;
  const smooth = t => t * t * (3 - 2 * t);
  const easeInOut = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const damp = (a, b, l, dt) => lerp(a, b, 1 - Math.exp(-l * dt)); // frame-rate independent
  const d2r = THREE.MathUtils.degToRad;

  const stage     = root.querySelector('.a3d-stage');
  const loadingEl = root.querySelector('.a3d-loading');
  const hintEl    = root.querySelector('.a3d-hint');
  const cueEl     = root.querySelector('.a3d-scrollcue');
  const finalEl   = root.querySelector('.a3d-final');
  const lines     = Array.prototype.slice.call(root.querySelectorAll('.a3d-line'));
  const MODEL     = MOBILE ? (root.dataset.modelMobile || 'assets/hilux_lite.glb')
                           : (root.dataset.model || 'assets/hilux.glb');

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
  } catch (e) { fail(); return; }
  function fail() { if (loadingEl) loadingEl.hidden = true; root.dataset.failed = '1'; }

  renderer.setPixelRatio(Math.min(devicePixelRatio, MOBILE ? 1.6 : 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.04;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.className = 'a3d-canvas';
  stage.appendChild(renderer.domElement);

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 400);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.02).texture;

  // --- studio lighting rig ---
  const key = new THREE.DirectionalLight(0xffffff, 2.7);
  key.position.set(5, 11, 7); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.near = 1; key.shadow.camera.far = 60;
  key.shadow.camera.left = -10; key.shadow.camera.right = 10;
  key.shadow.camera.top = 10; key.shadow.camera.bottom = -10;
  key.shadow.bias = -0.00022; key.shadow.radius = 6;
  scene.add(key);
  const rim    = new THREE.DirectionalLight(0xbcd4ff, 1.9); rim.position.set(-9, 6, -8); scene.add(rim);
  const fill   = new THREE.DirectionalLight(0xffffff, 0.55); fill.position.set(0, 4, 10); scene.add(fill);
  const accent = new THREE.PointLight(0xe11d2a, 0.0, 60, 2); accent.position.set(-5, 2.6, 5); scene.add(accent);
  scene.add(new THREE.AmbientLight(0xffffff, 0.16));

  const carGroup = new THREE.Group(); scene.add(carGroup);
  const paints = [];
  const isPaint = n => /body[_ ]?paint/i.test(n || '');
  let L = 5.4, W = 2.2, H = 2.1, ready = false;

  // camera keyframes: az deg (0 = front, + = CCW), polar deg from +Y, rad in units of L, ty target height as frac of H
  const KF = [
    { p: 0.00, az: -26,  polar: 80, rad: 1.78, ty: 0.44, exp: 1.00 }, // front 3/4, low
    { p: 0.34, az: -92,  polar: 72, rad: 1.44, ty: 0.52, exp: 1.05 }, // side profile
    { p: 0.66, az: -156, polar: 77, rad: 1.40, ty: 0.46, exp: 1.07 }, // rear 3/4
    { p: 1.00, az: -214, polar: 68, rad: 1.74, ty: 0.52, exp: 1.12 }, // front, pulled back (other side)
  ];
  function sampleKF(p) {
    let a = KF[0], b = KF[KF.length - 1];
    for (let i = 0; i < KF.length - 1; i++) { if (p <= KF[i + 1].p || i === KF.length - 2) { a = KF[i]; b = KF[i + 1]; break; } }
    const t = easeInOut(clamp((p - a.p) / (b.p - a.p || 1), 0, 1));
    return {
      az: lerp(a.az, b.az, t), polar: lerp(a.polar, b.polar, t),
      rad: lerp(a.rad, b.rad, t), ty: lerp(a.ty, b.ty, t), exp: lerp(a.exp, b.exp, t),
    };
  }
  const _off = new THREE.Vector3(), _tgt = new THREE.Vector3();
  function place(az, polar, radL, ty) {
    const pol = d2r(polar), a = d2r(az), r = radL * L;
    _off.set(r * Math.sin(pol) * Math.sin(a), r * Math.cos(pol), r * Math.sin(pol) * Math.cos(a));
    _tgt.set(0, ty * H, 0);
    camera.position.set(_off.x, _tgt.y + _off.y, _off.z);
    camera.lookAt(_tgt);
  }

  function loadModel() {
    new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load(MODEL, (gltf) => {
      const car = gltf.scene; carGroup.add(car);
      // Recolour the SHARED body material(s) in place so every body panel updates
      // (the body is split into many meshes that reference one 'body_paint' material).
      const seen = new Set();
      car.traverse(o => {
        if (!o.isMesh || !o.material) return;
        o.castShadow = true; o.receiveShadow = true;
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        mats.forEach(m => {
          if (!isPaint(m.name) || seen.has(m)) return;
          seen.add(m);
          m.color.setHex(0x1b1e24);            // deep glossy graphite
          m.metalness = 0.9; m.roughness = 0.22;
          m.envMapIntensity = 1.7;
          if ('clearcoat' in m) { m.clearcoat = 1.0; m.clearcoatRoughness = 0.05; }
          m.needsUpdate = true;
          paints.push(m);
        });
      });

      // centre on floor, derive bounds
      const box = new THREE.Box3().setFromObject(car);
      const size = new THREE.Vector3(); box.getSize(size);
      const ctr  = new THREE.Vector3(); box.getCenter(ctr);
      car.position.x -= ctr.x; car.position.z -= ctr.z; car.position.y -= box.min.y;
      L = size.z || size.x; W = size.x; H = size.y;

      // soft contact shadow (transparent plane — only the shadow shows over the DOM text)
      shadow = new THREE.Mesh(new THREE.PlaneGeometry(L * 2.4, L * 2.4), new THREE.ShadowMaterial({ opacity: 0.42 }));
      shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.001; shadow.receiveShadow = true;
      scene.add(shadow);
      // a tighter dark blob for weight under the truck
      const blob = new THREE.Mesh(
        new THREE.CircleGeometry(Math.max(L, W) * 0.6, 64),
        new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.5 })
      );
      blob.rotation.x = -Math.PI / 2; blob.position.y = 0.002; scene.add(blob);

      key.target = carGroup;
      ready = true;
      if (loadingEl) loadingEl.hidden = true;
      resize();
      requestAnimationFrame(loop);
    }, undefined, () => fail());
  }
  let shadow = null;

  // scroll progress across the tall wrapper while the stage is pinned
  const PROG_OVERRIDE = (location.search.match(/[?&]prog=([0-9.]+)/) || [])[1];
  function progress() {
    if (PROG_OVERRIDE != null) return clamp(parseFloat(PROG_OVERRIDE), 0, 1);
    const total = root.offsetHeight - innerHeight;
    if (total <= 0) return 0;
    return clamp(-root.getBoundingClientRect().top / total, 0, 1);
  }

  // ---- text choreography (giant type behind the subject) ----
  const sceneAt = lines.map((el, i) => parseFloat(el.dataset.at != null ? el.dataset.at : KF[Math.min(i, KF.length - 1)].p));
  function updateText(p) {
    for (let i = 0; i < lines.length; i++) {
      const d = p - sceneAt[i];
      const vis = clamp(1 - Math.abs(d) / 0.16, 0, 1);        // fade window
      const par = -d * (MOBILE ? 120 : 240);                  // parallax drift (px)
      const el = lines[i];
      el.style.opacity = smooth(vis).toFixed(3);
      el.style.transform = 'translate(-50%,-50%) translateY(' + par.toFixed(1) + 'px)';
    }
    // foreground CTA fades in over the last stretch; hint/cue fade out
    const fin = clamp((p - 0.86) / 0.12, 0, 1);
    if (finalEl) { finalEl.style.opacity = fin.toFixed(3); finalEl.classList.toggle('show', fin > 0.5); }
    if (hintEl && !everDragged) hintEl.style.opacity = (1 - clamp((p - 0.05) / 0.1, 0, 1)).toFixed(2);
    if (cueEl) cueEl.style.opacity = (1 - clamp((p - 0.02) / 0.08, 0, 1)).toFixed(2);
  }

  // ---- interaction: drag adds an offset that eases back to zero when idle ----
  let uAzTarget = 0, uPolTarget = 0, uAz = 0, uPol = 0, ambient = 0;
  let dragging = false, lastX = 0, lastY = 0, axis = 0, idleT = 0, everDragged = false;
  stage.addEventListener('pointerdown', e => {
    dragging = true; axis = 0; lastX = e.clientX; lastY = e.clientY; idleT = 0;
    try { stage.setPointerCapture(e.pointerId); } catch (_) {}
  });
  stage.addEventListener('pointermove', e => {
    if (!dragging) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY;
    if (axis === 0 && (Math.abs(dx) > 4 || Math.abs(dy) > 4)) axis = Math.abs(dx) >= Math.abs(dy) ? 1 : 2;
    if (axis === 2) return;                 // vertical drag → let the page scroll
    if (e.cancelable) e.preventDefault();
    lastX = e.clientX; lastY = e.clientY;
    uAzTarget += dx * 0.35;
    uPolTarget = clamp(uPolTarget - dy * 0.12, -16, 16);
    if (!everDragged) { everDragged = true; if (hintEl) { hintEl.classList.add('gone'); hintEl.style.opacity = '0'; } }
  }, { passive: false });
  const endDrag = e => { dragging = false; try { stage.releasePointerCapture(e.pointerId); } catch (_) {} };
  stage.addEventListener('pointerup', endDrag);
  stage.addEventListener('pointercancel', endDrag);

  let visible = false;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold: 0 }).observe(stage);

  let last = performance.now();
  function loop(now) {
    requestAnimationFrame(loop);
    const dt = Math.min(0.05, (now - last) / 1000 || 0.016); last = now;
    if (!ready || !visible) return;

    const p = progress();
    const k = sampleKF(p);

    // ease the user offset; a moment after release, relax it back so the story reasserts
    if (dragging) { idleT = 0; }
    else { idleT += dt; if (idleT > 1.4) { uAzTarget = damp(uAzTarget, 0, 1.4, dt); uPolTarget = damp(uPolTarget, 0, 1.4, dt); } }
    uAz  = damp(uAz,  uAzTarget,  10, dt);
    uPol = damp(uPol, uPolTarget, 10, dt);
    if (!REDUCED) ambient += dt;             // subtle life

    const az = k.az + uAz + Math.sin(ambient * 0.5) * 1.4;
    const polar = clamp(k.polar + uPol, 24, 88);
    place(az, polar, k.rad, k.ty);

    renderer.toneMappingExposure = k.exp;
    accent.intensity = 1.1 + Math.sin(ambient * 0.4) * 0.35;   // gentle red breathing
    rim.intensity = lerp(1.5, 2.2, smooth(p));

    updateText(p);
    renderer.render(scene, camera);
  }

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage); resize();

  // lazy-load the model when the stage is near the viewport
  const pre = new IntersectionObserver(es => { if (es[0].isIntersecting) { pre.disconnect(); loadModel(); } }, { rootMargin: '1200px 0px' });
  pre.observe(stage);
}
