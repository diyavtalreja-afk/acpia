// Small API helpers — all relative URLs (same origin in production).

async function j(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.json();
}

export const api = {
  case: () => j("GET", "/api/case"),
  flags: (params = "") => j("GET", `/api/flags${params}`),
  file: (id) => j("GET", `/api/files/${id}`),
  query: (question) => j("POST", "/api/query", { question }),
  timeline: () => j("GET", "/api/timeline"),
  graph: (focus) => j("GET", `/api/graph${focus ? `?focus=${encodeURIComponent(focus)}` : ""}`),
  decide: (flagId, decision) => j("POST", `/api/flags/${flagId}/decision`, { decision }),
  scan: (path) => j("POST", "/api/scan", { path }),
  newCase: () => j("POST", "/api/case/new"),
  chats: () => j("GET", "/api/chats"),
  chatMessages: (convId) => j("GET", `/api/chats/${convId}/messages`),
};

export function fmtTs(iso) {
  try {
    return new Date(iso).toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function sevColor(sev) {
  return sev === "high" ? "text-danger" : sev === "medium" ? "text-warn" : "text-ok";
}
