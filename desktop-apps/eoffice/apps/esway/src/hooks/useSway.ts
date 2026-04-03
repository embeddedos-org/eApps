import { useState, useCallback } from 'react';

export type SlideType = 'quiz' | 'poll' | 'qa';
export interface SlideOption { text: string; votes: number; }
export interface Slide { id: string; type: SlideType; question: string; options: SlideOption[]; }

let nextId = 1;
const uid = () => `s${nextId++}`;

const SEED: Slide[] = [
  {
    id: uid(), type: 'quiz', question: 'What does HTML stand for?',
    options: [
      { text: 'Hyper Text Markup Language', votes: 15 },
      { text: 'High Tech Modern Language', votes: 3 },
      { text: 'Hyper Transfer Markup Language', votes: 2 },
      { text: 'Home Tool Markup Language', votes: 1 },
    ],
  },
  {
    id: uid(), type: 'poll', question: 'What is your preferred code editor?',
    options: [
      { text: 'VS Code', votes: 24 },
      { text: 'IntelliJ', votes: 8 },
      { text: 'Vim/Neovim', votes: 6 },
      { text: 'Other', votes: 3 },
    ],
  },
  {
    id: uid(), type: 'qa', question: 'Any questions about the new API?',
    options: [
      { text: 'How does auth work?', votes: 5 },
      { text: 'What about rate limits?', votes: 3 },
    ],
  },
];

export function useSway() {
  const [slides, setSlides] = useState<Slide[]>(SEED);
  const [currentSlideId, setCurrentSlideId] = useState<string>(SEED[0].id);

  const currentSlide = slides.find((s) => s.id === currentSlideId) ?? null;
  const totalResponses = slides.reduce((sum: number, s: Slide) => sum + s.options.reduce((os: number, o: SlideOption) => os + o.votes, 0), 0);

  const addSlide = useCallback((type: SlideType, question: string, options: string[]) => {
    const id = uid();
    setSlides((prev: Slide[]) => [...prev, { id, type, question, options: options.map((text: string) => ({ text, votes: 0 })) }]);
    setCurrentSlideId(id);
  }, []);

  const submitResponse = useCallback((slideId: string, optionIdx: number) => {
    setSlides((prev: Slide[]) => prev.map((s: Slide) => {
      if (s.id !== slideId) return s;
      const options = s.options.map((o: SlideOption, i: number) => (i === optionIdx ? { ...o, votes: o.votes + 1 } : o));
      return { ...s, options };
    }));
  }, []);

  return {
    slides, currentSlideId, currentSlide, totalResponses,
    setCurrentSlideId, addSlide, submitResponse,
  };
}
