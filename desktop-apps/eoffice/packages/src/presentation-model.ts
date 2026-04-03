import type { Slide, SlideElement, SlideElementType } from './types';
import { generateId } from './utils';

export class PresentationModel {
  public slides: Slide[];
  public theme: string;

  constructor(theme: string = 'default', slides: Slide[] = []) {
    this.theme = theme;
    this.slides = slides;
  }

  addSlide(background?: string): Slide {
    const slide: Slide = { id: generateId(), elements: [], background, transition: 'none' };
    this.slides.push(slide);
    return slide;
  }

  removeSlide(id: string): boolean {
    const index = this.slides.findIndex((s) => s.id === id);
    if (index === -1) return false;
    this.slides.splice(index, 1);
    return true;
  }

  reorderSlides(ids: string[]): boolean {
    if (ids.length !== this.slides.length) return false;
    const map = new Map(this.slides.map((s) => [s.id, s]));
    const reordered: Slide[] = [];
    for (const id of ids) {
      const slide = map.get(id);
      if (!slide) return false;
      reordered.push(slide);
    }
    this.slides = reordered;
    return true;
  }

  duplicateSlide(id: string): Slide | undefined {
    const source = this.slides.find((s) => s.id === id);
    if (!source) return undefined;
    const copy: Slide = {
      id: generateId(),
      elements: source.elements.map((e) => ({ ...e, id: generateId() })),
      background: source.background,
      notes: source.notes,
      transition: source.transition,
    };
    const index = this.slides.indexOf(source);
    this.slides.splice(index + 1, 0, copy);
    return copy;
  }

  addElement(
    slideId: string,
    type: SlideElementType,
    content: string,
    x: number,
    y: number,
    width: number,
    height: number,
  ): SlideElement | undefined {
    const slide = this.slides.find((s) => s.id === slideId);
    if (!slide) return undefined;
    const element: SlideElement = { id: generateId(), type, content, x, y, width, height };
    slide.elements.push(element);
    return element;
  }

  updateElement(slideId: string, elementId: string, updates: Partial<Omit<SlideElement, 'id'>>): boolean {
    const slide = this.slides.find((s) => s.id === slideId);
    if (!slide) return false;
    const el = slide.elements.find((e) => e.id === elementId);
    if (!el) return false;
    Object.assign(el, updates);
    return true;
  }

  removeElement(slideId: string, elementId: string): boolean {
    const slide = this.slides.find((s) => s.id === slideId);
    if (!slide) return false;
    const index = slide.elements.findIndex((e) => e.id === elementId);
    if (index === -1) return false;
    slide.elements.splice(index, 1);
    return true;
  }

  getSlideCount(): number {
    return this.slides.length;
  }

  toJSON(): object {
    return { theme: this.theme, slides: this.slides };
  }

  static fromJSON(json: { theme: string; slides: Slide[] }): PresentationModel {
    return new PresentationModel(json.theme, json.slides.map((s) => ({
      ...s,
      elements: s.elements.map((e) => ({ ...e })),
    })));
  }
}
