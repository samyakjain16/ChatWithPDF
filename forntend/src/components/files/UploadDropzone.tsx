// src/components/files/UploadDropzone.tsx
import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UploadDropzoneProps {
  onUploadStart: () => void;
  onUploadComplete: () => void;
}

const UploadDropzone: React.FC<UploadDropzoneProps> = ({
  onUploadStart,
  onUploadComplete,
}) => {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    try {
      onUploadStart();
      const file = acceptedFiles[0];
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/v1/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      onUploadComplete();
    } catch (error) {
      console.error('Upload error:', error);
      onUploadComplete();
    }
  }, [onUploadStart, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-lg p-6 transition-colors",
        "hover:border-blue-500 hover:bg-blue-50/50",
        isDragActive ? "border-blue-500 bg-blue-50/50" : "border-gray-300",
        "cursor-pointer"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center text-sm text-gray-600">
        <Upload className="h-8 w-8 mb-2 text-gray-400" />
        <p className="text-center">
          Drop your PDF here or click to browse
        </p>
      </div>
    </div>
  );
};

export default UploadDropzone;