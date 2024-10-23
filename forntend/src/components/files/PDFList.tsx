// src/components/files/PDFList.tsx
import { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { ScrollArea } from '@/components/ui/scroll-area';
import { usePDFStore } from '../../hooks/usePDFs';

interface PDF {
  id: string;
  filename: string;
  url: string;
}

interface PDFListProps {
  onSelect: (url: string) => void;
  selectedPDF: string | null;
  refreshTrigger?: number;
}

const PDFList: React.FC<PDFListProps> = ({ onSelect, selectedPDF, refreshTrigger }) => {
  const [pdfs, setPdfs] = useState<PDF[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPDFs = async () => {
      try {
        setLoading(true);
        const data = await api.getPDFs();
        setPdfs(data);
      } catch (err) {
        setError('Failed to load PDFs');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPDFs();
  }, [refreshTrigger]); // Refresh when trigger changes

  if (loading) {
    return <div className="p-4 text-gray-500">Loading PDFs...</div>;
  }

  if (error) {
    return <div className="p-4 text-red-500">{error}</div>;
  }

  return (
    <ScrollArea className="h-full">
      <div className="space-y-2 p-4">
        {pdfs.map((pdf) => (
          <div
            key={pdf.id}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              selectedPDF === pdf.url 
                ? 'bg-blue-100 text-blue-900' 
                : 'hover:bg-gray-100'
            }`}
            onClick={() => onSelect(pdf.url)}
          >
            <p className="text-sm font-medium truncate">{pdf.filename}</p>
          </div>
        ))}
      </div>
    </ScrollArea>
  );
};

export default PDFList;