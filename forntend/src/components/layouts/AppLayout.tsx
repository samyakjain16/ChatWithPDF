// src/components/layout/AppLayout.tsx
import { useState } from 'react';
import FilesPanel from '../files/FilesPanel';
import PDFViewer from '../pdf/PDFViewer';
import ChatPanel from '../chat/ChatPanel';

const AppLayout = () => {  // Removed unused interface
  const [selectedPDF, setSelectedPDF] = useState<string | null>(null);

  const handlePDFSelect = (url: string | null) => {
    setSelectedPDF(url);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Panel - Files */}
      <div className="w-1/5 border-r border-gray-200 bg-white">
        <FilesPanel 
          onPDFSelect={handlePDFSelect} 
          selectedPDF={selectedPDF} 
        />
      </div>

      {/* Middle Panel - PDF Viewer */}
      <div className="w-[45%] border-r border-gray-200">
        <PDFViewer pdfUrl={selectedPDF} />
      </div>

      {/* Right Panel - Chat */}
      <div className="w-[35%]">
        <ChatPanel currentPDF={selectedPDF} />
      </div>
    </div>
  );
};

export default AppLayout;