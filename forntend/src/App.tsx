// src/App.tsx
import { useEffect } from 'react';
import FilesPanel from './components/files/FilesPanel';
import PDFViewer from './components/pdf/PDFViewer';
import ChatPanel from './components/chat/ChatPanel';
import { usePDFStore } from './hooks/usePDFs';

function App() {
  const selectedPDF = usePDFStore((state) => state.selectedPDF);
  const setSelectedPDF = usePDFStore((state) => state.setSelectedPDF);
  const fetchPDFs = usePDFStore((state) => state.fetchPDFs);

  // Fetch PDFs when app loads
  useEffect(() => {
    fetchPDFs();
  }, [fetchPDFs]);

  const handlePDFSelect = (url: string | null) => {
    setSelectedPDF(url);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden">
      <div className="w-[300px] flex-shrink-0 border-r border-gray-200">
        <FilesPanel 
        onPDFSelect={handlePDFSelect}
        selectedPDF={selectedPDF}
      />
      </div>
      <div className="flex-1 border-r border-gray-200">

      <PDFViewer pdfUrl={selectedPDF} />
      </div>
      <div className="w-[400px] flex-shrink-0">
      <ChatPanel currentPDF={selectedPDF} />
    </div>
    </div>

  );
}

export default App;