// src/components/pdf/PDFViewer.tsx
import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';
import { Button } from '@/components/ui/button';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PDFViewerProps {
  pdfUrl: string | null;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ pdfUrl }) => {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.0);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  if (!pdfUrl) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        Select a PDF to view
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-4 border-b bg-white">
      {/*<div className="flex items-center justify-between p-4 border-b">*/}
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setScale(scale => Math.max(0.5, scale - 0.1))}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <span className="text-sm">{Math.round(scale * 100)}%</span>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setScale(scale => Math.min(2, scale + 0.1))}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="icon"
            disabled={pageNumber <= 1}
            onClick={() => setPageNumber(page => page - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="text-sm">
            Page {pageNumber} of {numPages}
          </span>
          <Button
            variant="outline"
            size="icon"
            disabled={pageNumber >= numPages}
            onClick={() => setPageNumber(page => page + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* PDF Viewer */}

      {/*<div className="flex-1 overflow-auto bg-gray-100 p-4">*/}
      <div className="flex-1 overflow-auto bg-gray-100 p-4 relative min-h-0">
        {!pdfUrl ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            Select a PDF to view
          </div>
        ) : (
          <div className="flex justify-center min-h-full">
            <Document
              file={pdfUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              loading={
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="animate-pulse text-gray-500">Loading PDF...</div>
                </div>
              }
              error={
                <div className="absolute inset-0 flex items-center justify-center text-red-500">
                  Failed to load PDF
                </div>
              }
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={true}
                renderAnnotationLayer={true}
                className="shadow-lg"
              />
            </Document>
          </div>
        )}
      </div>
    </div>
  );
};

export default PDFViewer;