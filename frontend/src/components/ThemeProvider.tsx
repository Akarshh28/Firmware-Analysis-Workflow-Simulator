"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import React from "react";

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider defaultTheme="dark" attribute="data-theme" enableSystem={false}>
      {children}
    </NextThemesProvider>
  );
}
