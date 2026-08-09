/* About hero: a Hilux composited into Andy's studio photo, spinning in place
   while the copy chapters scroll past. Camera is locked to match the plate;
   the CAR rotates, not the camera. Add ?tune and use the keys shown to dial
   the car onto the floor, then read the values off the on-screen panel. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const root = document.querySelector('[data-about3d]');
if (root) init(root);

function init(root) {
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));

  const stageEl  = root.querySelector('.about-sticky');
  const canvasEl = root.querySelector('.about-canvas');
  const loading  = root.querySelector('.about-loading');
  const chapters = Array.prototype.slice.call(root.querySelectorAll('.ach'));
  const rail     = Array.prototype.slice.call(root.querySelectorAll('.about-rail i'));
  const tuneEl   = root.querySelector('.about-tune');

  // ---- tunables (match the garage plate) ----
  const CAM = { fov: 42, x: 0, y: 1.5, z: 5.7, tx: 0, ty: 0.62, tz: 0 };
  const CAR = { y: 0, scale: 1, spin: 0.0032, color: 0x181b21, metal: 0.64, rough: 0.15, env: 1.45 };
  const SHADOW = { r: 3.3, op: 0.55 };

  function fail() { if (loading) loading.hidden = true; }

  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' }); }
  catch (e) { fail(); return; }

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(CAM.fov, 1, 0.1, 100);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.06;
  canvasEl.appendChild(renderer.domElement);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;

  // studio-ish lighting (bright, from above/front like the ceiling strips)
  const key  = new THREE.DirectionalLight(0xffffff, 2.4); key.position.set(3, 9, 5); scene.add(key);
  const rim  = new THREE.DirectionalLight(0xffffff, 1.4); rim.position.set(-5, 6, -4); scene.add(rim);
  const fill = new THREE.DirectionalLight(0xffffff, 0.9); fill.position.set(0, 4, 7); scene.add(fill);
  scene.add(new THREE.AmbientLight(0xffffff, 0.28));

  function applyCam() {
    camera.fov = CAM.fov; camera.updateProjectionMatrix();
    camera.position.set(CAM.x, CAM.y, CAM.z);
    camera.lookAt(CAM.tx, CAM.ty, CAM.tz);
  }
  applyCam();

  const carGroup = new THREE.Group(); scene.add(carGroup);
  const paints = [];

  // soft radial contact shadow so the car sits on the floor
  const shadow = makeShadow();
  shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.003; scene.add(shadow);
  function applyShadow() { shadow.scale.setScalar(SHADOW.r); shadow.material.opacity = SHADOW.op; }
  applyShadow();

  function makeShadow() {
    const c = document.createElement('canvas'); c.width = c.height = 256;
    const g = c.getContext('2d');
    const grd = g.createRadialGradient(128, 128, 8, 128, 128, 128);
    grd.addColorStop(0, 'rgba(0,0,0,0.6)'); grd.addColorStop(0.55, 'rgba(0,0,0,0.28)'); grd.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = grd; g.fillRect(0, 0, 256, 256);
    const tex = new THREE.CanvasTexture(c);
    return new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false, opacity: SHADOW.op }));
  }

  function loadModel() {
    new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load('assets/hilux.glb', (gltf) => {
      const car = gltf.scene;
      const box0 = new THREE.Box3().setFromObject(car);
      const c0 = new THREE.Vector3(); box0.getCenter(c0);
      car.position.x -= c0.x; car.position.z -= c0.z; car.position.y -= box0.min.y; // sit on floor, centred
      carGroup.add(car);

      const seen = new Set();
      car.traverse(o => {
        if (o.isMesh && o.material && o.material.name === 'body_paint' && !seen.has(o.material)) {
          seen.add(o.material);
          o.material.color.setHex(CAR.color); o.material.metalness = CAR.metal;
          o.material.roughness = CAR.rough; o.material.envMapIntensity = CAR.env;
          paints.push(o.material);
        }
      });
      applyCar();
      if (loading) loading.hidden = true;
      resize();
      requestAnimationFrame(loop);
    }, undefined, () => fail());
  }
  function applyCar() { carGroup.scale.setScalar(CAR.scale); carGroup.position.y = CAR.y; }

  function progress() {
    var total = root.offsetHeight - innerHeight;
    if (total <= 0) return 0;
    return clamp(-root.getBoundingClientRect().top / total, 0, 1);
  }
  function updateChapters(p) {
    chapters.forEach(function (el) {
      var c = parseFloat(el.dataset.center);
      var a = clamp(1 - Math.abs(p - c) / 0.42, 0, 1);
      el.style.opacity = a.toFixed(3);
      el.style.transform = (el.classList.contains('ach-3') ? 'translateY(-30%)' : '') + ' translateY(' + ((1 - a) * 22) + 'px)';
    });
    var idx = clamp(Math.round(p * 2), 0, 2);
    rail.forEach(function (el, i) { el.classList.toggle('on', i === idx); });
  }

  let visible = false;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold: 0 }).observe(stageEl);

  function loop() {
    if (visible) {
      if (!REDUCED) carGroup.rotation.y += CAR.spin;
      updateChapters(progress());
      renderer.render(scene, camera);
    }
    requestAnimationFrame(loop);
  }

  // preload just before the hero is on screen (it is the top of the page)
  loadModel();

  function resize() {
    const w = stageEl.clientWidth, h = stageEl.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stageEl);
  resize();

  /* ---------- live tuner (?tune) ---------- */
  if (/[?&]tune\b/.test(location.search) && tuneEl) {
    tuneEl.classList.add('on');
    var readout = function () {
      tuneEl.textContent =
        'CAM fov ' + CAM.fov.toFixed(0) + '  y ' + CAM.y.toFixed(2) + '  z ' + CAM.z.toFixed(2) + '  x ' + CAM.x.toFixed(2) + '  ty ' + CAM.ty.toFixed(2) + '\n' +
        'CAR scale ' + CAR.scale.toFixed(2) + '  y ' + CAR.y.toFixed(2) + '  shadow r ' + SHADOW.r.toFixed(2) + '\n' +
        'keys: arrows=cam y/z  a/d=cam x  w/s=aim  q/e=fov  z/x=scale  r/f=car y  [/]=shadow';
    };
    readout();
    addEventListener('keydown', function (e) {
      var k = e.key;
      if (k === 'ArrowUp') CAM.y += 0.05; else if (k === 'ArrowDown') CAM.y -= 0.05;
      else if (k === 'ArrowLeft') CAM.z -= 0.1; else if (k === 'ArrowRight') CAM.z += 0.1;
      else if (k === 'a') CAM.x -= 0.05; else if (k === 'd') CAM.x += 0.05;
      else if (k === 'w') CAM.ty += 0.03; else if (k === 's') CAM.ty -= 0.03;
      else if (k === 'q') CAM.fov -= 1; else if (k === 'e') CAM.fov += 1;
      else if (k === 'z') CAR.scale -= 0.02; else if (k === 'x') CAR.scale += 0.02;
      else if (k === 'r') CAR.y += 0.02; else if (k === 'f') CAR.y -= 0.02;
      else if (k === '[') SHADOW.r -= 0.1; else if (k === ']') SHADOW.r += 0.1;
      else return;
      e.preventDefault(); applyCam(); applyCar(); applyShadow(); readout();
    });
  }
}
