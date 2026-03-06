import { create } from 'zustand';
import type { ClassificationResult } from '../types';

interface ClassificationState {
  results: ClassificationResult[];
  currentResult: ClassificationResult | null;
  uploading: boolean;
  processing: boolean;
  error: string | null;

  // Actions
  addResult: (result: ClassificationResult) => void;
  setCurrentResult: (result: ClassificationResult | null) => void;
  clearHistory: () => void;
  uploadImage: (file: File) => Promise<ClassificationResult>;
  uploadMultiple: (files: File[]) => Promise<ClassificationResult[]>;
}

export const useClassificationStore = create<ClassificationState>((set, get) => ({
  results: [],
  currentResult: null,
  uploading: false,
  processing: false,
  error: null,

  addResult: (result) => {
    const { results } = get();
    set({ results: [result, ...results], currentResult: result });
  },

  setCurrentResult: (result) => set({ currentResult: result }),

  clearHistory: () => set({ results: [], currentResult: null }),

  uploadImage: async (file: File) => {
    set({ processing: true, error: null });
    
    try {
      // Create object URL for preview
      const imageUrl = URL.createObjectURL(file);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock classification result
      const mockClasses = [
        'Galaxy - Spiral',
        'Galaxy - Elliptical',
        'Nebula - Emission',
        'Nebula - Planetary',
        'Star Cluster',
        'Supernova Remnant',
      ];
      
      const primaryClass = mockClasses[Math.floor(Math.random() * mockClasses.length)];
      const alternatives = mockClasses
        .filter(c => c !== primaryClass)
        .slice(0, 3)
        .map(c => ({
          class: c,
          confidence: Math.random() * 0.3,
        }))
        .sort((a, b) => b.confidence - a.confidence);

      const result: ClassificationResult = {
        id: crypto.randomUUID(),
        imageUrl,
        className: primaryClass,
        confidence: 0.7 + Math.random() * 0.29,
        timestamp: new Date(),
        alternativeClasses: alternatives,
      };

      get().addResult(result);
      return result;
    } catch (error) {
      set({ error: 'Classification failed', processing: false });
      throw error;
    } finally {
      set({ processing: false });
    }
  },

  uploadMultiple: async (files: File[]) => {
    set({ uploading: true, error: null });
    
    try {
      const results: ClassificationResult[] = [];
      
      for (const file of files) {
        try {
          const result = await get().uploadImage(file);
          results.push(result);
        } catch (error) {
          console.error(`Failed to classify ${file.name}`, error);
        }
      }
      
      return results;
    } finally {
      set({ uploading: false });
    }
  },
}));
