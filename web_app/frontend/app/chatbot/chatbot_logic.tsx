"use client"

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { performLogout } from "../services/logout";
import { useStreamingLogic } from "./streaming_logic";
import { useResendDeleteEdit } from "./resend_delete_edit";
import { apiFetch } from "../services/api";
import { InsertBoxHandle } from "./insert_box";

export function useChatbotLogic() {
  const router = useRouter();
  const [menuMinimized, setMenuMinimized] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [loadingBot, setLoadingBot] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [logoutLoading, setLogoutLoading] = useState(false);

  // restore messages from localStorage
  useEffect(() => {
    try {
      const cache = localStorage.getItem("chatbot_messages");
      if (cache) setMessages(JSON.parse(cache));
    } catch {}
  }, []);

  // auth guard
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const u = localStorage.getItem("username");
    if (!token) {
      router.replace("/");
    } else {
      setUsername(u);
    }
  }, [router]);

  // fetch chats + usage on mount
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const token = localStorage.getItem("access_token");
        // Always prefer local cache first. If local exists, send it to API in background to sync.
        let localRaw = null;
        try { localRaw = localStorage.getItem("chatbot_messages"); } catch {}
        const localMsgs = localRaw ? JSON.parse(localRaw) : [];

        if (token) {
          try {
            if (Array.isArray(localMsgs) && localMsgs.length > 0) {
              // Sync local to server (one-time). Do not overwrite client state with server copy.
              try {
                await apiFetch("/api/core/chats/", { method: "POST", body: JSON.stringify({ messages: localMsgs }) });
              } catch (e) {
                // ignore sync failures
              }
            } else {
              // No local messages: attempt to load from server and seed local cache
              try {
                const data = await apiFetch("/api/core/chats/");
                if (mounted && data?.messages) {
                  setMessages(data.messages);
                  try { localStorage.setItem("chatbot_messages", JSON.stringify(data.messages)); } catch {}
                }
              } catch (e) {
                // ignore fetch errors
              }
            }

            // Refresh usage info after sync/load
            try {
              const udata = await apiFetch("/api/core/usage/");
              if (udata) {
                try { localStorage.setItem("usage_cache", JSON.stringify(udata)); } catch {}
                try { window.dispatchEvent(new CustomEvent("usage_updated", { detail: udata })); } catch {}
              }
            } catch (e) {
              // ignore
            }
          } catch (e) {
            // ignore overall errors
          }
        } else {
          // No token: only keep local cache; do not contact API
        }
      } catch (e) {
        // ignore unexpected errors
      }
    })();
    return () => { mounted = false };
  }, []);

  // hooks for chat actions
  const { sendUserMessage } = useStreamingLogic(setMessages, setLoadingBot);
  const { editMessage, deleteMessage, resendUserMessage } = useResendDeleteEdit(messages, setMessages, setLoadingBot);

  // ref to InsertBox
  const insertRef = useRef<InsertBoxHandle | null>(null);

  // logout handler
  const handleLogout = async () => {
    setLogoutLoading(true);
    try { performLogout("/"); }
    finally { setLogoutLoading(false); }
  };

  return {
    messages, setMessages,
    loadingBot, username,
    menuMinimized, setMenuMinimized,
    showLogoutConfirm, setShowLogoutConfirm,
    logoutLoading, handleLogout,
    editMessage, deleteMessage, resendUserMessage,
    sendUserMessage, insertRef,
  };
}
