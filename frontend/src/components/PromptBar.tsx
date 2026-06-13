"use client";

import { useState } from "react";
import { ApiError, api } from "@/lib/api";
import type { StoredModule } from "@/lib/types";

interface Props {
  onModule: (m: StoredModule) => void;
}

export function PromptBar({ onModule }: Props) {
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const v = prompt.trim();
    if (!v || loading) return;
    setLoading(true);
    setError(null);
    try {
      const { module } = await api.generateModule(v);
      onModule(module);
      setPrompt("");
    } catch (err) {
      if (err instanceof ApiError && err.refusal) {
        setError(err.refusal);
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={submit}
      className="absolute left-1/2 -translate-x-1/2 bottom-6 w-[min(720px,calc(100%-2rem))] z-10"
    >
      <div className="flex flex-col gap-1.5 rounded-2xl border border-[var(--border)] bg-[var(--surface)]/95 backdrop-blur shadow-2xl shadow-black/40">
        <div className="flex items-center gap-2 px-4 py-3">
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={loading}
            placeholder="Describe what you want to organize — e.g. track my workouts"
            className="flex-1 bg-transparent text-sm placeholder:text-[var(--muted)] focus:outline-none disabled:opacity-50"
            autoFocus
          />
          <button
            type="submit"
            disabled={!prompt.trim() || loading}
            className="rounded-md bg-[var(--accent)] text-[var(--accent-fg)] px-3 py-1.5 text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 transition"
          >
            {loading ? "Generating…" : "Generate"}
          </button>
        </div>
        {error && (
          <div className="px-4 pb-3 -mt-1">
            <div className="text-xs text-[var(--danger)]">
              {error}
            </div>
          </div>
        )}
      </div>
    </form>
  );
}
