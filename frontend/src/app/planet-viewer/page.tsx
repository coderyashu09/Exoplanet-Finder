"use client";

import { useEffect, useRef, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import * as THREE from "three";
import {
  Eye,
  RotateCcw,
  Sparkles,
  Telescope,
  Radio,
  Globe,
  Info,
  Layers,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";
import { useExperienceMode } from "@/context/ModeContext";
import {
  createTerrestrialPBRMaps,
  createGasGiantPBRMaps,
  createLavaWorldPBRMaps,
  createPlanetaryRingTexture,
  createAtmosphereShaderMaterial,
} from "@/lib/three/planetTextures";

interface PlanetProfile {
  id: string;
  name: string;
  system: string;
  kepid: number;
  type: string;
  radiusEarth: number;
  periodDays: number;
  tempKelvin: number;
  habitable: boolean;
  discoveredByAI: boolean;
  discoveryYear: number;
  discoveryMethod: string;
  textureType: "rocky_lava" | "ocean_habitable" | "super_earth" | "water_world" | "gas_giant";
  primaryColor: string;
  atmosphereColor: string;
  description: string;
  scientificNotes: string;
}

const PLANET_PROFILES: PlanetProfile[] = [
  {
    id: "kepler-90i",
    name: "Kepler-90i",
    system: "Kepler-90 System",
    kepid: 11442793,
    type: "Rocky Super-Earth",
    radiusEarth: 1.32,
    periodDays: 14.449,
    tempKelvin: 709,
    habitable: false,
    discoveredByAI: true,
    discoveryYear: 2017,
    discoveryMethod: "Transit / 1D Deep Learning CNN",
    textureType: "rocky_lava",
    primaryColor: "#c25934",
    atmosphereColor: "#ffaa66",
    description: "An intensely heated rocky planet orbiting close to its G0V star. It was discovered by Christopher Shallue (Google AI) and Andrew Vanderburg (NASA) using a two-view 1D CNN trained on Kepler observations.",
    scientificNotes: "Transit SNR was only 8.7, missed by initial automated pipelines. Surface temperature reaches approximately 709 K (~436 °C).",
  },
  {
    id: "kepler-186f",
    name: "Kepler-186f",
    system: "Kepler-186 System",
    kepid: 8120608,
    type: "Habitable Zone Earth-Size",
    radiusEarth: 1.17,
    periodDays: 129.944,
    tempKelvin: 188,
    habitable: true,
    discoveredByAI: false,
    discoveryYear: 2014,
    discoveryMethod: "Transit",
    textureType: "ocean_habitable",
    primaryColor: "#2b6b55",
    atmosphereColor: "#55ddaa",
    description: "The first validated Earth-sized exoplanet orbiting within the circumstellar habitable zone of another star, where liquid water could potentially persist.",
    scientificNotes: "Orbits an M1V red dwarf star. Receives approximately one-third of the heat and light that Earth receives from the Sun.",
  },
  {
    id: "kepler-452b",
    name: "Kepler-452b",
    system: "Kepler-452 System",
    kepid: 8311864,
    type: "Super-Earth around G2 Solar Twin",
    radiusEarth: 1.63,
    periodDays: 384.843,
    tempKelvin: 265,
    habitable: true,
    discoveredByAI: false,
    discoveryYear: 2015,
    discoveryMethod: "Transit",
    textureType: "super_earth",
    primaryColor: "#305f8a",
    atmosphereColor: "#66ccff",
    description: "Often described as 'Earth's older cousin', it takes 385 days to orbit a G2-class star almost identical in temperature and brightness to our Sun.",
    scientificNotes: "Semi-major axis is 1.046 AU. The parent star is roughly 6 billion years old (1.5 billion years older than our Sun).",
  },
  {
    id: "kepler-22b",
    name: "Kepler-22b",
    system: "Kepler-22 System",
    kepid: 10666592,
    type: "Water World / Sub-Neptune",
    radiusEarth: 2.38,
    periodDays: 289.862,
    tempKelvin: 262,
    habitable: true,
    discoveredByAI: false,
    discoveryYear: 2011,
    discoveryMethod: "Transit",
    textureType: "water_world",
    primaryColor: "#1d4e89",
    atmosphereColor: "#49e4e8",
    description: "The very first confirmed exoplanet discovered by NASA's Kepler mission to orbit safely inside the habitable zone of a Sun-like star.",
    scientificNotes: "Its 2.4 Earth radii bulk composition is hypothesized to be an ocean planet with a volatile-rich gaseous envelope.",
  },
  {
    id: "kepler-10b",
    name: "Kepler-10b",
    system: "Kepler-10 System",
    kepid: 11904151,
    type: "Ultra-Hot Lava World",
    radiusEarth: 1.47,
    periodDays: 0.837,
    tempKelvin: 2169,
    habitable: false,
    discoveredByAI: false,
    discoveryYear: 2011,
    discoveryMethod: "Transit",
    textureType: "rocky_lava",
    primaryColor: "#801b1b",
    atmosphereColor: "#ff4444",
    description: "The first rocky exoplanet confirmed by Kepler. Tidally locked to its host star, its dayside is estimated to be covered by molten iron and silicate magma oceans.",
    scientificNotes: "Completes an entire orbit in just 20 hours. Extreme surface temperatures exceed 2,100 K.",
  },
];

function PlanetViewerContent() {
  const searchParams = useSearchParams();
  const initialId = searchParams.get("planet") || "kepler-90i";

  const [selectedPlanet, setSelectedPlanet] = useState<PlanetProfile>(() => {
    return PLANET_PROFILES.find((p) => p.id.includes(initialId)) || PLANET_PROFILES[0];
  });

  const containerRef = useRef<HTMLDivElement>(null);
  const { quality } = useExperienceMode();

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight || 520;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020409);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 500);
    camera.position.set(0, 4, 32);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({
      antialias: quality !== "low",
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, quality === "ultra" ? 2 : 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    containerRef.current.replaceChildren(renderer.domElement);

    // 2. Starfield
    const starGeo = new THREE.BufferGeometry();
    const starCount = quality === "ultra" ? 2000 : 1200;
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 400;
      starPos[i + 1] = (Math.random() - 0.5) * 300;
      starPos[i + 2] = -40 - Math.random() * 200;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0x99bbdd, size: 1.0, transparent: true, opacity: 0.85 });
    const stars = new THREE.Points(starGeo, starMat);
    scene.add(stars);

    // 3. Central Exoplanet PBR Mesh
    const planetRadius = 8.5;
    const planetGeo = new THREE.SphereGeometry(planetRadius, 64, 64);

    let planetMat: THREE.Material;
    let cloudMesh: THREE.Mesh | null = null;
    let ringMesh: THREE.Mesh | null = null;

    if (selectedPlanet.textureType === "rocky_lava") {
      const lava = createLavaWorldPBRMaps();
      planetMat = new THREE.MeshStandardMaterial({
        map: lava.albedo,
        bumpMap: lava.bump,
        bumpScale: 0.85,
        roughness: 0.9,
        metalness: 0.1,
        emissive: new THREE.Color(0x661500),
        emissiveIntensity: 0.4,
      });
    } else if (selectedPlanet.textureType === "gas_giant") {
      const gas = createGasGiantPBRMaps("amber_gold");
      planetMat = new THREE.MeshStandardMaterial({
        map: gas.albedo,
        bumpMap: gas.bump,
        bumpScale: 0.35,
        roughness: 0.7,
        metalness: 0.05,
      });

      // Rings
      const ringGeo = new THREE.RingGeometry(planetRadius * 1.35, planetRadius * 2.3, 64);
      const ringTex = createPlanetaryRingTexture();
      const ringMat = new THREE.MeshStandardMaterial({
        map: ringTex,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.88,
        roughness: 0.8,
      });
      ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2.3;
      ringMesh.rotation.y = Math.PI / 9;
    } else {
      const earth = createTerrestrialPBRMaps(selectedPlanet.textureType === "water_world" ? "water" : "habitable");
      planetMat = new THREE.MeshStandardMaterial({
        map: earth.albedo,
        bumpMap: earth.bump,
        bumpScale: 0.75,
        roughnessMap: earth.roughness,
        roughness: 0.75,
        metalness: 0.08,
      });

      // Independent Clouds
      if (earth.clouds) {
        const cGeo = new THREE.SphereGeometry(planetRadius + 0.16, 64, 64);
        const cMat = new THREE.MeshStandardMaterial({
          map: earth.clouds,
          transparent: true,
          opacity: 0.85,
          blending: THREE.NormalBlending,
        });
        cloudMesh = new THREE.Mesh(cGeo, cMat);
        cloudMesh.rotation.z = THREE.MathUtils.degToRad(21.0);
      }
    }

    const planetMesh = new THREE.Mesh(planetGeo, planetMat);
    planetMesh.rotation.z = THREE.MathUtils.degToRad(21.0);
    scene.add(planetMesh);

    if (cloudMesh) scene.add(cloudMesh);
    if (ringMesh) planetMesh.add(ringMesh);

    // Atmospheric Rayleigh Scattering Rim (Shader)
    const atmoMat = createAtmosphereShaderMaterial(selectedPlanet.atmosphereColor, 2.7);
    const atmoGeo = new THREE.SphereGeometry(planetRadius + 0.5, 64, 64);
    const atmoMesh = new THREE.Mesh(atmoGeo, atmoMat);
    scene.add(atmoMesh);

    // 4. Dramatic Directional Lighting
    const sunLight = new THREE.DirectionalLight(0xfff6ea, 3.6);
    sunLight.position.set(-45, 18, 28);
    scene.add(sunLight);

    const ambientLight = new THREE.AmbientLight(0x081224, 0.5);
    scene.add(ambientLight);

    // 5. Interactive Mouse Orbit / Rotation
    let isDragging = false;
    let prevMousePos = { x: 0, y: 0 };
    const domElem = renderer.domElement;

    const onMouseDown = (e: MouseEvent) => {
      isDragging = true;
      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - prevMousePos.x;
      const dy = e.clientY - prevMousePos.y;

      planetMesh.rotation.y += dx * 0.008;
      planetMesh.rotation.x += dy * 0.008;

      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onWheel = (e: WheelEvent) => {
      camera.position.z = Math.max(14, Math.min(60, camera.position.z + e.deltaY * 0.04));
    };

    domElem.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    domElem.addEventListener("wheel", onWheel);

    // 6. Animation Loop
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      if (!isDragging) {
        planetMesh.rotation.y += 0.05 * delta;
        if (cloudMesh) {
          cloudMesh.rotation.y += 0.065 * delta;
        }
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight || 520;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      domElem.removeEventListener("mousedown", onMouseDown);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
      domElem.removeEventListener("wheel", onWheel);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, [selectedPlanet, quality]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      {/* Header */}
      <div className="border-b border-space-border pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-accent-cyan/30 bg-accent-cyan/10 px-3 py-1 text-xs font-mono text-accent-cyan mb-2">
            <Eye className="h-3.5 w-3.5" />
            <span>3D PLANETARY SURFACE & ATMOSPHERE INSPECTOR</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-astro-text font-mono">
            3D Exoplanet Detail Experience
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted mt-1">
            Rotate, zoom, and inspect physical properties of notable Kepler-confirmed exoplanets
          </p>
        </div>

        {/* Planet Quick Select Pills */}
        <div className="flex flex-wrap items-center gap-2">
          {PLANET_PROFILES.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedPlanet(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition border ${
                selectedPlanet.id === p.id
                  ? "bg-accent-blue text-space-950 font-bold border-accent-blue shadow-md"
                  : "bg-space-850 text-astro-muted border-space-border hover:text-white"
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Mandatory Scientific Honesty Alert */}
      <div className="rounded-xl border border-accent-gold/40 bg-accent-gold/5 p-4 flex items-start gap-3 text-xs font-mono text-astro-muted">
        <ShieldAlert className="h-5 w-5 text-accent-gold shrink-0 mt-0.5" />
        <div>
          <strong className="text-accent-gold uppercase">Scientific Transparency Note:</strong> The orbital period, transit depth, radius, and equilibrium temperatures shown below are derived from authentic NASA Kepler data. However, exoplanetary surface appearances cannot be directly resolved from photometric transit dips. The 3D surface textures, clouds, and oceans are artistic educational representations based on physical temperature and bulk density models.
        </div>
      </div>

      {/* Main 3D Viewport & Metadata Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Canvas Box (Col span 2) */}
        <div className="lg:col-span-2 relative rounded-2xl border border-space-border overflow-hidden bg-space-950 shadow-2xl h-[520px]">
          <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

          {/* Canvas Tag Overlay */}
          <div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
            <div className="flex items-center gap-2 bg-space-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-space-border text-xs font-mono">
              <span className="text-astro-muted">OBJECT:</span>
              <span className="text-white font-bold">{selectedPlanet.name}</span>
              <span className="text-accent-cyan text-[10px]">({selectedPlanet.type})</span>
            </div>
            {selectedPlanet.discoveredByAI && (
              <div className="flex items-center gap-1.5 bg-accent-emerald/10 border border-accent-emerald/40 px-3 py-1 rounded-lg text-xs font-mono text-accent-emerald font-bold">
                <Sparkles className="h-3.5 w-3.5" />
                <span>DISCOVERED VIA 1D CNN DEEP LEARNING</span>
              </div>
            )}
          </div>

          <div className="absolute bottom-4 left-4 z-20 text-[11px] font-mono text-astro-subtle bg-space-900/80 backdrop-blur px-3 py-1 rounded border border-space-border">
            Drag with left mouse to rotate · Scroll to zoom
          </div>
        </div>

        {/* Detailed Scientific Metadata Sidebar */}
        <div className="rounded-2xl border border-space-border bg-space-850 p-6 flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div>
              <span className="text-[10px] font-mono uppercase bg-space-800 text-astro-muted px-2 py-0.5 rounded border border-space-border">
                {selectedPlanet.system} · KIC {selectedPlanet.kepid}
              </span>
              <h2 className="text-2xl font-bold font-mono text-white mt-2">
                {selectedPlanet.name}
              </h2>
              <p className="text-xs text-astro-muted mt-2 leading-relaxed">
                {selectedPlanet.description}
              </p>
            </div>

            {/* Astrophysical Parameters Card */}
            <div className="rounded-xl bg-space-900 border border-space-border p-4 space-y-2.5 text-xs font-mono">
              <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                <span className="text-astro-muted">Planetary Radius:</span>
                <span className="text-accent-cyan font-bold">{selectedPlanet.radiusEarth.toFixed(2)} R⊕ ({selectedPlanet.radiusEarth}x Earth)</span>
              </div>
              <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                <span className="text-astro-muted">Orbital Period:</span>
                <span className="text-accent-blue font-bold">{selectedPlanet.periodDays.toFixed(3)} Days</span>
              </div>
              <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                <span className="text-astro-muted">Equilibrium Temp:</span>
                <span className="text-accent-gold font-bold">{selectedPlanet.tempKelvin} K (~{selectedPlanet.tempKelvin - 273} °C)</span>
              </div>
              <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                <span className="text-astro-muted">Circumstellar Habitable Zone:</span>
                <span className={selectedPlanet.habitable ? "text-accent-emerald font-bold" : "text-astro-subtle"}>
                  {selectedPlanet.habitable ? "Yes (Potential Liquid Water)" : "No (Extreme Temperatures)"}
                </span>
              </div>
              <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                <span className="text-astro-muted">Discovery Year:</span>
                <span className="text-astro-text">{selectedPlanet.discoveryYear}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-astro-muted">Detection Method:</span>
                <span className="text-accent-purple font-semibold">{selectedPlanet.discoveryMethod}</span>
              </div>
            </div>

            {/* Scientific Notes */}
            <div className="rounded-lg bg-space-900/60 border border-space-border/60 p-3 text-[11px] font-mono text-astro-subtle leading-relaxed">
              <span className="text-white font-bold block mb-1">Observation Provenance:</span>
              {selectedPlanet.scientificNotes}
            </div>
          </div>

          {/* Action Links */}
          <div className="pt-3 border-t border-space-border/60 flex flex-col gap-2">
            <Link
              href={`/detector?kepid=${selectedPlanet.kepid}&period=${selectedPlanet.periodDays}`}
              className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-accent-blue py-2 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition shadow"
            >
              <Telescope className="h-3.5 w-3.5" />
              Analyze Light Curve in Lab (KIC {selectedPlanet.kepid})
            </Link>
            <Link
              href={`/studio?kepid=${selectedPlanet.kepid}`}
              className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-space-border bg-space-800 py-2 text-xs font-mono font-medium text-white hover:bg-space-700 transition"
            >
              <Radio className="h-3.5 w-3.5 text-accent-cyan" />
              View Detrended Photometry
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PlanetViewerPage() {
  return (
    <Suspense fallback={<div className="p-8 text-center text-xs font-mono text-astro-subtle">Loading 3D Planet Viewer...</div>}>
      <PlanetViewerContent />
    </Suspense>
  );
}

