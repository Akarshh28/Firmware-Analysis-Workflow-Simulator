"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { UploadCloud, File as FileIcon, CheckCircle, AlertTriangle, X, Play, RefreshCw, Hash, HardDrive } from "lucide-react";
import { useProjectStore } from "../store/projectStore";
import toast from "react-hot-toast";

const ALLOWED_EXTS = [
  ".bin", ".img", ".zip", ".tar", ".tar.gz", ".hex",
  ".elf", ".axf", ".out", ".srec", ".mot", ".bin.gz", ".7z"
];
const MAX_SIZE = 500 * 1024 * 1024; // 500MB

export const Upload: React.FC = () => {
  const { createProject, uploadFirmware, activeProject, activePipeline, startPipeline } = useProjectStore();
  
  const [file, setFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!activeProject) {
      setFile(null);
      setProgress(0);
      setError(null);
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

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const handleCancel = () => {
    setFile(null);
    setProgress(0);
    setError(null);
    if (fileInputRef.current) {
        fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async () => {
    if (!file) return;

    try {
      setUploading(true);
      setError(null);
      
      let projId = activeProject?.id;
      if (!projId) {
        const newProj = await createProject(
          file.name,
          "Auto-created from upload",
          "Unknown"
        );
        projId = newProj.id;
      }

      await uploadFirmware(projId, file, (p) => {
        setProgress(p);
      });
      
      toast.success("Firmware uploaded successfully!");
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || "Failed to upload firmware.");
    } finally {
      setUploading(false);
    }
  };

  const handleRunPipeline = async () => {
    if (!activeProject?.id) return;
    try {
      await startPipeline(activeProject.id);
      toast.success("Pipeline started!");
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Failed to start pipeline");
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const isUploaded = activeProject?.firmware_filepath != null;
  const isRunning = activePipeline?.status === "RUNNING";

  return (
    <div className="view-container">
      <h2 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '8px' }}>
        Firmware Ingestion
      </h2>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
        Upload a firmware image to begin the analysis pipeline. Maximum file size is 500MB.
      </p>

      {/* Upload Zone */}
      {!isUploaded && (
        <div style={{ maxWidth: '600px', margin: '0 auto' }}>
          <div 
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${dragActive ? 'var(--accent-cyan)' : 'var(--border-dim)'}`,
              borderRadius: '12px',
              padding: '48px',
              textAlign: 'center',
              backgroundColor: dragActive ? 'rgba(34,211,238,0.05)' : 'var(--bg-secondary)',
              cursor: uploading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease',
              position: 'relative',
              overflow: 'hidden'
            }}
            onClick={() => !uploading && !file && fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleChange} 
              style={{ display: 'none' }} 
              disabled={uploading}
              accept={ALLOWED_EXTS.join(',')}
            />

            {!file ? (
              <div style={{ pointerEvents: 'none' }}>
                <div style={{
                  width: '64px', height: '64px', borderRadius: '50%', background: 'var(--bg-tertiary)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
                  color: 'var(--accent-cyan)'
                }}>
                  <UploadCloud size={32} />
                </div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                  Drag & Drop Firmware File
                </h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                  or click to browse from your computer
                </p>
                <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'center', gap: '8px', flexWrap: 'wrap' }}>
                  {ALLOWED_EXTS.map(ext => (
                    <span key={ext} style={{ fontSize: '11px', background: 'var(--bg-tertiary)', padding: '2px 8px', borderRadius: '4px', color: 'var(--text-muted)' }}>
                      {ext}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'left', background: 'var(--bg-primary)', padding: '20px', borderRadius: '8px', border: '1px solid var(--border-dim)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ padding: '12px', background: 'rgba(34,211,238,0.1)', color: 'var(--accent-cyan)', borderRadius: '8px' }}>
                      <FileIcon size={24} />
                    </div>
                    <div>
                      <h4 style={{ color: 'var(--text-primary)', fontWeight: 600, margin: 0 }}>{file.name}</h4>
                      <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>{formatSize(file.size)}</span>
                    </div>
                  </div>
                  {!uploading && (
                    <button onClick={(e) => { e.stopPropagation(); handleCancel(); }} className="btn btn-icon" style={{ background: 'none' }}>
                      <X size={18} />
                    </button>
                  )}
                </div>

                {uploading ? (
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                      <span>Uploading...</span>
                      <span>{progress}%</span>
                    </div>
                    <div style={{ height: '6px', background: 'var(--bg-tertiary)', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ height: '100%', width: `${progress}%`, background: 'var(--accent-cyan)', transition: 'width 0.2s ease' }} />
                    </div>
                  </div>
                ) : (
                  <button 
                    onClick={(e) => { e.stopPropagation(); handleSubmit(); }}
                    className="btn btn-primary" 
                    style={{ width: '100%', display: 'flex', justifyContent: 'center', gap: '8px' }}
                  >
                    <UploadCloud size={16} /> Begin Upload
                  </button>
                )}
              </div>
            )}
          </div>
          {error && (
            <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--accent-red)' }}>
              <AlertTriangle size={18} />
              <span style={{ fontSize: '14px' }}>{error}</span>
            </div>
          )}
        </div>
      )}

      {/* Uploaded State */}
      {isUploaded && activeProject && (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <div style={{ 
            background: 'var(--bg-secondary)', border: '1px solid var(--accent-cyan)', borderRadius: '12px', 
            padding: '24px', position: 'relative', overflow: 'hidden' 
          }}>
            <div style={{ position: 'absolute', top: 0, left: 0, width: '4px', height: '100%', background: 'var(--accent-cyan)' }} />
            
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'rgba(34,211,238,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent-cyan)' }}>
                  <CheckCircle size={24} />
                </div>
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--text-primary)', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                    Firmware Ready <span style={{ padding: '2px 8px', background: 'var(--accent-green)', color: '#000', fontSize: '11px', borderRadius: '12px', fontWeight: 800 }}>VALIDATED</span>
                  </h3>
                  <p style={{ color: 'var(--text-secondary)', margin: '4px 0 0 0', fontSize: '14px' }}>
                    File successfully uploaded and validated.
                  </p>
                </div>
              </div>

              {!isRunning ? (
                <button onClick={handleRunPipeline} className="btn btn-primary" style={{ padding: '12px 24px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px' }}>
                  <Play size={18} /> Run Pipeline
                </button>
              ) : (
                <button disabled className="btn btn-secondary" style={{ padding: '12px 24px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px', opacity: 0.7 }}>
                  <RefreshCw size={18} className="animate-spin" /> Pipeline Running
                </button>
              )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', borderTop: '1px solid var(--bg-tertiary)', paddingTop: '24px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <FileIcon size={12} /> Filename
                </div>
                <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '14px', wordBreak: 'break-all' }}>
                  {activeProject.firmware_filepath?.split('/').pop() || activeProject.firmware_filepath?.split('\\').pop() || 'Unknown'}
                </div>
              </div>
              
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <HardDrive size={12} /> Size
                </div>
                <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '14px' }}>
                  {activeProject.file_size ? formatSize(activeProject.file_size) : 'Unknown'}
                </div>
              </div>

              <div style={{ gridColumn: '1 / -1' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)', fontSize: '12px', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <Hash size={12} /> SHA256 Checksum
                </div>
                <div style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontSize: '13px', padding: '12px', background: '#0a0a0a', borderRadius: '6px', wordBreak: 'break-all', border: '1px solid #222' }}>
                  {activeProject.checksum || 'Pending calculation...'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload;
