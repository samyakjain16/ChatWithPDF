// src/services/api.ts
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  // Upload PDF
  uploadPDF: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  },

  // Get PDF list
  getPDFs: async () => {
    const response = await fetch(`${API_BASE_URL}/pdfs`);
    if (!response.ok) {
      throw new Error('Failed to fetch PDFs');
    }
    return response.json();
  }
};