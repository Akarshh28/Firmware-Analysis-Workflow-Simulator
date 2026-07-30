"use client";

import React from "react";
import { usePipelineStore } from "../store/pipelineStore";
import { useProjectStore } from "../store/projectStore";

const getColor = (status: string) => {
  switch (status) {
    case "completed":
      return "#22c55e";
    case "running":
      return "#facc15";
    case "failed":
      return "#ef4444";
    case "queued":
      return "#3b82f6";
    default:
      return "#6b7280";
  }
};

export const PipelineViewer: React.FC = () => {
  const {
    pipeline,
    runPipeline,
    resetPipeline,
  } = usePipelineStore();
  const { activeProject } = useProjectStore();

  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);

  return (
    <div style={{ padding: 24 }}>

      <h2 style={{ color: "white", marginBottom: 20 }}>
        Firmware Analysis Pipeline
      </h2>

      {/* Firmware Upload */}
      <div
        style={{
          marginBottom: 24,
          padding: 20,
          border: "1px solid #333",
          borderRadius: 10,
          background: "#111827",
        }}
      >
        <h3 style={{ color: "white", marginBottom: 15 }}>
          Firmware Upload
        </h3>

        <input
          type="file"
          accept=".bin,.hex,.elf,.img"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) setSelectedFile(file);
          }}
        />

        {selectedFile && (
          <p
            style={{
              marginTop: 12,
              color: "#22c55e",
            }}
          >
            ✅ Selected Firmware : <b>{selectedFile.name}</b>
          </p>
        )}
      </div>

      {/* Buttons */}
      <div style={{ display: "flex", gap: 12, marginBottom: 30 }}>

        <button
          disabled={!selectedFile}
          onClick={() => {
            if (!selectedFile) {
              alert("Please upload firmware first.");
              return;
            }
            if (!activeProject) return;

            runPipeline(activeProject.id);
          }}
          style={{
            padding: "10px 20px",
            background: "#0891b2",
            color: "white",
            border: "none",
            borderRadius: 8,
            opacity: selectedFile ? 1 : 0.5,
            cursor: selectedFile ? "pointer" : "not-allowed",
          }}
        >
          ▶ Run Pipeline
        </button>

        <button
          onClick={() => {
            setSelectedFile(null);
            resetPipeline();
          }}
          style={{
            padding: "10px 20px",
            background: "#374151",
            color: "white",
            border: "none",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          Reset
        </button>

      </div>

      {pipeline.nodes.map((node) => (

        <div
          key={node.id}
          style={{
            border: "1px solid #333",
            padding: 16,
            borderRadius: 10,
            marginBottom: 18,
            background: "#111827",
          }}
        >

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
            }}
          >

            <h3 style={{ color: "white" }}>
              {node.toolName.toUpperCase()}
            </h3>

            <span
              style={{
                color: getColor(node.status),
                fontWeight: "bold",
              }}
            >
              {node.status.toUpperCase()}
            </span>

          </div>

          <div
            style={{
              marginTop: 12,
              height: 10,
              background: "#333",
              borderRadius: 20,
            }}
          >
            <div
              style={{
                width: `${node.progress}%`,
                background: getColor(node.status),
                height: "100%",
                borderRadius: 20,
                transition: "0.2s",
              }}
            />
          </div>

          <p
            style={{
              color: "#aaa",
              marginTop: 8,
            }}
          >
            {node.progress}%
          </p>

        </div>

      ))}

    </div>
  );
};

export default PipelineViewer;