export const EBOT_DEFAULT_HOST = "192.168.1.100";
export const EBOT_DEFAULT_PORT = 8420;
export const EBOT_API_VERSION = "v1";

export interface EBotResponse {
  success: boolean;
  text: string;
  tokens_used?: number;
  model?: string;
  error?: string;
}

export interface EBotModel {
  name: string;
  tier: string;
  params: string;
}

export interface EBotTool {
  name: string;
  description: string;
  permission: string;
}

export interface EBotStatus {
  total_requests: number;
  total_tokens: number;
}

export interface EBotClientStats {
  requests: number;
  connected: boolean;
}

export class EBotClient {
  private host: string;
  private port: number;
  private baseUrl: string;
  private connected: boolean = false;
  private totalRequests: number = 0;

  constructor(host: string = EBOT_DEFAULT_HOST, port: number = EBOT_DEFAULT_PORT) {
    this.host = host;
    this.port = port;
    this.baseUrl = `http://${this.host}:${this.port}/${EBOT_API_VERSION}`;
  }

  // ---------------------------------------------------------------------------
  // Internal helpers
  // ---------------------------------------------------------------------------

  private async post<T>(endpoint: string, body: Record<string, unknown>): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const errorText = await res.text().catch(() => res.statusText);
      throw new Error(`EBot ${endpoint} failed (${res.status}): ${errorText}`);
    }

    this.connected = true;
    this.totalRequests++;
    return res.json() as Promise<T>;
  }

  private async get<T>(endpoint: string): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const res = await fetch(url, {
      method: "GET",
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      const errorText = await res.text().catch(() => res.statusText);
      throw new Error(`EBot ${endpoint} failed (${res.status}): ${errorText}`);
    }

    this.connected = true;
    this.totalRequests++;
    return res.json() as Promise<T>;
  }

  private errorResponse(err: unknown): EBotResponse {
    this.connected = false;
    const message = err instanceof Error ? err.message : String(err);
    return { success: false, text: "", error: message };
  }

  // ---------------------------------------------------------------------------
  // Core endpoints — matching EAI Ebot Server API
  // ---------------------------------------------------------------------------

  async chat(message: string, context?: Record<string, unknown>): Promise<EBotResponse> {
    try {
      return await this.post<EBotResponse>("/chat", { message, context });
    } catch (err) {
      return this.errorResponse(err);
    }
  }

  async complete(prompt: string): Promise<EBotResponse> {
    try {
      return await this.post<EBotResponse>("/complete", { prompt });
    } catch (err) {
      return this.errorResponse(err);
    }
  }

  async summarize(text: string): Promise<EBotResponse> {
    try {
      return await this.post<EBotResponse>("/summarize", { text });
    } catch (err) {
      return this.errorResponse(err);
    }
  }

  async taskExtract(text: string): Promise<EBotResponse> {
    try {
      return await this.post<EBotResponse>("/task-extract", { text });
    } catch (err) {
      return this.errorResponse(err);
    }
  }

  async search(query: string): Promise<EBotResponse> {
    try {
      return await this.post<EBotResponse>("/search", { query });
    } catch (err) {
      return this.errorResponse(err);
    }
  }

  // ---------------------------------------------------------------------------
  // Management endpoints
  // ---------------------------------------------------------------------------

  async getModels(): Promise<{ models: EBotModel[] }> {
    try {
      return await this.get<{ models: EBotModel[] }>("/models");
    } catch {
      this.connected = false;
      return { models: [] };
    }
  }

  async getTools(): Promise<{ tools: EBotTool[] }> {
    try {
      return await this.get<{ tools: EBotTool[] }>("/tools");
    } catch {
      this.connected = false;
      return { tools: [] };
    }
  }

  async getStatus(): Promise<EBotStatus> {
    try {
      return await this.get<EBotStatus>("/status");
    } catch {
      this.connected = false;
      return { total_requests: 0, total_tokens: 0 };
    }
  }

  async resetSession(): Promise<void> {
    try {
      await this.post("/reset", {});
    } catch {
      this.connected = false;
    }
  }

  // ---------------------------------------------------------------------------
  // Connection state
  // ---------------------------------------------------------------------------

  isConnected(): boolean {
    return this.connected;
  }

  getStats(): EBotClientStats {
    return { requests: this.totalRequests, connected: this.connected };
  }
}
