"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import * as THREE from "three";
import {
  BookOpen,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  HelpCircle,
  Telescope,
  Radio,
  ArrowRight,
  Info,
  CheckCircle2,
  ChevronDown,
} from "lucide-react";
import Link from "next/link";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
} from "recharts";

export default function TransitSimulatorPage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [speed, setSpeed] = useState<number>(1.0);
  const [orbitAngle, setOrbitAngle] = useState<number>(0); // 0 to 2*PI
  const [activeFaq, setActiveFaq] = useState<number | null>(0);

  const angleRef = useRef(orbitAngle);
  const isPlayingRef = useRef(isPlaying);
  const speedRef = useRef(speed);

  angleRef.current = orbitAngle;
  isPlayingRef.current = isPlaying;
  speedRef.current = speed;

  // Transit geometry: transit occurs around angle = PI / 2 (when planet is directly between star and camera)
  // Transit duration is roughly 30 degrees (PI/6)
  const isTransiting = useMemo(() => {
    const transitCenter = Math.PI / 2;
    const diff = Math.abs(angleRef.current - transitCenter);
    return diff < 0.25;
  }, [orbitAngle]);

  // Brightness calculation for educational light curve
  const currentFlux = useMemo(() => {
    const transitCenter = Math.PI / 2;
    const diff = Math.abs(orbitAngle - transitCenter);
    if (diff < 0.25) {
      // Limb darkened transit dip
      const depth = 0.018; // 1.8% dip (typical for hot Jupiter / large planet)
      const u = diff / 0.25;
      return 1.0 - depth * (1.0 - u * u);
    }
    return 1.0;
  }, [orbitAngle]);

  // Pre-generate full 360-degree educational light curve data for charting
  const educationalCurveData = useMemo(() => {
    const pts = [];
    const transitCenter = Math.PI / 2;
    for (let i = 0; i <= 100; i++) {
      const a = (i / 100) * 2 * Math.PI;
      const diff = Math.abs(a - transitCenter);
      let flux = 1.0;
      if (diff < 0.25) {
        const u = diff / 0.25;
        flux = 1.0 - 0.018 * (1.0 - u * u);
      }
      pts.push({
        phasePct: Math.round((i / 100) * 100),
        angleDeg: Math.round((a * 180) / Math.PI),
        flux: Number(flux.toFixed(4)),
      });
    }
    return pts;
  }, []);

  const currentPhasePct = Math.round((orbitAngle / (2 * Math.PI)) * 100);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight || 420;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x040711);

    // Position camera slightly elevated looking directly along transit path
    const camera = new THREE.PerspectiveCamera(40, width / height, 0.1, 500);
    camera.position.set(0, 14, 45);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.replaceChildren(renderer.domElement);

    // 2. Distant Starfield
    const starGeo = new THREE.BufferGeometry();
    const starCount = 800;
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 300;
      starPos[i + 1] = (Math.random() - 0.5) * 200;
      starPos[i + 2] = -50 - Math.random() * 150;
    }
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0x99bbdd, size: 0.8, transparent: true, opacity: 0.7 });
    const stars = new THREE.Points(starGeo, starMat);
    scene.add(stars);

    // 3. Central Glowing Host Star
    const starSphereGeo = new THREE.SphereGeometry(4.2, 32, 32);
    const starSphereMat = new THREE.MeshBasicMaterial({ color: 0xffe070 });
    const hostStar = new THREE.Mesh(starSphereGeo, starSphereMat);
    scene.add(hostStar);

    // Star Corona Glow
    const coronaGeo = new THREE.SphereGeometry(5.2, 32, 32);
    const coronaMat = new THREE.MeshBasicMaterial({
      color: 0xffaa20,
      transparent: true,
      opacity: 0.3,
      side: THREE.BackSide,
    });
    const corona = new THREE.Mesh(coronaGeo, coronaMat);
    scene.add(corona);

    // 4. Orbit Path Line
    const ORBIT_RADIUS = 18.0;
    const orbitRingGeo = new THREE.RingGeometry(ORBIT_RADIUS - 0.08, ORBIT_RADIUS + 0.08, 64);
    const orbitRingMat = new THREE.MeshBasicMaterial({
      color: 0x314972,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.6,
    });
    const orbitRing = new THREE.Mesh(orbitRingGeo, orbitRingMat);
    orbitRing.rotation.x = Math.PI / 2;
    scene.add(orbitRing);

    // 5. Orbiting Exoplanet
    const planetGeo = new THREE.SphereGeometry(1.4, 24, 24);
    const planetMat = new THREE.MeshStandardMaterial({
      color: 0x2266aa,
      roughness: 0.7,
      metalness: 0.1,
    });
    const planet = new THREE.Mesh(planetGeo, planetMat);
    scene.add(planet);

    // 6. Telescope Line-of-Sight Indicator
    // Dotted light cylinder pointing from star directly toward observer camera
    const losGeo = new THREE.CylinderGeometry(0.05, 0.05, 30, 8);
    const losMat = new THREE.MeshBasicMaterial({
      color: 0x49e4e8,
      transparent: true,
      opacity: 0.35,
    });
    const losLine = new THREE.Mesh(losGeo, losMat);
    losLine.rotation.x = Math.PI / 2;
    losLine.position.set(0, 0, 15);
    scene.add(losLine);

    // Lighting
    const pointLight = new THREE.PointLight(0xffffff, 2.8, 150);
    scene.add(pointLight);
    const ambientLight = new THREE.AmbientLight(0x112233, 1.0);
    scene.add(ambientLight);

    // Animation Loop
    let animId: number;
    const clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      if (isPlayingRef.current) {
        angleRef.current = (angleRef.current + delta * 0.8 * speedRef.current) % (2 * Math.PI);
        setOrbitAngle(angleRef.current);
      }

      // Update planet position along orbit
      // When angle = PI/2, x = 0, z = ORBIT_RADIUS (directly between star and camera)
      planet.position.x = Math.cos(angleRef.current) * ORBIT_RADIUS;
      planet.position.z = Math.sin(angleRef.current) * ORBIT_RADIUS;
      planet.rotation.y += 0.02;

      // Slight star rotation
      hostStar.rotation.y += 0.005;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight || 420;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", handleResize);
      renderer.dispose();
    };
  }, []);

  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsPlaying(false);
    const val = parseFloat(e.target.value);
    const rad = (val / 100) * 2 * Math.PI;
    setOrbitAngle(rad);
    angleRef.current = rad;
  };

  const handleReset = () => {
    setOrbitAngle(0);
    angleRef.current = 0;
    setIsPlaying(true);
  };

  const faqs = [
    {
      q: "What is an Exoplanet?",
      a: "An exoplanet (extrasolar planet) is any planet that orbits a star other than our Sun. The first confirmed exoplanet was discovered in the 1990s, and NASA's Kepler Space Telescope has discovered thousands more across the Milky Way.",
    },
    {
      q: "What is a Planetary Transit?",
      a: "A transit occurs when an exoplanet passes directly between its host star and an observer (like the Kepler telescope). As the planet transits, it blocks a tiny fraction of the star's starlight—typically between 0.01% for Earth-sized planets and 1% to 2% for Jupiter-sized gas giants.",
    },
    {
      q: "What is a Light Curve?",
      a: "A light curve is a graph showing stellar brightness (flux) over time. When no planet is in transit, the light curve stays flat. When a planet crosses the star, the light curve dips down, stays low for several hours, and then rises back up once the transit concludes.",
    },
    {
      q: "How does NASA Kepler find planets using transits?",
      a: "The Kepler spacecraft monitored over 150,000 stars every 29.4 minutes for 4 continuous years. By searching for periodic, repeating dips that happen at the exact same interval (the orbital period), astronomers identify candidate exoplanets.",
    },
    {
      q: "Why do we need Artificial Intelligence & Deep Learning?",
      a: "Thousands of non-planetary events mimic transits: eclipsing binary stars, background star blends, and spacecraft instrumental noise. Our Two-View 1D Convolutional Neural Network examines the entire orbit (Global View) and zooms into the transit (Local View) to automatically separate real planets from false alarms with 94.5% accuracy.",
    },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      {/* Header */}
      <div className="border-b border-space-border pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-accent-cyan/30 bg-accent-cyan/10 px-3 py-1 text-xs font-mono text-accent-cyan mb-2">
            <BookOpen className="h-3.5 w-3.5" />
            <span>EDUCATIONAL 3D TRANSIT SIMULATION · FOR ALL AUDIENCES</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-astro-text font-mono">
            How Planets Are Detected: The Transit Method
          </h1>
          <p className="text-xs sm:text-sm text-astro-muted mt-1">
            Watch a planet orbit its host star in real-time and observe how Kepler measures the resulting brightness dip
          </p>
        </div>

        <Link
          href="/detector"
          className="inline-flex items-center gap-2 rounded-lg bg-accent-blue px-4 py-2 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition shadow-md shadow-accent-blue/20"
        >
          <Telescope className="h-4 w-4" />
          Test Real AI on Candidates
        </Link>
      </div>

      {/* Notice Banner: Clearly distinguishing educational simulation from NASA data */}
      <div className="rounded-xl border border-accent-cyan/30 bg-accent-cyan/5 p-4 flex items-start gap-3 text-xs font-mono text-astro-muted">
        <Info className="h-5 w-5 text-accent-cyan shrink-0 mt-0.5" />
        <div>
          <strong className="text-accent-cyan uppercase">Scientific Disclosure:</strong> This 3D simulation and synchronized light curve are mathematical educational models designed for clear visual understanding. Real NASA observations and model training pipelines are located in the{" "}
          <Link href="/detector" className="text-white underline hover:text-accent-blue">
            AI Detection Laboratory
          </Link>{" "}
          and{" "}
          <Link href="/studio" className="text-white underline hover:text-accent-blue">
            Light Curve Studio
          </Link>.
        </div>
      </div>

      {/* 3D Simulation Viewport */}
      <div className="relative rounded-2xl border border-space-border overflow-hidden bg-space-950 shadow-2xl">
        <div ref={containerRef} className="w-full h-[400px]" />

        {/* Real-time Status Overlay */}
        <div className="absolute top-4 left-4 z-20 flex flex-col gap-2">
          <div className="flex items-center gap-2 bg-space-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-space-border text-xs font-mono">
            <span className="text-astro-muted">OBSERVATION STATUS:</span>
            {isTransiting ? (
              <span className="text-accent-emerald font-bold animate-pulse flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-accent-emerald" />
                TRANSIT IN PROGRESS (STARLIGHT BLOCKED)
              </span>
            ) : (
              <span className="text-astro-subtle flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-space-600" />
                OUT OF TRANSIT (STEADY BRIGHTNESS)
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 bg-space-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-space-border text-xs font-mono">
            <span className="text-astro-muted">MEASURED FLUX:</span>
            <span className={`font-bold ${isTransiting ? "text-accent-gold" : "text-astro-text"}`}>
              {(currentFlux * 100).toFixed(2)}%
            </span>
            {isTransiting && (
              <span className="text-accent-rose text-[10px]">
                (-{((1.0 - currentFlux) * 100).toFixed(2)}% dip)
              </span>
            )}
          </div>
        </div>

        {/* 3D Simulation Controls Bar */}
        <div className="absolute bottom-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-4 bg-space-900/85 backdrop-blur-md p-3 rounded-xl border border-space-border text-xs font-mono">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-1.5 rounded-lg bg-accent-blue px-3 py-1.5 text-space-950 font-bold hover:bg-accent-blue/90 transition shadow"
            >
              {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5 fill-space-950" />}
              {isPlaying ? "PAUSE" : "PLAY"}
            </button>

            <button
              onClick={handleReset}
              className="flex items-center gap-1 rounded-lg border border-space-border bg-space-800 px-2.5 py-1.5 text-astro-muted hover:text-white transition"
              title="Reset position to 0%"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </button>

            <div className="flex items-center gap-1">
              <span className="text-astro-subtle text-[11px]">SPEED:</span>
              {[0.5, 1.0, 2.0].map((s) => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={`px-1.5 py-0.5 rounded ${speed === s ? "bg-accent-blue text-space-950 font-bold" : "text-astro-muted hover:text-white"}`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>

          {/* Orbit Scrubber Slider */}
          <div className="flex items-center gap-3 flex-1 max-w-md">
            <span className="text-astro-subtle text-[11px] whitespace-nowrap">ORBIT POSITION:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={currentPhasePct}
              onChange={handleSliderChange}
              className="flex-1 accent-accent-blue cursor-pointer"
            />
            <span className="text-white font-bold w-10 text-right">{currentPhasePct}%</span>
          </div>
        </div>
      </div>

      {/* Synchronized Real-time Light Curve */}
      <div className="rounded-xl border border-space-border bg-space-850 p-5 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold font-mono text-astro-text uppercase tracking-wider flex items-center gap-2">
              <Radio className="h-4 w-4 text-accent-cyan" />
              Synchronized Light Curve Output (Brightness vs. Orbital Phase)
            </h3>
            <p className="text-xs text-astro-muted">
              The red cursor indicates where the planet is right now on its orbital cycle
            </p>
          </div>
          <div className="text-xs font-mono text-astro-subtle">
            Transit Dip Depth: <strong className="text-accent-gold">1.8%</strong>
          </div>
        </div>

        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={educationalCurveData} margin={{ top: 10, right: 15, left: -20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E2D4A" />
              <XAxis
                dataKey="phasePct"
                stroke="#627591"
                tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }}
                unit="%"
              />
              <YAxis
                domain={[0.975, 1.005]}
                stroke="#627591"
                tick={{ fill: "#627591", fontSize: 10, fontFamily: "monospace" }}
                tickFormatter={(v) => v.toFixed(3)}
              />
              <Tooltip
                contentStyle={{ backgroundColor: "#0D1424", borderColor: "#1E2D4A", fontSize: "11px", fontFamily: "monospace" }}
                formatter={(val: any) => [`${(Number(val) * 100).toFixed(2)}%`, "Relative Brightness"]}
                labelFormatter={(lbl) => `Orbital Phase: ${lbl}%`}
              />
              <Line
                type="monotone"
                dataKey="flux"
                stroke="#49E4E8"
                strokeWidth={2.5}
                dot={false}
                isAnimationActive={false}
              />
              {/* Active Marker Dot */}
              <ReferenceDot
                x={currentPhasePct}
                y={currentFlux}
                r={6}
                fill="#FF657A"
                stroke="#FFFFFF"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="flex justify-between text-[11px] font-mono text-astro-subtle pt-1">
          <span>0% (Behind Star)</span>
          <span className="text-accent-gold font-bold">25% (Transit Ingress & Midpoint)</span>
          <span>50% (Opposite Side)</span>
          <span>100% (Complete Orbit)</span>
        </div>
      </div>

      {/* Beginner-Friendly Scientific Explanations */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold font-mono text-astro-text flex items-center gap-2">
          <HelpCircle className="h-5 w-5 text-accent-blue" />
          Frequently Asked Questions: Understanding Exoplanet Science
        </h2>

        <div className="grid grid-cols-1 gap-3">
          {faqs.map((faq, idx) => {
            const isOpen = activeFaq === idx;
            return (
              <div
                key={idx}
                className="rounded-xl border border-space-border bg-space-850 overflow-hidden transition"
              >
                <button
                  onClick={() => setActiveFaq(isOpen ? null : idx)}
                  className="w-full flex items-center justify-between p-4 text-left font-mono text-sm font-bold text-astro-text hover:text-accent-blue transition"
                >
                  <span className="flex items-center gap-3">
                    <span className="text-accent-cyan font-bold">0{idx + 1}.</span>
                    {faq.q}
                  </span>
                  <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? "rotate-180 text-accent-blue" : "text-astro-subtle"}`} />
                </button>

                {isOpen && (
                  <div className="px-4 pb-4 pt-1 text-xs text-astro-muted leading-relaxed border-t border-space-border/50">
                    <p className="bg-space-900/60 p-3 rounded-lg border border-space-border/60">
                      {faq.a}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Next Step Exploration Banner */}
      <div className="rounded-xl border border-space-border bg-gradient-to-r from-space-850 to-space-900 p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-base font-bold font-mono text-white">
            Ready to test this with real NASA Kepler data?
          </h3>
          <p className="text-xs text-astro-muted mt-1">
            Now that you understand transits, explore the 8-planet Kepler-90 system or run our PyTorch CNN on genuine light curves.
          </p>
        </div>
        <div className="flex items-center gap-3 shrink-0">
          <Link
            href="/kepler90"
            className="rounded-lg border border-space-border bg-space-800 px-4 py-2 text-xs font-mono font-medium text-white hover:bg-space-700 transition"
          >
            Explore Kepler-90 →
          </Link>
          <Link
            href="/detector"
            className="rounded-lg bg-accent-blue px-4 py-2 text-xs font-mono font-bold text-space-950 hover:bg-accent-blue/90 transition shadow"
          >
            AI Detection Lab →
          </Link>
        </div>
      </div>
    </div>
  );
}

