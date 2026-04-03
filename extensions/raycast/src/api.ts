import { getPreferenceValues } from "@raycast/api";

interface Preferences {
  backendUrl: string;
}

function getBaseUrl(): string {
  const { backendUrl } = getPreferenceValues<Preferences>();
  return backendUrl.replace(/\/+$/, "");
}

export interface EDoc {
  id: string;
  title: string;
  content: string;
  updatedAt: string;
  createdAt: string;
  tags?: string[];
}

export interface ENote {
  id: string;
  title: string;
  content: string;
  createdAt: string;
}

export interface EBotResponse {
  response: string;
  message?: string;
}

export interface RecentFile {
  id: string;
  name: string;
  app: string;
  path: string;
  updatedAt: string;
  type: string;
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${getBaseUrl()}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    throw new Error(`eOffice API error: ${response.status} ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function searchDocs(query: string): Promise<EDoc[]> {
  return apiFetch<EDoc[]>(`/api/edocs/search?q=${encodeURIComponent(query)}`);
}

export async function createNote(title: string, content: string): Promise<ENote> {
  return apiFetch<ENote>("/api/enotes", {
    method: "POST",
    body: JSON.stringify({ title, content }),
  });
}

export async function askEBot(prompt: string): Promise<string> {
  const data = await apiFetch<EBotResponse>("/api/ebot", {
    method: "POST",
    body: JSON.stringify({ prompt, source: "raycast" }),
  });
  return data.response || data.message || "No response from eBot.";
}

export async function getRecentFiles(): Promise<RecentFile[]> {
  return apiFetch<RecentFile[]>("/api/files/recent");
}

export async function healthCheck(): Promise<boolean> {
  try {
    await apiFetch<{ status: string }>("/api/health");
    return true;
  } catch {
    return false;
  }
}
