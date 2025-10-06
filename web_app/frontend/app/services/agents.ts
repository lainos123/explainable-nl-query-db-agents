import apiFetch from "./fetch";

export async function getAgentsLast() {
  return apiFetch("/api/agents/");
}

export async function deleteAgentsCache() {
  return apiFetch("/api/agents/cache/", { method: "DELETE" });
}

export default { getAgentsLast, deleteAgentsCache };
