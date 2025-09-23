"use client"

import React, { useEffect, useState } from "react";
import { apiFetch } from "../services/api";

interface FileItem {
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
        <form>
          <table className="w-full border mb-4 text-sm">
            <thead>
                <tr className="bg-gray-100 dark:bg-gray-800">
                  <th className="border px-2 py-1 bg-white text-black">Select</th>
                  <th className="border px-2 py-1 bg-white text-black">ID</th>
                  <th className="border px-2 py-1 bg-white text-black">Database</th>
                  <th className="border px-2 py-1 bg-white text-black">Download</th>
                </tr>
            </thead>
            <tbody>
              {files.map(f => (
                <tr key={f.id}>
                  <td className="border px-2 py-1 text-center">
                    <input
                      type="checkbox"
                      checked={selected.includes(f.id)}
                      onChange={e => {
                        setSelected(sel => e.target.checked ? [...sel, f.id] : sel.filter(x => x !== f.id));
                      }}
                    />
                  </td>
                  <td className="border px-2 py-1 font-mono">{f.id}</td>
                  <td className="border px-2 py-1 font-mono">{f.database}</td>
                  <td className="border px-2 py-1 text-center">
                    <button
                      className="px-2 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 cursor-pointer"
                      onClick={async e => {
                        e.preventDefault();
                        document.body.style.cursor = "wait";
                        try {
                          const token = localStorage.getItem("access_token");
                          if (!token) {
                            alert("You need to log in to download files.");
                            return;
                          }
                          // Create download link via API, passing OAuth token
                          const url = `${process.env.NEXT_PUBLIC_API_URL}/api/core/files/${f.id}/download/`;
                          const res = await fetch(url, {
                            headers: { Authorization: `Bearer ${token}` },
                          });
                          if (!res.ok) {
                            alert("Unable to download file: " + (await res.text()));
                            return;
                          }
                          const blob = await res.blob();
                          const link = document.createElement("a");
                          link.href = window.URL.createObjectURL(blob);
                          link.download = f.database + ".sqlite";
                          link.click();
                          window.URL.revokeObjectURL(link.href);
                        } finally {
                          document.body.style.cursor = "default";
                        }
                      }}
                    >Download</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </form>
      )}
      <div className="flex gap-2 mt-4">
        <button
          className={`px-4 py-2 rounded font-medium flex items-center justify-center ${selected.length === 0 || deleteLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-red-600 text-white hover:bg-red-700 cursor-pointer'}`}
          disabled={selected.length === 0 || deleteLoading}
          onClick={e => { console.log("Delete button: clicked"); e.preventDefault(); handleDelete(); }}
        >{deleteLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Delete selected</button>
        <button
          className={`px-4 py-2 rounded font-medium flex items-center justify-center ${refreshLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-gray-600 text-white hover:bg-gray-700 cursor-pointer'}`}
          disabled={refreshLoading}
          onClick={async () => {
            console.log("Refresh button: clicked");
            setRefreshLoading(true);
            document.body.style.cursor = "wait";
            try {
              console.log("Refresh button: fetchFiles");
              await fetchFiles();
            } finally {
              setRefreshLoading(false);
              document.body.style.cursor = "default";
              console.log("Refresh button: end");
            }
          }}
        >{refreshLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Refresh</button>
        <button
          className={`px-4 py-2 rounded font-medium flex items-center justify-center ${clearLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-yellow-600 text-white hover:bg-yellow-700 cursor-pointer'}`}
          disabled={clearLoading}
          onClick={async () => {
            console.log("Clear All button: clicked");
            setClearLoading(true);
            document.body.style.cursor = "wait";
            try {
              console.log("Clear All button: apiFetch");
              await apiFetch("/api/core/files/clear/", { method: "DELETE" });
              console.log("Clear All button: fetchFiles");
              await fetchFiles();
            } catch (e: any) {
              console.error("Clear All button: error", e);
              alert(e.message || JSON.stringify(e));
            } finally {
              setClearLoading(false);
              document.body.style.cursor = "default";
              console.log("Clear All button: end");
            }
          }}
        >{clearLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Clear All</button>
        <label className={`px-4 py-2 rounded font-medium text-center flex items-center justify-center ${addLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-green-600 text-white hover:bg-green-700 cursor-pointer'}`}>
          {addLoading ? (
            <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span>
          ) : null}
          <span>Add</span>
          <input
            type="file"
            multiple
            hidden
            onClick={() => console.log("Add button: clicked")}
            onChange={async (e) => {
              setAddLoading(true);
              document.body.style.cursor = "wait";
              console.log("Add button: file upload start");
              try {
                const files = e.target.files;
                if (!files || files.length === 0) {
                  console.log("Add button: no files selected");
                  return;
                }
                const formData = new FormData();
                for (let i = 0; i < files.length; ++i) formData.append("file", files[i]);
                console.log("Add button: uploading", files.length, "files");
                await apiFetch("/api/core/files/", { method: "POST", body: formData });
                console.log("Add button: fetchFiles");
                await fetchFiles();
              } catch (e: any) {
                console.error("Add button: error", e);
                alert(e.message || JSON.stringify(e));
              } finally {
                setAddLoading(false);
                document.body.style.cursor = "default";
                e.target.value = "";
                console.log("Add button: end");
              }
            }}
          />
        </label>
      </div>
    </div>
  );
};

export default ViewFilesPage;
