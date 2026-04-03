import { useState, useCallback } from 'react';

export interface SlideElement {
  id: string;
  type: 'text' | 'shape';
  content: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string;
}

export interface Slide {
  id: string;
  elements: SlideElement[];
}

let nextId = 1;
const uid = () => `el-${nextId++}`;
const slideUid = () => `slide-${nextId++}`;

function createBlankSlide(): Slide {
  return { id: slideUid(), elements: [] };
}

export function usePresentation() {
  const [slides, setSlides] = useState<Slide[]>([createBlankSlide()]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);

  const currentSlide = slides[currentIndex] || slides[0];

  const addSlide = useCallback(() => {
    setSlides((prev) => {
      const newSlides = [...prev];
      newSlides.splice(currentIndex + 1, 0, createBlankSlide());
      return newSlides;
    });
    setCurrentIndex((prev) => prev + 1);
  }, [currentIndex]);

  const removeSlide = useCallback(
    (index: number) => {
      if (slides.length <= 1) return;
      setSlides((prev) => prev.filter((_, i) => i !== index));
      setCurrentIndex((prev) => (prev >= slides.length - 1 ? Math.max(0, prev - 1) : prev));
    },
    [slides.length],
  );

  const duplicateSlide = useCallback(
    (index: number) => {
      setSlides((prev) => {
        const source = prev[index];
        const dup: Slide = {
          id: slideUid(),
          elements: source.elements.map((el) => ({ ...el, id: uid() })),
        };
        const newSlides = [...prev];
        newSlides.splice(index + 1, 0, dup);
        return newSlides;
      });
      setCurrentIndex(index + 1);
    },
    [],
  );

  const updateSlide = useCallback((index: number, elements: SlideElement[]) => {
    setSlides((prev) => prev.map((s, i) => (i === index ? { ...s, elements } : s)));
  }, []);

  const addElement = useCallback(
    (type: 'text' | 'shape', content: string) => {
      const el: SlideElement = {
        id: uid(),
        type,
        content,
        x: 20 + Math.random() * 30,
        y: 20 + Math.random() * 20,
        width: type === 'text' ? 40 : 15,
        height: type === 'text' ? 10 : 15,
        color: type === 'shape' ? '#ea580c' : undefined,
      };
      setSlides((prev) =>
        prev.map((s, i) =>
          i === currentIndex ? { ...s, elements: [...s.elements, el] } : s,
        ),
      );
      setSelectedElementId(el.id);
    },
    [currentIndex],
  );

  const updateElement = useCallback(
    (id: string, updates: Partial<SlideElement>) => {
      setSlides((prev) =>
        prev.map((s, i) =>
          i === currentIndex
            ? { ...s, elements: s.elements.map((el) => (el.id === id ? { ...el, ...updates } : el)) }
            : s,
        ),
      );
    },
    [currentIndex],
  );

  const removeElement = useCallback(
    (id: string) => {
      setSlides((prev) =>
        prev.map((s, i) =>
          i === currentIndex ? { ...s, elements: s.elements.filter((el) => el.id !== id) } : s,
        ),
      );
      setSelectedElementId(null);
    },
    [currentIndex],
  );

  return {
    slides,
    currentIndex,
    currentSlide,
    selectedElementId,
    setCurrentIndex,
    setSelectedElementId,
    addSlide,
    removeSlide,
    duplicateSlide,
    updateSlide,
    addElement,
    updateElement,
    removeElement,
  };
}
