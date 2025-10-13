import React from "react";
import { FileItem } from "./page";

export interface file_actions_props {
  selected: number[];
  deleteLoading: boolean;
  refreshLoading: boolean;
  clearLoading: boolean;
  addLoading: boolean;
  handleDelete: () => void;
  fetchFiles: () => Promise<void>;
  setRefreshLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setClearLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setAddLoading: React.Dispatch<React.SetStateAction<boolean>>;
  apiFetch: typeof import("../services/api").apiFetch;
  files: import("./page").FileItem[];
  setSelected: React.Dispatch<React.SetStateAction<number[]>>;
  setSpiderLoading: React.Dispatch<React.SetStateAction<boolean>>;
  spiderLoading: boolean;
}

const FileActions: React.FC<file_actions_props> = ({
  selected,
  deleteLoading,
  refreshLoading,
  clearLoading,
  addLoading,
  handleDelete,
  fetchFiles,
  setRefreshLoading,
  setClearLoading,
  setAddLoading,
  apiFetch,
  files,
  setSelected,
  setSpiderLoading,
  spiderLoading,
}) => {
  const allSelected = files.length > 0 && selected.length === files.length;
  
  const handleSelectAll = () => {
    if (allSelected) {
      setSelected([]);
    } else {
      setSelected(files.map(f => f.id));
    }
  };

  return (
  <div className="flex gap-2 mt-4 mb-8">
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
            e.target.value = "";
            console.log("Add button: end");
          }
        }}
        title="Upload database files"
      />
    </label>
    <button
      className={`px-4 py-2 rounded font-medium flex items-center justify-center ${refreshLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-gray-600 text-white hover:bg-gray-700 cursor-pointer'}`}
      disabled={refreshLoading}
      onClick={async () => {
        console.log("Refresh button: clicked");
        setRefreshLoading(true);
        try {
          console.log("Refresh button: fetchFiles");
          await fetchFiles();
        } finally {
          setRefreshLoading(false);
          console.log("Refresh button: end");
        }
      }}
    >{refreshLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Refresh</button>
    <button
      className={`px-4 py-2 rounded font-medium flex items-center justify-center ${clearLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-yellow-600 text-white hover:bg-yellow-700 cursor-pointer'}`}
      disabled={clearLoading}
      onClick={async () => {
        console.log("Clear All button: clicked");
        // Ask for confirmation before clearing all
        if (typeof window !== 'undefined') {
          const ok = window.confirm("Are you sure you want to clear all files? This action cannot be undone.");
          if (!ok) {
            console.log("Clear All button: cancelled by user");
            return;
          }
        }
        setClearLoading(true);
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
          console.log("Clear All button: end");
        }
      }}
    >{clearLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Clear All</button>
    <button
      className={`px-4 py-2 rounded font-medium flex items-center justify-center ${selected.length === 0 || deleteLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-red-600 text-white hover:bg-red-700 cursor-pointer'}`}
      disabled={selected.length === 0 || deleteLoading}
      onClick={e => { console.log("Delete button: clicked"); e.preventDefault(); handleDelete(); }}
    >{deleteLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Delete selected</button>
    <button
      className={`px-4 py-2 rounded font-medium flex items-center justify-center ${files.length === 0 ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'}`}
      disabled={files.length === 0}
      onClick={handleSelectAll}
      title={allSelected ? "Deselect all files" : "Select all files"}
    >{allSelected ? "Deselect All" : "Select All"}</button>
    <button
      className={`px-4 py-2 rounded font-medium flex items-center justify-center ${spiderLoading ? 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-60' : 'bg-purple-600 text-white hover:bg-purple-700 cursor-pointer'}`}
      disabled={spiderLoading}
      onClick={async () => {
        console.log("Add All Spider button: clicked");
        if (typeof window !== 'undefined') {
          const ok = window.confirm("This will upload all Spider databases from /data/spider_data/test_database. This may take a few minutes. Continue?");
          if (!ok) {
            console.log("Add All Spider button: cancelled by user");
            return;
          }
        }
        setSpiderLoading(true);
        try {
          console.log("Add All Spider button: apiFetch");
          await apiFetch("/api/core/files/add_spider_databases/", { method: "POST" });
          console.log("Add All Spider button: fetchFiles");
          await fetchFiles();
        } catch (e: any) {
          console.error("Add All Spider button: error", e);
          alert(e.message || JSON.stringify(e));
        } finally {
          setSpiderLoading(false);
          console.log("Add All Spider button: end");
        }
      }}
      title="Upload all Spider test databases from /data/spider_data/test_database"
    >{spiderLoading ? <span className="animate-spin mr-2 w-4 h-4 border-2 border-t-2 border-white rounded-full"></span> : null}Add All Spider</button>
  </div>
  );
};

export default FileActions;
