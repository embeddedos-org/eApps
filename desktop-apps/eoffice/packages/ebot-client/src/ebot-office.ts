import { EBotClient, EBotResponse } from "./ebot-client";

export interface GrammarResult {
  suggestions: string[];
  corrected: string;
}

export interface SlideContent {
  title: string;
  bullets: string[];
}

export interface ExtractedTask {
  task: string;
  priority: "high" | "medium" | "low";
  due?: string;
}

export interface SearchResult {
  title: string;
  snippet: string;
  app: string;
  score: number;
}

export class EBotOffice {
  private client: EBotClient;

  constructor(client: EBotClient) {
    this.client = client;
  }

  // ---------------------------------------------------------------------------
  // Internal helpers
  // ---------------------------------------------------------------------------

  private extractText(res: EBotResponse): string {
    if (!res.success || !res.text) {
      throw new Error(res.error ?? "Empty response from EBot");
    }
    return res.text;
  }

  private parseJson<T>(raw: string, fallback: T): T {
    try {
      const trimmed = raw.trim();
      const braceIdx = trimmed.indexOf("{");
      const bracketIdx = trimmed.indexOf("[");

      if (braceIdx === -1 && bracketIdx === -1) return fallback;

      let jsonStart: number;
      let jsonEnd: number;

      if (bracketIdx !== -1 && (braceIdx === -1 || bracketIdx < braceIdx)) {
        jsonStart = bracketIdx;
        jsonEnd = trimmed.lastIndexOf("]") + 1;
      } else {
        jsonStart = braceIdx;
        jsonEnd = trimmed.lastIndexOf("}") + 1;
      }

      if (jsonEnd <= jsonStart) return fallback;
      return JSON.parse(trimmed.slice(jsonStart, jsonEnd)) as T;
    } catch {
      return fallback;
    }
  }

  // ---------------------------------------------------------------------------
  // Text AI — eDocs
  // ---------------------------------------------------------------------------

  async summarizeText(text: string): Promise<string> {
    const res = await this.client.summarize(text);
    return this.extractText(res);
  }

  async rewriteText(text: string, tone: "formal" | "casual" | "concise" = "formal"): Promise<string> {
    const prompt =
      `Rewrite the following text in a ${tone} tone. ` +
      `Return only the rewritten text, no commentary.\n\n${text}`;
    const res = await this.client.complete(prompt);
    return this.extractText(res);
  }

  async grammarCheck(text: string): Promise<GrammarResult> {
    const prompt =
      `Check the following text for grammar and spelling errors. ` +
      `Respond in JSON with keys "suggestions" (array of strings describing each issue) ` +
      `and "corrected" (the full corrected text).\n\n${text}`;
    const res = await this.client.complete(prompt);
    const raw = this.extractText(res);
    return this.parseJson<GrammarResult>(raw, { suggestions: [], corrected: text });
  }

  async translateText(text: string, targetLang: string): Promise<string> {
    const prompt =
      `Translate the following text to ${targetLang}. ` +
      `Return only the translation, no commentary.\n\n${text}`;
    const res = await this.client.complete(prompt);
    return this.extractText(res);
  }

  // ---------------------------------------------------------------------------
  // Spreadsheet AI — eSheets
  // ---------------------------------------------------------------------------

  async suggestFormula(description: string, cellContext?: string): Promise<string> {
    let prompt = `Suggest a spreadsheet formula for: ${description}.`;
    if (cellContext) {
      prompt += ` The surrounding cell context is: ${cellContext}.`;
    }
    prompt += " Return only the formula, no explanation.";
    const res = await this.client.complete(prompt);
    return this.extractText(res).trim();
  }

  async explainFormula(formula: string): Promise<string> {
    const prompt =
      `Explain the following spreadsheet formula in plain English, step by step:\n${formula}`;
    const res = await this.client.complete(prompt);
    return this.extractText(res);
  }

  // ---------------------------------------------------------------------------
  // Slides AI — eSlides
  // ---------------------------------------------------------------------------

  async generateSlideContent(
    topic: string,
    slideCount: number = 5,
  ): Promise<SlideContent[]> {
    const prompt =
      `Generate exactly ${slideCount} presentation slides about "${topic}". ` +
      `Respond in JSON as an array of objects, each with "title" (string) and "bullets" (array of strings, 3-5 per slide). ` +
      `Return only the JSON array.`;
    const res = await this.client.complete(prompt);
    const raw = this.extractText(res);
    return this.parseJson<SlideContent[]>(raw, [
      { title: topic, bullets: ["Content generation unavailable"] },
    ]);
  }

  async generateTalkingPoints(slideContent: string): Promise<string[]> {
    const prompt =
      `Generate concise speaker talking points for the following slide content. ` +
      `Respond as a JSON array of strings.\n\n${slideContent}`;
    const res = await this.client.complete(prompt);
    const raw = this.extractText(res);
    return this.parseJson<string[]>(raw, []);
  }

  // ---------------------------------------------------------------------------
  // Notes AI — eNotes
  // ---------------------------------------------------------------------------

  async autoTagNote(content: string): Promise<string[]> {
    const prompt =
      `Analyze the following note and suggest relevant tags. ` +
      `Respond as a JSON array of short tag strings (lowercase, no #).\n\n${content}`;
    const res = await this.client.complete(prompt);
    const raw = this.extractText(res);
    return this.parseJson<string[]>(raw, []);
  }

  async linkRelatedNotes(noteContent: string, allNoteTitles: string[]): Promise<string[]> {
    const prompt =
      `Given this note content:\n${noteContent}\n\n` +
      `And this list of existing note titles:\n${allNoteTitles.join("\n")}\n\n` +
      `Which existing notes are most related? ` +
      `Respond as a JSON array of the related note title strings (max 5).`;
    const res = await this.client.complete(prompt);
    const raw = this.extractText(res);
    const related = this.parseJson<string[]>(raw, []);
    return related.filter((t) => allNoteTitles.includes(t));
  }

  // ---------------------------------------------------------------------------
  // Tasks AI — eMail, ePlanner
  // ---------------------------------------------------------------------------

  async extractTasks(text: string): Promise<ExtractedTask[]> {
    const res = await this.client.taskExtract(text);
    const raw = this.extractText(res);
    return this.parseJson<ExtractedTask[]>(raw, []);
  }

  // ---------------------------------------------------------------------------
  // Search — cross-app
  // ---------------------------------------------------------------------------

  async semanticSearch(query: string): Promise<SearchResult[]> {
    const res = await this.client.search(query);
    const raw = this.extractText(res);
    return this.parseJson<SearchResult[]>(raw, []);
  }
}
