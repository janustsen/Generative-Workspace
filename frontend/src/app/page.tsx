"use client";

import { useCallback, useEffect, useState } from "react";
import { Canvas } from "@/components/Canvas";
import { PromptBar } from "@/components/PromptBar";
import { api } from "@/lib/api";
import type { StoredModule } from "@/lib/types";

export default function Home() {
  const [modules, setModules] = useState<StoredModule[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listModules()
      .then((list) => setModules(list))
      .catch((err) => console.error("Failed to load modules", err))
      .finally(() => setLoading(false));
  }, []);

  const handleNewModule = useCallback((m: StoredModule) => {
    setModules((prev) => {
      const cascadeOffset = prev.length * 40;
      const placed: StoredModule = {
        ...m,
        config: {
          ...m.config,
          layout: {
            ...m.config.layout,
            x: m.config.layout.x + cascadeOffset,
            y: m.config.layout.y + cascadeOffset,
          },
        },
      };
      void api.patchModule(placed.id, placed.config).catch(() => {});
      return [...prev, placed];
    });
  }, []);

  const handleModuleChange = useCallback((updated: StoredModule) => {
    setModules((prev) =>
      prev.map((m) => (m.id === updated.id ? updated : m)),
    );
  }, []);

  return (
    <main className="flex-1 flex flex-col h-screen relative">
      <header className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between px-6 py-4 pointer-events-none">
        <div className="pointer-events-auto">
          <h1 className="text-xl font-semibold tracking-tight">Trus</h1>
          <p className="text-xs text-[var(--muted)] -mt-0.5">
            {loading
              ? "Loading…"
              : modules.length === 0
                ? "An empty canvas. Tell it what you want to organize."
                : `${modules.length} module${modules.length === 1 ? "" : "s"}`}
          </p>
        </div>
      </header>
      <Canvas modules={modules} onModuleChange={handleModuleChange} />
      <PromptBar onModule={handleNewModule} />
    </main>
  );
}
