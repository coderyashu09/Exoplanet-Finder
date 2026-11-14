"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

export type ExperienceMode = "explore" | "research";
export type GraphicsQuality = "low" | "medium" | "high" | "ultra";

interface ModeContextType {
  mode: ExperienceMode;
  setMode: (mode: ExperienceMode) => void;
  toggleMode: () => void;
  quality: GraphicsQuality;
  setQuality: (quality: GraphicsQuality) => void;
  showExplainer: boolean;
  setShowExplainer: (show: boolean) => void;
}

const ModeContext = createContext<ModeContextType>({
  mode: "explore",
  setMode: () => {},
  toggleMode: () => {},
  quality: "high",
  setQuality: () => {},
  showExplainer: false,
  setShowExplainer: () => {},
});

export function ModeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ExperienceMode>("explore");
  const [quality, setQuality] = useState<GraphicsQuality>("high");
  const [showExplainer, setShowExplainer] = useState<boolean>(false);

  useEffect(() => {
    try {
      const savedMode = localStorage.getItem("exo_mode") as ExperienceMode;
      if (savedMode) setMode(savedMode);
      const savedQuality = localStorage.getItem("exo_quality") as GraphicsQuality;
      if (savedQuality) setQuality(savedQuality);
    } catch {}
  }, []);

  const handleSetMode = (m: ExperienceMode) => {
    setMode(m);
    try {
      localStorage.setItem("exo_mode", m);
    } catch {}
  };

  const handleSetQuality = (q: GraphicsQuality) => {
    setQuality(q);
    try {
      localStorage.setItem("exo_quality", q);
    } catch {}
  };

  const toggleMode = () => {
    handleSetMode(mode === "explore" ? "research" : "explore");
  };

  return (
    <ModeContext.Provider
      value={{
        mode,
        setMode: handleSetMode,
        toggleMode,
        quality,
        setQuality: handleSetQuality,
        showExplainer,
        setShowExplainer,
      }}
    >
      {children}
    </ModeContext.Provider>
  );
}

export const useExperienceMode = () => useContext(ModeContext);

