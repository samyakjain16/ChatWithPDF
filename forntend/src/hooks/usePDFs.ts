// src/hooks/usePDFs.ts
import { create } from 'zustand';
import { api } from '../services/api';

interface PDF {
  id: string;
  filename: string;
  url: string;
  uploadedAt: string;
}
interface PDFStore {
  pdfs: PDF[];
  loading: boolean;
  error: string | null;
  selectedPDF: string | null;
  setSelectedPDF: (url: string | null) => void;
  fetchPDFs: () => Promise<void>;
  uploadPDF: (file: File) => Promise<void>;
}

export const usePDFStore = create<PDFStore>((set) => ({
  pdfs: [],
  loading: false,
  error: null,
  selectedPDF: null,

  setSelectedPDF: (url) => set({ selectedPDF: url }),

  fetchPDFs: async () => {
    set({ loading: true, error: null });
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/pdfs');
      if (!response.ok) throw new Error('Failed to fetch PDFs');
      const data = await response.json();
      set({ pdfs: data });
    } catch (error) {
      set({ error: 'Failed to fetch PDFs' });
      console.error('Error fetching PDFs:', error);
    } finally {
      set({ loading: false });
    }
  },

  uploadPDF: async (file: File) => {
    set({ loading: true, error: null });
    try {
      await api.uploadPDF(file);
      // Refresh PDF list after upload
      const data = await api.getPDFs();
      set({ pdfs: data });
    } catch (error) {
      set({ error: 'Failed to upload PDF' });
      console.error(error);
    } finally {
      set({ loading: false });
    }
  }
}));