import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FAWS — Firmware Analysis Workflow Simulator",
  description:
    "Digital twin of the complete firmware analysis pipeline for DLMS/COSEM Smart Meter security research at C3iHub, IIT Kanpur.",
  keywords: ["firmware analysis", "DLMS", "COSEM", "smart meter", "cybersecurity", "IIT Kanpur", "C3iHub"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
