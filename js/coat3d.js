/* Spinning vehicle that visually walks through the 4 stages of a ceramic job.
   Model-agnostic (auto-fits any GLB), self-hosted Three.js. Mounts on [data-coat3d]. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const root = document.querySelector('[data-coat3d]');
if (root) init(root);

function init(root) {
  const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MODEL   = root.dataset.model || 'assets/rover.glb';
  const stage   = root.querySelector('.coat3d-stage');
  const loading = root.querySelector('.coat3d-loading');
  const steps   = [...root.querySelectorAll('.coat3d-step')];

  // The four stages of a proper ceramic job. Visual state escalates gloss/
  // protection so the vehicle reads as improving as the story advances.
  const STAGES = [
    { n:'01', title:'Deep clean & decontaminate', desc:'Strip-wash, an iron fallout remover and a clay bar pull embedded grime out of the pores of the paint.', rough:0.62, env:0.60, shell:0.0,  gloss:0.16 },
    { n:'02', title:'Paint correction',           desc:'Staged machine polishing removes swirls and oxidation. Ceramic magnifies the surface, so it has to be right first.', rough:0.30, env:1.10, shell:0.0,  gloss:0.52 },
    { n:'03', title:'Panel prep',                 desc:'A full alcohol wipe-down strips every polishing oil so the coating can bond directly to the bare clear coat.', rough:0.20, env:1.25, shell:0.04, gloss:0.72 },
    { n:'04', title:'Ceramic coating',            desc:'Graphene ceramic is applied by hand and levelled section by section for a deep, protected, high-gloss finish.', rough:0.06, env:1.90, shell:0.17, gloss:1.0, product:'Graphene ceramic, up to 10H' },
  ];

  const setField = (name, val, html) => root.querySelectorAll('[data-field="'+name+'"]').forEach(el => { if (html) el.innerHTML = val; else el.textContent = val; });

  function fail() { if (loading) loading.hidden = true; root.dataset.failed = '1'; }

  let renderer;
  try { renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true, powerPreference:'high-performance' }); }
  catch (e) { fail(); return; }

  const scene  = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(33, 1, 0.1, 200);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.02;
  stage.appendChild(renderer.domElement);

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;

  const key = new THREE.DirectionalLight(0xffffff, 2.7); key.position.set(6, 8, 6); scene.add(key);
  const rim = new THREE.DirectionalLight(0xbcd0ff, 1.6); rim.position.set(-7, 5, -6); scene.add(rim);
  scene.add(new THREE.AmbientLight(0xffffff, 0.22));

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true; controls.dampingFactor = 0.07;
  controls.enableZoom = false; controls.enablePan = false;
  controls.minPolarAngle = 0.55; controls.maxPolarAngle = Math.PI / 2 - 0.04;
  controls.autoRotate = !REDUCED; controls.autoRotateSpeed = 1.0;

  const shellMat = new THREE.MeshStandardMaterial({ color:0xffffff, metalness:0.0, roughness:0.05, envMapIntensity:1.7, transparent:true, opacity:0.0, depthWrite:false });
  const PAINT = new Set(['Car_Paint', 'Carbon', 'body_paint']);
  const isPaint = (n) => PAINT.has(n) || /paint/i.test(n || '');

  const paints = [];
  const shells = [];
  const st  = { rough:0.5, env:0.6, shell:0 };
  const tgt = { ...st };
  let idx = 0, auto = !REDUCED, autoAt = 0, idleAt = 0;
  const AUTO_MS = 3600, RESUME_MS = 9000;

  function setStage(i, byUser) {
    idx = i; const S = STAGES[i];
    tgt.rough = S.rough; tgt.env = S.env; tgt.shell = S.shell;
    steps.forEach((b, j) => b.classList.toggle('active', j === i));
    steps.forEach((b, j) => b.classList.toggle('done', j < i));
    setField('num', S.n);
    setField('title', S.title);
    setField('desc', S.desc);
    setField('meter', '', false);
    root.querySelectorAll('[data-field="meter"]').forEach(el => { el.style.width = Math.round(S.gloss * 100) + '%'; });
    const pw = root.querySelector('[data-field="product-wrap"]');
    if (pw) { if (S.product) { pw.hidden = false; setField('product', S.product); } else pw.hidden = true; }
    if (byUser) { auto = false; idleAt = performance.now(); }
  }
  steps.forEach((b, i) => b.addEventListener('click', () => setStage(i, true)));
  // pause auto-advance while the user is spinning the car
  stage.addEventListener('pointerdown', () => { auto = false; idleAt = performance.now(); });

  function loadModel() {
    new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load(MODEL, (gltf) => {
      const car = gltf.scene; scene.add(car);
      const seen = new Set();
      car.traverse(o => {
        if (!o.isMesh || !o.material) return;
        if (isPaint(o.material.name)) {
          const m = o.material;
          if (!seen.has(m)) { seen.add(m); m.color.setHex(0x1b1f26); m.metalness = 0.62; paints.push(m); }
          const skin = new THREE.Mesh(o.geometry, shellMat); skin.renderOrder = 3; o.add(skin); shells.push(skin);
        }
      });

      // auto-fit: centre on the ground, frame the whole vehicle
      const box = new THREE.Box3().setFromObject(car);
      const size = new THREE.Vector3(); box.getSize(size);
      const ctr  = new THREE.Vector3(); box.getCenter(ctr);
      car.position.x -= ctr.x; car.position.z -= ctr.z; car.position.y -= box.min.y;
      const maxDim = Math.max(size.x, size.y, size.z);
      const ty = size.y * 0.46;
      controls.target.set(0, ty, 0);
      const fov = camera.fov * Math.PI / 180;
      const fitR = (maxDim * 0.6) / Math.tan(fov / 2);
      controls.minDistance = controls.maxDistance = fitR;
      const s = new THREE.Spherical(fitR, 1.24, 0.72);
      camera.position.setFromSpherical(s).add(controls.target);

      const shadow = new THREE.Mesh(
        new THREE.CircleGeometry(maxDim * 0.62, 64),
        new THREE.MeshBasicMaterial({ color:0x000000, transparent:true, opacity:0.5 })
      );
      shadow.rotation.x = -Math.PI / 2; shadow.position.y = 0.002; scene.add(shadow);

      if (loading) loading.hidden = true;
      setStage(0, false);
      autoAt = performance.now();
      resize();
      requestAnimationFrame(loop);
    }, undefined, () => fail());
  }

  let visible = false;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; }, { threshold:0 }).observe(stage);

  function loop(now) {
    if (visible) {
      if (auto && now - autoAt > AUTO_MS) { setStage((idx + 1) % STAGES.length, false); autoAt = now; }
      if (!auto && !REDUCED && now - idleAt > RESUME_MS) { auto = true; autoAt = now; }
      st.rough += (tgt.rough - st.rough) * 0.08;
      st.env   += (tgt.env   - st.env)   * 0.08;
      st.shell += (tgt.shell - st.shell) * 0.08;
      for (const m of paints) { m.roughness = st.rough; m.envMapIntensity = st.env; }
      shellMat.opacity = st.shell;
      controls.autoRotate = auto && !REDUCED;
      controls.update();
      renderer.render(scene, camera);
    }
    requestAnimationFrame(loop);
  }

  const arm = () => {
    const pre = new IntersectionObserver((es) => { if (es[0].isIntersecting) { pre.disconnect(); loadModel(); } }, { rootMargin:'800px 0px' });
    pre.observe(stage);
  };
  if (document.readyState === 'complete') arm();
  else addEventListener('load', arm, { once:true });

  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(stage);
  resize();
}
