"use client"

import React, { useState, useEffect } from "react";
import { useRouter } from 'next/navigation';
import { apiFetch } from "../services/api";
import { performLogout } from "../services/logout";

export default function SettingsPage() {
  const [apiKey, setApiKey] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [deleting, setDeleting] = useState(false);
  const router = useRouter();

  // Load current API key
  useEffect(() => {
    const loadApiKey = async () => {
      setLoading(true);
      try {
        const data = await apiFetch("/api/core/apikeys/");
        if (typeof data === "undefined") return; // apiFetch handled logout/redirect
        
        if (data && data.api_key) {
          // Show masked version of the API key
          const maskedKey = data.api_key.substring(0, 8) + "..." + data.api_key.substring(data.api_key.length - 4);
          setApiKey(maskedKey);
        }
      } catch (e: any) {
        console.error("Error loading API key:", e);
        setError("Failed to load API key");
      } finally {
        setLoading(false);
      }
    };

    loadApiKey();
  }, []);

  const handleSave = async () => {
    if (!apiKey || apiKey.length < 20) {
      setError("Please enter a valid OpenAI API key");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await apiFetch("/api/core/apikeys/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey }),
      });
      
      setMessage("API key saved successfully!");
      setApiKey(apiKey.substring(0, 8) + "..." + apiKey.substring(apiKey.length - 4));
    } catch (e: any) {
      console.error("Error saving API key:", e);
      setError("Failed to save API key");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Delete your saved API key? This cannot be undone.")) return;
    setDeleting(true);
    setError("");
    setMessage("");
    try {
      // Backend lacks DELETE; send empty key via POST to clear
      await apiFetch("/api/core/apikeys/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: "" })
      });
      setApiKey("");
      try { localStorage.removeItem("has_api_key"); } catch {}
      setMessage("API key deleted.");
    } catch (e: any) {
      console.error("Error deleting API key:", e);
      setError("Failed to delete API key");
    } finally {
      setDeleting(false);
    }
  };

  const handleLogout = async () => {
    await performLogout();
    router.push("/");
  };

  return (
    <div className="fixed inset-0 z-50 bg-gray-900 text-gray-100 p-4 overflow-auto">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <button
              className="inline-flex items-center gap-2 px-3 py-1 rounded bg-gray-800 text-white text-sm"
              onClick={() => router.back()}
            >
              ← Back
            </button>
            <h1 className="text-xl font-semibold ml-2">Settings</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">OpenAI API Key</h2>
          <p className="text-gray-400 mb-4">
            Your OpenAI API key is used to power the AI agents. Each user needs their own API key.
            You can get one from <a href="https://platform.openai.com/account/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 underline">OpenAI's website</a>.
          </p>

          {loading ? (
            <div className="text-gray-400">Loading...</div>
          ) : (
            <div className="space-y-4">
              <div>
                <label htmlFor="apiKey" className="block text-sm font-medium mb-2">
                  API Key
                </label>
                <input
                  id="apiKey"
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleSave}
                  disabled={saving || !apiKey}
                  className={`px-4 py-2 rounded font-medium ${
                    saving || !apiKey
                      ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {saving ? "Saving..." : "Save API Key"}
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className={`px-4 py-2 rounded font-medium ${
                    deleting
                      ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                      : 'bg-red-600 text-white hover:bg-red-700'
                  }`}
                >
                  {deleting ? "Deleting..." : "Delete API Key"}
                </button>
              </div>

              {message && (
                <div className="p-3 bg-green-900 border border-green-700 rounded text-green-200">
                  {message}
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-900 border border-red-700 rounded text-red-200">
                  {error}
                </div>
              )}
            </div>
          )}

          <div className="mt-6 p-4 bg-gray-700 rounded">
            <h3 className="font-semibold mb-2">How it works:</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>• Your API key is stored securely and only used for your queries</li>
              <li>• The AI agents use your key to generate SQL queries</li>
              <li>• You can update your API key anytime</li>
              <li>• Without an API key, the chatbot won't work</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
