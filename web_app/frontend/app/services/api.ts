// Backward-compatible façade: re-export split service modules
export { default as apiFetch } from "./fetch";
export { default as defaultFetch } from "./fetch"; // compatibility alias
export { default as streamAgents } from "./sse";
export { getAgentsLast, deleteAgentsCache } from "./agents";
export { tryRefresh, getAccessToken, getRefreshToken } from "./auth";
