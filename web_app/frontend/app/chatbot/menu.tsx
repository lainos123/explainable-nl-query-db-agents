// import React from "react"; // removed duplicate
import React from "react";

interface MenuProps {
  minimized: boolean;
  setMinimized: (m: boolean) => void;
  username?: string | null;
  onRequestLogout?: () => void;
}

const Menu: React.FC<MenuProps> = ({ minimized, setMinimized, username, onRequestLogout }) => {
  if (minimized) return null;
  // Remove modal logic, use tab view

  return (
    <div className="flex flex-col gap-4">
  {/* Move View Files button to bottom, open tab */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-7 h-7 rounded-full bg-violet-600 text-white grid place-items-center text-xs">
            {(username?.[0] || "?").toUpperCase()}
          </div>
          <div className="truncate">
            <div className="text-sm font-medium truncate" title={username || undefined}>{username || "User"}</div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onRequestLogout && onRequestLogout()}
            className="inline-flex items-center gap-1 rounded-full h-8 px-3 text-xs font-medium text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-sm backdrop-blur-md transition-colors"
            title="Logout"
            aria-label="Logout"
          >
            <svg className="w-3.5 h-3.5 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" y1="12" x2="9" y2="12" />
            </svg>
            <span>Logout</span>
          </button>
          <button
            onClick={() => setMinimized(true)}
            className="inline-flex items-center gap-1 rounded-full h-8 px-3 text-xs font-medium text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-sm backdrop-blur-md transition-colors"
            title="Minimize menu"
            aria-label="Minimize menu"
          >
            <svg className="w-3.5 h-3.5 text-gray-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>Hide</span>
          </button>
        </div>
      </div>
      <button
        className="w-full px-3 py-2 mt-2 rounded bg-red-600 text-white text-xs font-medium hover:bg-red-700"
        onClick={() => {
          if (typeof window !== "undefined") {
            localStorage.removeItem("chatbot_messages");
          }
          window.location.reload();
        }}
      >Clear chat session</button>

      {/* File actions */}
      <div className="flex flex-col gap-2 mt-2">
        <label className="w-full px-3 py-2 rounded bg-blue-600 text-white text-xs font-medium hover:bg-blue-700 cursor-pointer text-center">
          Upload .zip/.sqlite/.sqlite3... files
          <input type="file" multiple hidden onChange={async (e) => {
            const files = e.target.files;
            if (!files || files.length === 0) return;
            const formData = new FormData();
            for (let i = 0; i < files.length; ++i) formData.append("file", files[i]);
            const res = await fetch("/backend/core/files/", {
              method: "POST",
              body: formData,
              credentials: "include"
            });
            if (res.status === 401) {
              localStorage.clear(); sessionStorage.clear(); window.location.href = "/"; return;
            }
            window.location.reload();
          }} />
        </label>
        <button className="w-full px-3 py-2 rounded bg-gray-600 text-white text-xs font-medium hover:bg-gray-700" onClick={async () => {
          const res = await fetch("/backend/core/files/clear/", {
            method: "DELETE",
            credentials: "include"
          });
          if (res.status === 401) {
            localStorage.clear(); sessionStorage.clear(); window.location.href = "/"; return;
          }
          window.location.reload();
        }}>Clear databases</button>
      </div>

      {/* API actions */}
      <div className="flex flex-col gap-2 mt-2">
        <button className="w-full px-3 py-2 rounded bg-green-600 text-white text-xs font-medium hover:bg-green-700" onClick={async () => {
          const key = prompt("Nhập API key mới:");
          if (key !== null) {
            const res = await fetch("/backend/core/apikey/", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ key }),
              credentials: "include"
            });
            if (res.status === 401) {
              localStorage.clear(); sessionStorage.clear(); window.location.href = "/"; return;
            }
            window.location.reload();
          }
        }}>Add/Replace chatGPT API key</button>
        <button className="w-full px-3 py-2 rounded bg-gray-600 text-white text-xs font-medium hover:bg-gray-700" onClick={async () => {
          const res = await fetch("/backend/core/apikey/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ key: "" }),
            credentials: "include"
          });
          if (res.status === 401) {
            localStorage.clear(); sessionStorage.clear(); window.location.href = "/"; return;
          }
          window.location.reload();
        }}>Clear chatGPT API key</button>
      </div>
    {/* ...existing menu content... */}
    <div className="mt-8" />
    <button
      className="w-full px-3 py-2 rounded bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 mt-8"
      onClick={() => {
        window.open("/view-files", "_blank");
      }}
    >View databases</button>
  </div>
  );
};

export default Menu;

