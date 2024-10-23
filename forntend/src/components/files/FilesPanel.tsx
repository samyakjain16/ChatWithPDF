// src/components/files/FilesPanel.tsx
import { useState, useRef } from 'react';
import { Upload, X, AlertCircle, FileText } from 'lucide-react';
import { usePDFStore } from '../../hooks/usePDFs';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ACCEPTED_FILE_TYPES = ['application/pdf'];

interface UploadError {
  message: string;
  type: 'size' | 'type' | 'upload';
}


interface FilesPanelProps {
  onPDFSelect: (url: string | null) => void;
  selectedPDF: string | null;
}

const FilesPanel: React.FC<FilesPanelProps> = ({ onPDFSelect, selectedPDF: selectedPDFProp }) => {
  const {
    pdfs,
    loading,
    error: storeError,
    setSelectedPDF,
    uploadPDF,
    fetchPDFs
  } = usePDFStore(); 

  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<UploadError | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): UploadError | null => {
    if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
      return { message: 'Only PDF files are allowed', type: 'type' };
    }
    if (file.size > MAX_FILE_SIZE) {
      return { message: 'File size should be less than 10MB', type: 'size' };
    }
    return null;
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Reset states
    setUploadError(null);
    setUploadProgress(0);

    // Validate file
    const validationError = validateFile(file);
    if (validationError) {
      setUploadError(validationError);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    try {
      setIsUploading(true);
      setUploadProgress(20);

      // Simulate progress while uploading
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      await uploadPDF(file);
      
      clearInterval(progressInterval);
      setUploadProgress(100);

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Fetch updated PDF list
      await fetchPDFs();

    } catch (error) {
      setUploadError({ 
        message: 'Failed to upload file. Please try again.', 
        type: 'upload' 
      });
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
      // Reset progress after a delay
      setTimeout(() => setUploadProgress(0), 1000);
    }
  };

  const handleRetry = () => {
    setUploadError(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Header */}
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-gray-900">Documents</h2>
        <p className="text-sm text-gray-500">Upload and manage your PDFs</p>
      </div>

      {/* Upload Section */}
      <div className="p-4">
        <div className="relative">
          <label 
            className={cn(
              "flex flex-col items-center px-4 py-6 rounded-lg",
              "border-2 border-dashed transition-colors duration-200",
              isUploading 
                ? "border-blue-400 bg-blue-50" 
                : "border-gray-300 hover:border-blue-400",
              "cursor-pointer"
            )}
          >
            {!isUploading ? (
              <>
                <Upload className="w-8 h-8 text-gray-400" />
                <span className="mt-2 text-sm text-gray-500">
                  Click to upload or drag and drop
                </span>
                <span className="text-xs text-gray-400 mt-1">
                  PDF up to 10MB
                </span>
              </>
            ) : (
              <div className="w-full space-y-2">
                <div className="flex items-center justify-center">
                  <FileText className="w-8 h-8 text-blue-500 animate-pulse" />
                </div>
                <Progress value={uploadProgress} className="w-full" />
                <p className="text-xs text-center text-blue-500">
                  Uploading...
                </p>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf"
              onChange={handleFileUpload}
              disabled={isUploading}
            />
          </label>
        </div>

        {/* Error Display */}
        {uploadError && (
          <Alert variant="destructive" className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="ml-2">
              {uploadError.message}
              <Button
                variant="link"
                size="sm"
                onClick={handleRetry}
                className="ml-2"
              >
                Try Again
              </Button>
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* PDF List */}
      <ScrollArea className="flex-1">
      <div className="p-4 space-y-2">
        {pdfs.map((pdf) => (
         <div
    key={pdf.id}
    onClick={() => {
      setSelectedPDF(pdf.url);
      onPDFSelect(pdf.url);
    }}
    className={cn(
      "p-3 rounded-lg cursor-pointer",
      "hover:bg-gray-100",
      selectedPDFProp === pdf.url && "bg-blue-50"  // Use selectedPDFProp here
    )}
  >
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-gray-400" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {pdf.filename}
                </p>
                {pdf.uploadedAt && (
                  <p className="text-xs text-gray-500">
                    Uploaded {new Date(pdf.uploadedAt).toLocaleDateString()}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      </ScrollArea>

      {/* Global Error Display */}
      {storeError && (
        <div className="p-4 border-t">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="ml-2">
              {storeError}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
};

export default FilesPanel;