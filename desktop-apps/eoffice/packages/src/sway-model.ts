import type { SwayPresentation, InteractiveSlide } from './types';
import { generateId } from './utils';

export class SwayModel {
  public presentations: SwayPresentation[];

  constructor(presentations: SwayPresentation[] = []) {
    this.presentations = presentations;
  }

  addPresentation(title: string): SwayPresentation {
    const now = new Date();
    const pres: SwayPresentation = { id: generateId(), title, slides: [], created_at: now, updated_at: now };
    this.presentations.push(pres);
    return pres;
  }

  removePresentation(id: string): boolean {
    const index = this.presentations.findIndex((p) => p.id === id);
    if (index === -1) return false;
    this.presentations.splice(index, 1);
    return true;
  }

  addSlide(presId: string, type: 'quiz' | 'poll' | 'qa', question: string, options?: string[]): InteractiveSlide | undefined {
    const pres = this.presentations.find((p) => p.id === presId);
    if (!pres) return undefined;
    const slide: InteractiveSlide = { id: generateId(), type, question, options, responses: [] };
    pres.slides.push(slide);
    pres.updated_at = new Date();
    return slide;
  }

  removeSlide(presId: string, slideId: string): boolean {
    const pres = this.presentations.find((p) => p.id === presId);
    if (!pres) return false;
    const index = pres.slides.findIndex((s) => s.id === slideId);
    if (index === -1) return false;
    pres.slides.splice(index, 1);
    pres.updated_at = new Date();
    return true;
  }

  submitResponse(presId: string, slideId: string, participantId: string, answer: string): boolean {
    const pres = this.presentations.find((p) => p.id === presId);
    if (!pres) return false;
    const slide = pres.slides.find((s) => s.id === slideId);
    if (!slide) return false;
    slide.responses.push({ participantId, answer, timestamp: new Date() });
    return true;
  }

  getResults(presId: string, slideId: string): Array<{ participantId: string; answer: string; timestamp: Date }> {
    const pres = this.presentations.find((p) => p.id === presId);
    if (!pres) return [];
    const slide = pres.slides.find((s) => s.id === slideId);
    return slide?.responses ?? [];
  }

  toJSON(): object {
    return { presentations: this.presentations };
  }

  static fromJSON(json: { presentations: SwayPresentation[] }): SwayModel {
    return new SwayModel(
      json.presentations.map((p) => ({
        ...p,
        created_at: new Date(p.created_at),
        updated_at: new Date(p.updated_at),
        slides: p.slides.map((s) => ({
          ...s,
          responses: s.responses.map((r) => ({ ...r, timestamp: new Date(r.timestamp) })),
        })),
      })),
    );
  }
}
