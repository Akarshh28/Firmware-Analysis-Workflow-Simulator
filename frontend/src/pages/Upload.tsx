"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, File as FileIcon, CheckCircle, AlertTriangle } from "lucide-react";
import { useProjectStore } from "../store/projectStore";


import { Project } from "../Types/project";

const ALLOWED_EXTS = [
  ".bin", ".img", ".zip", ".tar", ".tar.gz", ".hex",
  ".elf", ".axf", ".out", ".srec", ".mot", ".bin.gz"
];
const MAX_SIZE = 500 * 1024 * 1024; // 500MB

export const Upload: React.FC = () => {
  const { createProject, uploadFirmware, activePipeline, activeProject } = useProjectStore();
  
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadedProject, setUploadedProject] = useState<Project | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  React.useEffect(() => {
    if (!activeProject) {
      // eslint-disable-next-line
      setUploadedProject(null);
      setFile(null);
    }
  }, [activeProject]);

  const validateFile = (file: File) => {
    setError(null);
    const name = file.name.toLowerCase();
    const isValidExt = ALLOWED_EXTS.some(ext => name.endsWith(ext));
    if (!isValidExt) {
      setError(`Unsupported extension. Allowed: ${ALLOWED_EXTS.join(", ")}`);
      return false;
    }
    if (file.size > MAX_SIZE) {
      setError("File exceeds 500MB limit.");
      return false;
    }
    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      if (validateFile(selected)) {
        setFile(selected);
      }
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      // Create Project
      const project = await createProject(
        file.name,
        "Firmware Analysis run",
        "ARM Cortex-M4"
      );
      // Upload Firmware
      await uploadFirmware(project.id, file);
      
      setUploadedProject(project);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message || "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  const isReady = activePipeline?.status === "READY" || uploadedProject;

  return (
    <div className="animate-fade-in" style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <div className="page-header" style={{ marginBottom: 30 }}>
        <h1 className="page-title">Upload Firmware</h1>
        <p className="page-subtitle">Upload your firmware image to begin the automated analysis workflow.</p>
      </div>

      {!isReady ? (
        <div 
          style={{
            border: `2px dashed ${dragActive ? "var(--accent-blue)" : "var(--border-dim)"}`,
            borderRadius: "var(--radius-lg)",
            padding: "60px 20px",
            textAlign: "center",
            background: dragActive ? "rgba(99,120,255,0.05)" : "var(--bg-card)",
            transition: "all 0.2s ease"
          }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <UploadCloud size={48} color="var(--accent-blue)" style={{ margin: "0 auto", marginBottom: 20 }} />
          
          <h2 style={{ color: "var(--text-primary)", fontSize: 18, marginBottom: 8 }}>
            Drag & Drop Firmware Here
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: 14, marginBottom: 24 }}>
            Supported: .bin, .img, .zip, .tar, .tar.gz, .hex, .elf, etc. (Max 500MB)
          </p>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleChange}
            style={{ display: "none" }}
            accept={ALLOWED_EXTS.join(",")}
          />

          <button 
            className="btn btn-secondary"
            onClick={() => fileInputRef.current?.click()}
          >
            Browse Files
          </button>
        </div>
      ) : (
        <div className="card" style={{ padding: 40, textAlign: "left", border: "1px solid var(--accent-green)" }}>
          <div style={{ textAlign: "center", marginBottom: 30 }}>
            <CheckCircle size={64} color="var(--accent-green)" style={{ margin: "0 auto", marginBottom: 20 }} />
            <h2 style={{ color: "var(--text-primary)", fontSize: 24, marginBottom: 12 }}>
              Firmware Uploaded Successfully
            </h2>
            <p style={{ color: "var(--text-secondary)" }}>
              Project created and firmware validated. The analysis pipeline is ready.
            </p>
          </div>
          
          <div style={{ background: "var(--bg-secondary)", padding: 20, borderRadius: "var(--radius-md)", marginBottom: 30 }}>
            <h3 style={{ fontSize: 16, color: "var(--text-primary)", marginBottom: 16 }}>Upload Details</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: "12px 24px", fontSize: 14 }}>
                <div style={{ color: "var(--text-muted)" }}>Filename:</div>
                <div style={{ color: "var(--text-primary)", fontFamily: "var(--font-mono)" }}>{activeProject?.name || uploadedProject?.name || file?.name}</div>
                
                <div style={{ color: "var(--text-muted)" }}>Size:</div>
                <div style={{ color: "var(--text-primary)" }}>{activeProject?.file_size ? (activeProject.file_size / 1024 / 1024).toFixed(2) : (file?.size ? (file.size / 1024 / 1024).toFixed(2) : "0")} MB</div>
                
                <div style={{ color: "var(--text-muted)" }}>Upload Timestamp:</div>
                <div style={{ color: "var(--text-primary)" }}>{new Date().toLocaleString()}</div>
                
                <div style={{ color: "var(--text-muted)" }}>Architecture:</div>
                <div style={{ color: "var(--text-primary)" }}>{activeProject?.target_architecture || "ARM Cortex-M4"}</div>
                
                <div style={{ color: "var(--text-muted)" }}>Checksum (SHA256):</div>
                <div style={{ color: "var(--accent-cyan)", fontFamily: "var(--font-mono)", wordBreak: "break-all" }}>
                    {activeProject?.checksum || "Calculating..."}
                </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div style={{ marginTop: 20, padding: 16, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: "var(--radius-md)", display: "flex", gap: 10, alignItems: "center", color: "var(--accent-red)" }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {file && !isReady && (
        <div className="card" style={{ marginTop: 24, padding: 20, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <FileIcon size={24} color="var(--accent-blue)" />
            <div>
              <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>{file.name}</div>
              <div style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
          </div>
          <button 
            className="btn btn-primary"
            disabled={uploading}
            onClick={handleUpload}
          >
            {uploading ? "Uploading..." : "Upload & Create Project"}
          </button>
        </div>
      )}

    </div>
  );
};

export default Upload;
