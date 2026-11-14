import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/Navigation";
import { ModeProvider } from "@/context/ModeContext";

export const metadata: Metadata = {
  title: "EXOPLANET FINDER — Beyond Our Solar System",
  description: "Discover Worlds. Explore the Unknown. Powered by AI. Authentic NASA Kepler DR24 observations & PyTorch Two-View 1D CNN.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-space-950 text-astro-text antialiased selection:bg-accent-blue/30 selection:text-white flex flex-col">
        <ModeProvider>
          <Navigation />
          <main className="flex-1 w-full flex flex-col">
            {children}
          </main>
          <footer className="border-t border-space-border bg-space-950 py-6 text-center text-xs text-astro-subtle font-mono">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <p>
                EXOPLANET FINDER · NASA Kepler Q1–Q17 DR24 Mission · PyTorch 1D CNN
              </p>
              <p className="text-astro-muted">
                Discover Worlds. Explore the Unknown. Powered by AI.
              </p>
            </div>
          </footer>
        </ModeProvider>
      </body>
    </html>
  );
}
