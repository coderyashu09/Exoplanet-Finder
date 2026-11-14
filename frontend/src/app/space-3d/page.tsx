"use client";

import { useEffect, useRef, useState, Suspense } from "react";
import * as THREE from "three";
import {
  Compass,
  RotateCcw,
  Sparkles,
  Info,
  Telescope,
  Radio,
  Eye,
  Sliders,
  HelpCircle,
  ExternalLink,
  Layers,
  ChevronRight,
  X,
  Play,
  Pause,
} from "lucide-react";
import Link from "next/link";
import { api, CatalogObject, CatalogPlanet } from "@/lib/api";
import { useExperienceMode } from "@/context/ModeContext";
import {
  createTerrestrialPBRMaps,
  createGasGiantPBRMaps,
  createLavaWorldPBRMaps,
  createPlanetaryRingTexture,
  createAtmosphereShaderMaterial,
} from "@/lib/three/planetTextures";

export default function UniverseExplorer3DPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [catalogObjects, setCatalogObjects] = useState<CatalogObject[]>([]);
  const [selectedSystem, setSelectedSystem] = useState<CatalogObject | null>(null);
  const [selectedPlanet, setSelectedPlanet] = useState<CatalogPlanet | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [speed, setSpeed] = useState<number>(1.0);
  const [showOrbits, setShowOrbits] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [showHelp, setShowHelp] = useState<boolean>(false);

  const { mode, quality } = useExperienceMode();

  const isPlayingRef = useRef(isPlaying);
  const speedRef = useRef(speed);
  const showOrbitsRef = useRef(showOrbits);

  isPlayingRef.current = isPlaying;
  speedRef.current = speed;
  showOrbitsRef.current = showOrbits;

  // Camera focus animation controller
  const targetCamPos = useRef<THREE.Vector3 | null>(null);
  const targetCamLook = useRef<THREE.Vector3 | null>(null);

  useEffect(() => {
    api.getCatalogObjects()
      .then((data) => {
        setCatalogObjects(data);
        if (data.length > 0) {
          setSelectedSystem(data[0]); // Kepler-90 default
          if (data[0].planets.length > 2) {
            setSelectedPlanet(data[0].planets[2]); // Kepler-90i AI planet
          }
        }
      })
      .catch((err) => console.error("Error loading catalog objects", err));
  }, []);

  useEffect(() => {
    if (!containerRef.current || catalogObjects.length === 0) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight || 580;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020409);
    scene.fog = new THREE.FogExp2(0x020409, 0.0018);

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 50, 75);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: quality !== "low", alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, quality === "ultra" ? 2 : 1.5));
    containerRef.current.replaceChildren(renderer.domElement);

    // 2. Starfield & Cosmic Dust
    const starCount = quality === "ultra" ? 4000 : quality === "high" ? 2500 : 1200;
    const starGeo = new THREE.BufferGeometry();
    const starPos = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);

    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 600;
      starPos[i + 1] = (Math.random() - 0.5) * 400;
      starPos[i + 2] = (Math.random() - 0.5) * 500;

      const temp = 0.5 + Math.random() * 0.5;
      starColors[i] = temp;
      starColors[i + 1] = temp * 0.9;
      starColors[i + 2] = 1.0;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    starGeo.setAttribute("color", new THREE.BufferAttribute(starColors, 3));
    const starMat = new THREE.PointsMaterial({ size: 1.0, vertexColors: true, transparent: true, opacity: 0.8 });
    const stars = new THREE.Points(starGeo, starMat);
    scene.add(stars);

    // 3. Populate Curated Star Systems
    interface SystemGroupItem {
      object: CatalogObject;
      group: THREE.Group;
      starMesh: THREE.Mesh;
      planetMeshes: Array<{
        planet: CatalogPlanet;
        mesh: THREE.Mesh;
        orbitR: number;
        speed: number;
        angle: number;
        orbitLine: THREE.Mesh;
      }>;
    }

    const systemGroups: SystemGroupItem[] = [];
    const raycastTargets: THREE.Object3D[] = [];

    catalogObjects.forEach((obj) => {
      const sysGroup = new THREE.Group();
      sysGroup.position.set(obj.coordinates_3d.x, obj.coordinates_3d.y, obj.coordinates_3d.z);
      scene.add(sysGroup);

      // Star Sphere
      const starRadius = Math.max(1.5, obj.radius_solar * 2.2);
      const sGeo = new THREE.SphereGeometry(starRadius, 28, 28);
      const starColor = obj.spectral_type.startsWith("M")
        ? 0xff5533
        : obj.spectral_type.startsWith("K")
        ? 0xff9944
        : 0xffea70;
      const sMat = new THREE.MeshBasicMaterial({ color: starColor });
      const starMesh = new THREE.Mesh(sGeo, sMat);
      starMesh.userData = { type: "star", object: obj };
      sysGroup.add(starMesh);
      raycastTargets.push(starMesh);

      // Star Glow
      const glowGeo = new THREE.SphereGeometry(starRadius * 1.3, 24, 24);
      const glowMat = new THREE.MeshBasicMaterial({
        color: starColor,
        transparent: true,
        opacity: 0.28,
        side: THREE.BackSide,
      });
      const glowMesh = new THREE.Mesh(glowGeo, glowMat);
      sysGroup.add(glowMesh);

      // Star Light
      const pLight = new THREE.PointLight(starColor, 2.0, 120);
      sysGroup.add(pLight);

      // Planets & Orbits
      const planetMeshes: SystemGroupItem["planetMeshes"] = [];

      obj.planets.forEach((p, pIdx) => {
        const orbitR = Math.max(4.0, (p.semi_major_axis_au || (pIdx + 1) * 0.15) * 28.0 + 3.0);

        // Orbit Line
        const ringGeo = new THREE.RingGeometry(orbitR - 0.05, orbitR + 0.05, 64);
        const ringMat = new THREE.MeshBasicMaterial({
          color: p.discovered_by_ai ? 0x35d49a : 0x1e2d4a,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: p.discovered_by_ai ? 0.8 : 0.4,
        });
        const orbitLine = new THREE.Mesh(ringGeo, ringMat);
        orbitLine.rotation.x = Math.PI / 2;
        sysGroup.add(orbitLine);

        // Photorealistic Planetary Mesh Generation based on physical classification
        const pR = Math.max(0.45, (p.radius_earth / 11.3) * 1.5 + 0.3);
        const pGeo = new THREE.SphereGeometry(pR, 32, 32);

        let pMat: THREE.Material;
        const isGasGiant = p.radius_earth >= 6.0;
        const isLava = p.equilibrium_temp_k && p.equilibrium_temp_k > 650;
        const isHabitable = p.is_habitable_zone || (p.radius_earth > 1.0 && p.radius_earth < 2.5 && !isLava);

        if (isGasGiant) {
          const gasMaps = createGasGiantPBRMaps(p.radius_earth > 9.0 ? "amber_gold" : "azure_neptune");
          pMat = new THREE.MeshStandardMaterial({
            map: gasMaps.albedo,
            bumpMap: gasMaps.bump,
            bumpScale: 0.3,
            roughness: 0.7,
            metalness: 0.05,
          });
        } else if (isLava) {
          const lavaMaps = createLavaWorldPBRMaps();
          pMat = new THREE.MeshStandardMaterial({
            map: lavaMaps.albedo,
            bumpMap: lavaMaps.bump,
            bumpScale: 0.6,
            roughness: 0.9,
            emissive: new THREE.Color(0x551100),
            emissiveIntensity: 0.35,
          });
        } else if (isHabitable) {
          const earthMaps = createTerrestrialPBRMaps("habitable");
          pMat = new THREE.MeshStandardMaterial({
            map: earthMaps.albedo,
            bumpMap: earthMaps.bump,
            bumpScale: 0.5,
            roughnessMap: earthMaps.roughness,
            roughness: 0.7,
            metalness: 0.1,
          });
        } else {
          const aridMaps = createTerrestrialPBRMaps("arid");
          pMat = new THREE.MeshStandardMaterial({
            map: aridMaps.albedo,
            bumpMap: aridMaps.bump,
            bumpScale: 0.7,
            roughness: 0.85,
          });
        }

        const pMesh = new THREE.Mesh(pGeo, pMat);
        pMesh.userData = { type: "planet", planet: p, system: obj };

        // Planetary Rings for massive gas giants
        if (isGasGiant && p.radius_earth >= 7.5) {
          const ringGeo = new THREE.RingGeometry(pR * 1.4, pR * 2.3, 48);
          const ringTex = createPlanetaryRingTexture();
          const ringMat = new THREE.MeshStandardMaterial({
            map: ringTex,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.85,
            roughness: 0.8,
          });
          const ringMesh = new THREE.Mesh(ringGeo, ringMat);
          ringMesh.rotation.x = Math.PI / 2.3;
          ringMesh.rotation.y = Math.PI / 8;
          pMesh.add(ringMesh);
        }

        // Atmospheric Rayleigh Scattering Rim
        if (isHabitable || isGasGiant) {
          const atmoMat = createAtmosphereShaderMaterial(isHabitable ? "#49E4E8" : "#8B7CFF", 3.0);
          const atmoMesh = new THREE.Mesh(new THREE.SphereGeometry(pR * 1.05, 32, 32), atmoMat);
          pMesh.add(atmoMesh);
        }

        sysGroup.add(pMesh);
        raycastTargets.push(pMesh);

        const startAngle = (pIdx * (Math.PI / 3)) + Math.random();
        pMesh.position.set(Math.cos(startAngle) * orbitR, 0, Math.sin(startAngle) * orbitR);

        planetMeshes.push({
          planet: p,
          mesh: pMesh,
          orbitR,
          speed: (2 * Math.PI) / (p.period_days * 1.2),
          angle: startAngle,
          orbitLine,
        });
      });

      systemGroups.push({
        object: obj,
        group: sysGroup,
        starMesh,
        planetMeshes,
      });
    });

    const ambientLight = new THREE.AmbientLight(0x1a2638, 1.2);
    scene.add(ambientLight);

    // 4. Mouse Drag & Orbit Controls
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

      scene.rotation.y += dx * 0.005;
      scene.rotation.x = Math.max(-0.8, Math.min(0.8, scene.rotation.x + dy * 0.005));

      prevMousePos = { x: e.clientX, y: e.clientY };
    };

    const onMouseUp = () => {
      isDragging = false;
    };

    const onWheel = (e: WheelEvent) => {
      camera.position.z = Math.max(15, Math.min(180, camera.position.z + e.deltaY * 0.06));
    };

    // Object Selection via Raycasting
    const raycaster = new THREE.Raycaster();
    const mouseVec = new THREE.Vector2();

    const onClick = (e: MouseEvent) => {
      const rect = domElem.getBoundingClientRect();
      mouseVec.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouseVec.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouseVec, camera);
      const intersects = raycaster.intersectObjects(raycastTargets);

      if (intersects.length > 0) {
        const hit = intersects[0].object;
        if (hit.userData.type === "star") {
          setSelectedSystem(hit.userData.object);
          setSelectedPlanet(hit.userData.object.planets[0] || null);
        } else if (hit.userData.type === "planet") {
          setSelectedSystem(hit.userData.system);
          setSelectedPlanet(hit.userData.planet);
        }
      }
    };

    domElem.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    domElem.addEventListener("wheel", onWheel);
    domElem.addEventListener("click", onClick);

    // 5. Animation Loop
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      if (isPlayingRef.current) {
        systemGroups.forEach((sys) => {
          sys.starMesh.rotation.y += 0.006;
          sys.planetMeshes.forEach((item) => {
            item.angle += item.speed * delta * speedRef.current;
            item.mesh.position.x = Math.cos(item.angle) * item.orbitR;
            item.mesh.position.z = Math.sin(item.angle) * item.orbitR;
            item.mesh.rotation.y += 0.02;
            item.orbitLine.visible = showOrbitsRef.current;
          });
        });
      }

      // Smooth camera transition if focused
      if (targetCamPos.current && targetCamLook.current) {
        camera.position.lerp(targetCamPos.current, 0.05);
        camera.lookAt(targetCamLook.current);
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight || 580;
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
      domElem.removeEventListener("click", onClick);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, [catalogObjects, quality]);

  const handleResetCamera = () => {
    targetCamPos.current = new THREE.Vector3(0, 50, 75);
    targetCamLook.current = new THREE.Vector3(0, 0, 0);
  };

  const handleFocusSystem = (sys: CatalogObject) => {
    setSelectedSystem(sys);
    setSelectedPlanet(sys.planets[0] || null);
    targetCamPos.current = new THREE.Vector3(
      sys.coordinates_3d.x,
      sys.coordinates_3d.y + 25,
      sys.coordinates_3d.z + 40
    );
    targetCamLook.current = new THREE.Vector3(
      sys.coordinates_3d.x,
      sys.coordinates_3d.y,
      sys.coordinates_3d.z
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      {/* Header */}
      <div className="border-b border-space-border pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-accent-blue/30 bg-accent-blue/10 px-3 py-1 text-xs font-mono text-accent-blue mb-2">
            <Compass className="h-3.5 w-3.5" />
            <span>INTERACTIVE 3D ASTRONOMICAL ENVIRONMENT · KEPLER ARCHIVE</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-astro-text font-mono">
            Interactive 3D Universe Explorer
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted mt-1">
            Navigate through genuine star systems, examine calculated orbits, and inspect verified exoplanet properties
          </p>
        </div>

        {/* Action Controls & Help Button */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowHelp(true)}
            className="flex items-center gap-1.5 rounded-lg border border-space-border bg-space-850 px-3 py-1.5 text-xs font-mono text-astro-muted hover:text-white transition"
          >
            <HelpCircle className="h-4 w-4" />
            Controls Guide
          </button>
          <button
            onClick={handleResetCamera}
            className="flex items-center gap-1.5 rounded-lg border border-space-border bg-space-850 px-3 py-1.5 text-xs font-mono text-astro-muted hover:text-white transition"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Reset Camera
          </button>
        </div>
      </div>

      {/* 3D Universe Viewport Container */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 3D Canvas Box (Col span 2) */}
        <div className="lg:col-span-2 relative rounded-2xl border border-space-border overflow-hidden bg-space-950 shadow-2xl h-[560px]">
          <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

          {/* Quick Controls HUD on Canvas Top */}
          <div className="absolute top-4 left-4 z-20 flex flex-wrap items-center gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-1.5 bg-space-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-space-border text-xs font-mono text-white hover:border-accent-blue transition"
            >
              {isPlaying ? <Pause className="h-3.5 w-3.5 text-accent-blue" /> : <Play className="h-3.5 w-3.5 fill-accent-blue text-accent-blue" />}
              <span>{isPlaying ? "PAUSE" : "RESUME"}</span>
            </button>

            <button
              onClick={() => setShowOrbits(!showOrbits)}
              className={`px-3 py-1.5 rounded-lg border text-xs font-mono transition ${
                showOrbits ? "bg-accent-blue/15 border-accent-blue text-accent-blue" : "bg-space-900/90 border-space-border text-astro-muted"
              }`}
            >
              Orbits {showOrbits ? "ON" : "OFF"}
            </button>

            <div className="flex items-center gap-1 bg-space-900/90 backdrop-blur-md px-2 py-1.5 rounded-lg border border-space-border text-xs font-mono text-astro-muted">
              <span>SPEED:</span>
              {[0.5, 1.0, 2.5].map((s) => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={`px-1.5 py-0.5 rounded ${speed === s ? "bg-accent-blue text-space-950 font-bold" : "hover:text-white"}`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>

          {/* Target Star Systems Quick-Selector (Canvas Bottom) */}
          <div className="absolute bottom-4 left-4 right-4 z-20 flex overflow-x-auto gap-2 bg-space-900/80 backdrop-blur-md p-2 rounded-xl border border-space-border no-scrollbar">
            {catalogObjects.map((obj) => {
              const isSelected = selectedSystem?.id === obj.id;
              return (
                <button
                  key={obj.id}
                  onClick={() => handleFocusSystem(obj)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono whitespace-nowrap transition border ${
                    isSelected
                      ? "bg-space-800 border-accent-blue text-white font-bold"
                      : "bg-space-850/60 border-space-border/60 text-astro-muted hover:text-white"
                  }`}
                >
                  <span className="h-2 w-2 rounded-full bg-accent-blue" />
                  <span>{obj.name.split(" ")[0]}</span>
                  <span className="text-[10px] text-accent-cyan font-normal">({obj.confirmed_planets_count}p)</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected System & Object Inspector Side Panel */}
        <div className="rounded-2xl border border-space-border bg-space-850 p-6 flex flex-col justify-between space-y-4">
          {selectedSystem ? (
            <div className="space-y-4">
              {/* Scientific Visualization Category Badge */}
              <div className="flex items-center justify-between">
                <span
                  className={`text-[10px] font-mono font-bold px-2.5 py-1 rounded-full border ${
                    selectedSystem.visualization_category === "Observationally supported object"
                      ? "bg-accent-emerald/10 text-accent-emerald border-accent-emerald/30"
                      : selectedSystem.visualization_category === "Catalog-parameter-based visualization"
                      ? "bg-accent-gold/10 text-accent-gold border-accent-gold/30"
                      : "bg-accent-cyan/10 text-accent-cyan border-accent-cyan/30"
                  }`}
                >
                  {selectedSystem.visualization_category}
                </span>
                <span className="text-xs font-mono text-astro-subtle">
                  KIC {selectedSystem.kepid}
                </span>
              </div>

              {/* System Title */}
              <div>
                <h2 className="text-xl font-bold font-mono text-white">
                  {selectedSystem.name}
                </h2>
                <p className="text-xs text-astro-muted mt-1 leading-relaxed">
                  {selectedSystem.scientific_summary}
                </p>
              </div>

              {/* Host Star Physical Metrics */}
              <div className="rounded-xl bg-space-900 border border-space-border p-3.5 space-y-2 text-xs font-mono">
                <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                  <span className="text-astro-muted">Spectral Class:</span>
                  <span className="text-accent-gold font-bold">{selectedSystem.spectral_type}</span>
                </div>
                <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                  <span className="text-astro-muted">Distance:</span>
                  <span className="text-astro-text">{selectedSystem.distance_ly.toLocaleString()} Light-Years</span>
                </div>
                <div className="flex justify-between border-b border-space-border/50 pb-1.5">
                  <span className="text-astro-muted">Star Temperature:</span>
                  <span className="text-accent-cyan">{selectedSystem.temperature_k.toLocaleString()} K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-astro-muted">Confirmed Planets:</span>
                  <span className="text-accent-emerald font-bold">{selectedSystem.confirmed_planets_count} Orbiting Worlds</span>
                </div>
              </div>

              {/* Planets Selector in this System */}
              <div className="space-y-2">
                <span className="text-[11px] font-mono text-astro-muted uppercase tracking-wider block">
                  Orbiting Worlds ({selectedSystem.planets.length})
                </span>
                <div className="grid grid-cols-2 gap-2">
                  {selectedSystem.planets.map((p) => {
                    const isSelected = selectedPlanet?.name === p.name;
                    return (
                      <button
                        key={p.name}
                        onClick={() => setSelectedPlanet(p)}
                        className={`p-2 rounded-lg border text-left font-mono text-xs transition ${
                          isSelected
                            ? "bg-space-800 border-accent-blue text-white"
                            : "bg-space-900/60 border-space-border/60 text-astro-muted hover:text-white"
                        }`}
                      >
                        <div className="flex items-center gap-1.5">
                          <span className="h-2 w-2 rounded-full" style={{ backgroundColor: p.color }} />
                          <span className="font-bold">{p.name}</span>
                        </div>
                        <div className="text-[10px] text-astro-subtle mt-1">
                          {p.period_days.toFixed(1)}d · {p.radius_earth.toFixed(2)} R⊕
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Selected Planet Details */}
              {selectedPlanet && (
                <div className="rounded-xl border border-accent-blue/30 bg-accent-blue/5 p-3.5 space-y-2 text-xs font-mono">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-accent-blue">{selectedPlanet.name}</span>
                    {selectedPlanet.discovered_by_ai && (
                      <span className="text-[9px] font-bold bg-accent-emerald/20 text-accent-emerald px-1.5 py-0.5 rounded">
                        DISCOVERED BY AI
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-astro-muted leading-relaxed">
                    {selectedPlanet.description}
                  </p>
                  <div className="flex justify-between text-[11px] pt-1 border-t border-accent-blue/20">
                    <span className="text-astro-subtle">Habitable Zone:</span>
                    <span className={selectedPlanet.is_habitable_zone ? "text-accent-emerald font-bold" : "text-astro-muted"}>
                      {selectedPlanet.is_habitable_zone ? "Yes (Circumstellar)" : "No"}
                    </span>
                  </div>
                </div>
              )}

              {/* Provenance Citation */}
              <div className="text-[10px] font-mono text-astro-subtle leading-tight pt-1">
                Data Provenance: {selectedSystem.provenance_reference}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-xs font-mono text-astro-subtle">
              Select a star system to inspect details
            </div>
          )}

          {/* Quick Handoff Action Links */}
          {selectedSystem && (
            <div className="pt-3 border-t border-space-border/60 flex flex-col gap-2">
              <Link
                href={`/detector?kepid=${selectedSystem.kepid}&period=${selectedPlanet?.period_days || 10}`}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-accent-blue py-2 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition shadow"
              >
                <Telescope className="h-3.5 w-3.5" />
                Analyze KIC {selectedSystem.kepid} in Neural Lab
              </Link>
              <Link
                href={`/planet-viewer?system=${selectedSystem.id}&planet=${selectedPlanet?.letter || "b"}`}
                className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-space-border bg-space-800 py-2 text-xs font-mono font-medium text-white hover:bg-space-700 transition"
              >
                <Eye className="h-3.5 w-3.5 text-accent-cyan" />
                Inspect in 3D Planet Viewer
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Controls Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="rounded-2xl border border-space-border bg-space-900 p-6 max-w-md w-full space-y-4 font-mono text-xs">
            <div className="flex items-center justify-between border-b border-space-border pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <HelpCircle className="h-4 w-4 text-accent-blue" />
                3D Navigation Controls Guide
              </h3>
              <button onClick={() => setShowHelp(false)} className="text-astro-subtle hover:text-white">
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="space-y-3 text-astro-muted">
              <div className="flex justify-between p-2 rounded bg-space-850 border border-space-border">
                <span className="font-bold text-white">Rotate View:</span>
                <span>Left-Click & Drag</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-space-850 border border-space-border">
                <span className="font-bold text-white">Zoom In / Out:</span>
                <span>Mouse Scroll Wheel</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-space-850 border border-space-border">
                <span className="font-bold text-white">Select Star / Planet:</span>
                <span>Click directly on object</span>
              </div>
              <div className="flex justify-between p-2 rounded bg-space-850 border border-space-border">
                <span className="font-bold text-white">Reset View:</span>
                <span>Click &quot;Reset Camera&quot; button</span>
              </div>
            </div>

            <p className="text-[11px] text-astro-subtle leading-relaxed">
              Orbital paths follow Keplerian mechanics where inner planets orbit significantly faster than outer worlds.
            </p>

            <button
              onClick={() => setShowHelp(false)}
              className="w-full rounded-lg bg-accent-blue py-2 text-space-950 font-bold hover:bg-accent-blue/90 transition"
            >
              Close Guide
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
