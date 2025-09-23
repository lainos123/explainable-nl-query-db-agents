"use client"

import React, { useEffect, useState } from "react";
import { apiFetch } from "../services/api";
import FileTable from "./file_table";
import FileActions from "./file_actions";
// Helper to download file with correct extension
function downloadFile(f: FileItem) {
  return async (e: React.MouseEvent) => {
    e.preventDefault();
    document.body.style.cursor = "wait";
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        alert("You need to log in to download files.");
        return;
      }
      const url = `${process.env.NEXT_PUBLIC_API_URL}/api/core/files/${f.id}/download/`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        alert("Unable to download file: " + (await res.text()));
        return;
      }
      const blob = await res.blob();
      // Preserve original extension (.sqlite, .sqlite3, .sqlite6, etc.)
      const fileUrl = f.file || "";
      const extMatch = fileUrl.match(/\.(sqlite\d*|db)$/i);
      const ext = extMatch ? extMatch[0] : ".sqlite";
      const link = document.createElement("a");
      link.href = window.URL.createObjectURL(blob);
      link.download = `${f.database}${ext}`;
      link.click();
      window.URL.revokeObjectURL(link.href);
    } finally {
      document.body.style.cursor = "default";
    }
  };
}

export interface FileItem {
  id: number;
  database: string;
  file: string;
}

const ViewFilesPage: React.FC = () => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [refreshLoading, setRefreshLoading] = useState(false);
  const [clearLoading, setClearLoading] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    console.log("fetchFiles: start");
    try {
      const data = await apiFetch("/api/core/files/");
      console.log("fetchFiles: success", data);
  setFiles(Array.isArray(data) ? data.sort((a, b) => b.id - a.id) : []);
  setSelected([]); // Clear selection whenever files are refreshed
    } catch (e: any) {
      console.error("fetchFiles: error", e);
      const msg = e.message || JSON.stringify(e);
      if (
        msg.includes("401") ||
        msg.includes("token_not_valid") ||
        msg.includes("Token is expired")
      ) {
        localStorage.clear(); sessionStorage.clear();
        if (window.confirm("Your login session has expired. Please log in again")) {
          window.location.href = "/";
        }
        return;
      }
      alert(msg);
    } finally {
      setLoading(false);
      console.log("fetchFiles: end");
    }
  };

  useEffect(() => {
  console.log("useEffect: fetchFiles");
  fetchFiles();
  }, []);

  const handleDelete = async () => {
    setDeleteLoading(true);
    document.body.style.cursor = "wait";
    console.log("Delete button: start", selected);
    try {
      for (const id of selected) {
        try {
          console.log("Delete button: deleting", id);
          await apiFetch(`/api/core/files/${id}/`, { method: "DELETE" });
          console.log("Delete button: deleted", id);
        } catch (e: any) {
          console.error("Delete button: error", id, e);
          const msg = e.message || JSON.stringify(e);
          if (
            msg.includes("401") ||
            msg.includes("token_not_valid") ||
            msg.includes("Token is expired")
          ) {
            localStorage.clear(); sessionStorage.clear(); window.location.href = "/"; return;
          }
          alert(msg);
          return;
        }
      }
      setSelected([]);
      console.log("Delete button: fetchFiles");
      await fetchFiles();
    } finally {
      setDeleteLoading(false);
      document.body.style.cursor = "default";
      console.log("Delete button: end");
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-bold mb-6">Database Files</h1>
      {loading && <div className="mb-4 text-gray-500">Loading...</div>}
  {/* error popup only, no HTML error rendering */}
      {files.length === 0 ? (
        <div className="text-gray-400">No databases found.</div>
      ) : (
        <FileTable
          files={files}
          selected={selected}
          setSelected={setSelected}
          downloadFile={downloadFile}
        />
      )}
      <FileActions
        selected={selected}
        deleteLoading={deleteLoading}
        refreshLoading={refreshLoading}
        clearLoading={clearLoading}
        addLoading={addLoading}
        handleDelete={handleDelete}
        fetchFiles={fetchFiles}
        setRefreshLoading={setRefreshLoading}
        setClearLoading={setClearLoading}
        setAddLoading={setAddLoading}
        apiFetch={apiFetch}
      />
    </div>
  );
};

export default ViewFilesPage;
