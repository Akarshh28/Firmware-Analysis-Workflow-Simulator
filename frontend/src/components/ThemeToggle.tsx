"use client";

import React, { useState, useEffect } from "react";
import { useTheme } from "next-themes";
import { Sun, Moon, Monitor } from "lucide-react";

export function ThemeToggle() {
  const [mounted, setMounted] = useState(false);
  const { theme, setTheme } = useTheme();

  // useEffect only runs on the client, so now we can safely show the UI
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
  }, []);

  if (!mounted) {
    return null; // Prevent hydration mismatch
  }

  const themes = [
    { id: "light", label: "Day", icon: <Sun size={14} /> },
    { id: "dark", label: "Dark", icon: <Moon size={14} /> },
    { id: "midnight", label: "Midnight", icon: <Monitor size={14} /> },
  ];

  return (
    <div style={{ display: "flex", gap: "4px", padding: "4px", background: "var(--bg-tertiary)", borderRadius: "var(--radius-md)" }}>
      {themes.map((t) => (
        <button
          key={t.id}
          onClick={() => setTheme(t.id)}
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "6px",
            padding: "6px 8px",
            borderRadius: "var(--radius-sm)",
            background: theme === t.id ? "var(--accent-blue)" : "transparent",
            color: theme === t.id ? "#fff" : "var(--text-muted)",
            border: "none",
            cursor: "pointer",
            fontSize: "12px",
            fontWeight: 600,
            transition: "all 0.2s ease"
          }}
          title={`${t.label} Mode`}
        >
          {t.icon}
        </button>
      ))}
    </div>
  );
}
