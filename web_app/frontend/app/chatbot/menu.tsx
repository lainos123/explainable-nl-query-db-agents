"use client";

import React from "react";

interface MenuProps {
  minimized: boolean;
  setMinimized: (m: boolean) => void;
  username?: string | null;
  onRequestLogout?: () => void;
}

const Menu: React.FC<MenuProps> = ({ minimized, setMinimized, username, onRequestLogout }) => {
  if (minimized) return null;

  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL}/api/core/apikeys/`;
  const getToken = () => localStorage.getItem("access_token");

  const updateApiKey = async (value: string) => {
    const token = getToken();
    if (!token) {
      alert("Unauthorized, please login again.");
      localStorage.removeItem("access_token");
      onRequestLogout?.();
      window.location.href = "/";
      return;
    }

    try {
      const res = await fetch(apiUrl, {
        method: "POST", // DRF ViewSet.create
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ key: value }),
      });

      if (res.status === 401) {
        alert("Session expired, please login again.");
        localStorage.removeItem("access_token");
        onRequestLogout?.();
        window.location.href = "/";
        return;
      }

      const result = await res.json().catch(() => ({}));
      console.log("API key update response:", result);

      if (res.ok) {
        alert(value ? "API key updated successfully." : "API key cleared successfully.");
      } else {
        alert("Failed to update API key.");
      }
    } catch (err) {
      console.error("API key update error:", err);
      alert("Network error while updating API key.");
    }
  };

  const addOrReplaceKey = async () => {
    const key = prompt("Insert new API key:");
    if (key !== null) {
      await updateApiKey(key);
    }
  };

  const clearKey = async () => {
    if (window.confirm("Are you sure you want to clear the chatGPT API key?")) {
      await updateApiKey("");
    }
  };

  return (
    <div className="flex flex-col gap-4">
      {/* User info + logout/minimize */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-7 h-7 rounded-full bg-violet-600 text-white grid place-items-center text-xs">
            {(username?.[0] || "?").toUpperCase()}
          </div>
          <div className="truncate">
            <div className="text-sm font-medium truncate" title={username || undefined}>
              {username || "User"}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              localStorage.removeItem("chatbot_messages");
              localStorage.removeItem("access_token");
              onRequestLogout?.();
            }}
            className="inline-flex items-center gap-1 rounded-full h-8 px-3 text-xs font-medium text-gray-100 bg-gray-800/70 hover:bg-gray-800/90 border border-white/10 shadow-sm backdrop-blur-md transition-colors"
            title="Logout"
            aria-label="Logout"
          >
            <svg
              className="w-3.5 h-3.5 text-gray-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
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
            <svg
              className="w-3.5 h-3.5 text-gray-300"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>Hide</span>
          </button>
        </div>
      </div>

      {/* Clear chat session */}
      <button
        className="w-full px-3 py-2 mt-2 rounded bg-red-600 text-white text-xs font-medium hover:bg-red-700"
        onClick={() => {
          if (window.confirm("Are you sure you want to clear the chat session?")) {
            localStorage.removeItem("chatbot_messages");
            window.location.reload();
          }
        }}
      >
        Clear chat session
      </button>

      {/* API actions */}
      <div className="flex flex-col gap-2 mt-2">
        <button
          className="w-full px-3 py-2 rounded bg-green-600 text-white text-xs font-medium hover:bg-green-700"
          onClick={addOrReplaceKey}
        >
          Add/Replace chatGPT API key
        </button>
        <button
          className="w-full px-3 py-2 rounded bg-gray-600 text-white text-xs font-medium hover:bg-gray-700"
          onClick={clearKey}
        >
          Clear chatGPT API key
        </button>
      </div>

      {/* Extra actions */}
      <div className="mt-8" />
      <button
        className="w-full px-3 py-2 rounded bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 mt-8"
        onClick={() => {
          window.open("/view-files", "_blank");
        }}
      >
        View/Import/Delete Databases
      </button>
    </div>
  );
};

export default Menu;
