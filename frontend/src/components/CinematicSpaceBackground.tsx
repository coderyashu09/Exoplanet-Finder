"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { useExperienceMode } from "@/context/ModeContext";
import {
  createTerrestrialPBRMaps,
  createAtmosphereShaderMaterial,
} from "@/lib/three/planetTextures";

export default function CinematicSpaceBackground() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { quality } = useExperienceMode();

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x020408);
    scene.fog = new THREE.FogExp2(0x020408, 0.0015);

    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 1000);
    camera.position.set(0, 0, 52);

    const renderer = new THREE.WebGLRenderer({
      antialias: quality !== "low",
      alpha: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, quality === "ultra" ? 2 : 1.5));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.35;
    renderer.shadowMap.enabled = quality !== "low";
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.replaceChildren(renderer.domElement);

    // 2. Multi-Depth Astronomical Starfield
    const starCount = quality === "ultra" ? 4500 : quality === "high" ? 3000 : 1500;
    const starGeo = new THREE.BufferGeometry();
    const starPos = new Float32Array(starCount * 3);
    const starColors = new Float32Array(starCount * 3);

    const palette = [
      new THREE.Color("#63B3FF"),
      new THREE.Color("#8B7CFF"),
      new THREE.Color("#FFFFFF"),
      new THREE.Color("#FFD166"),
      new THREE.Color("#49E4E8"),
      new THREE.Color("#E0E7FF"),
    ];

    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 650;
      starPos[i + 1] = (Math.random() - 0.5) * 450;
      starPos[i + 2] = -40 - Math.random() * 350;

      const c = palette[Math.floor(Math.random() * palette.length)];
      starColors[i] = c.r;
      starColors[i + 1] = c.g;
      starColors[i + 2] = c.b;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    starGeo.setAttribute("color", new THREE.BufferAttribute(starColors, 3));
    const starMat = new THREE.PointsMaterial({
      size: 1.1,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
    });
    const bgStars = new THREE.Points(starGeo, starMat);
    scene.add(bgStars);

    // Cosmic Dust & Faint Nebula Gas Particles
    const dustCount = quality === "low" ? 200 : 500;
    const dustGeo = new THREE.BufferGeometry();
    const dustPos = new Float32Array(dustCount * 3);
    for (let i = 0; i < dustCount * 3; i += 3) {
      dustPos[i] = (Math.random() - 0.5) * 140;
      dustPos[i + 1] = (Math.random() - 0.5) * 90;
      dustPos[i + 2] = (Math.random() - 0.5) * 70;
    }
    dustGeo.setAttribute("position", new THREE.BufferAttribute(dustPos, 3));
    const dustMat = new THREE.PointsMaterial({
      color: 0x58b9ff,
      size: 1.8,
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending,
    });
    const dustParticles = new THREE.Points(dustGeo, dustMat);
    scene.add(dustParticles);

    // 3. Massive Photorealistic Exoplanet (Dominating composition on the right)
    const PLANET_RADIUS = 21.0;
    const pbr = createTerrestrialPBRMaps("habitable");

    const planetGeo = new THREE.SphereGeometry(PLANET_RADIUS, 64, 64);
    const planetMat = new THREE.MeshStandardMaterial({
      map: pbr.albedo,
      bumpMap: pbr.bump,
      bumpScale: 0.85,
      roughnessMap: pbr.roughness,
      roughness: 0.8,
      metalness: 0.05,
    });

    const planetMesh = new THREE.Mesh(planetGeo, planetMat);
    // Positioned majestically on right side with cinematic crop
    planetMesh.position.set(24.5, -5.5, 4.0);
    planetMesh.rotation.z = THREE.MathUtils.degToRad(23.5);
    scene.add(planetMesh);

    // Independent Cloud Layer Sphere (rotates slightly faster)
    let cloudsMesh: THREE.Mesh | null = null;
    if (pbr.clouds) {
      const cloudGeo = new THREE.SphereGeometry(PLANET_RADIUS + 0.22, 64, 64);
      const cloudMat = new THREE.MeshStandardMaterial({
        map: pbr.clouds,
        transparent: true,
        opacity: 0.88,
        blending: THREE.NormalBlending,
        roughness: 0.9,
      });
      cloudsMesh = new THREE.Mesh(cloudGeo, cloudMat);
      cloudsMesh.position.copy(planetMesh.position);
      cloudsMesh.rotation.z = planetMesh.rotation.z;
      scene.add(cloudsMesh);
    }

    // Atmospheric Rayleigh Scattering Rim (Custom GLSL Shader)
    const atmoGeo = new THREE.SphereGeometry(PLANET_RADIUS + 0.95, 64, 64);
    const atmoMat = createAtmosphereShaderMaterial("#58B9FF", 2.6);
    const atmoMesh = new THREE.Mesh(atmoGeo, atmoMat);
    atmoMesh.position.copy(planetMesh.position);
    scene.add(atmoMesh);

    // 4. Physically Inspired Distant Star Lighting (Terminator Line)
    const sunLight = new THREE.DirectionalLight(0xfff7ea, 3.8);
    sunLight.position.set(-65, 20, 35);
    sunLight.castShadow = quality !== "low";
    scene.add(sunLight);

    const ambientLight = new THREE.AmbientLight(0x060f1e, 0.45);
    scene.add(ambientLight);

    // Subtle blue fill light from surrounding nebula
    const fillLight = new THREE.DirectionalLight(0x1a3a5c, 0.5);
    fillLight.position.set(40, -30, -20);
    scene.add(fillLight);

    // 5. Restrained Mouse Parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const onMouseMove = (e: MouseEvent) => {
      const halfW = window.innerWidth / 2;
      const halfH = window.innerHeight / 2;
      mouseX = (e.clientX - halfW) * 0.0006;
      mouseY = (e.clientY - halfH) * 0.0006;
    };
    window.addEventListener("mousemove", onMouseMove);

    // 6. 60 FPS Render Loop
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      // Smooth camera parallax
      targetX += (mouseX - targetX) * 0.04;
      targetY += (mouseY - targetY) * 0.04;
      camera.position.x = targetX * 10;
      camera.position.y = -targetY * 7;
      camera.lookAt(0, 0, 0);

      // Planet axial rotation
      planetMesh.rotation.y += 0.025 * delta;

      // Cloud layer rotates at differential speed
      if (cloudsMesh) {
        cloudsMesh.rotation.y += 0.035 * delta;
      }

      // Subtle celestial drift
      dustParticles.rotation.y += 0.008 * delta;
      bgStars.rotation.y += 0.0015 * delta;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, [quality]);

  return (
    <div
      ref={containerRef}
      className="absolute inset-0 w-full h-full pointer-events-none select-none z-0"
    />
  );
}
