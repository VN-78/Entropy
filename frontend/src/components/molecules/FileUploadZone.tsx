import React, { useState, useRef } from 'react';
import type { DragEvent, ChangeEvent } from 'react';
import { Upload, File as FileIcon, X as XIcon, CheckCircle } from 'lucide-react';
import { Button } from '../atoms/Button';
import { uploadFile } from '../../services/api';
import type { FileUploadResponse } from '../../types';
import { cn } from '../../lib/utils';

interface FileUploadZoneProps {
  onUploadSuccess: (response: FileUploadResponse) => void;
  className?: string;
}

export function FileUploadZone({ onUploadSuccess, className }: FileUploadZoneProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    setError(null);
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    try {
      const result = await uploadFile(file);
      onUploadSuccess(result);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) handleFileSelect(droppedFile);
  };

  return (
    <div className={cn('w-full', className)}>
      {!file ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            'flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-12 transition-all cursor-pointer',
            isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          )}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept=".csv,.parquet,.json"
          />
          <Upload className="h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-700">Drop your dataset here</p>
          <p className="text-sm text-gray-500 mt-1">Supports CSV, Parquet, and JSON</p>
        </div>
      ) : (
        <div className="border border-gray-200 rounded-xl p-4 bg-white flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-primary-50 p-3 rounded-lg">
              <FileIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div>
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {!isUploading ? (
              <>
                <Button onClick={handleUpload}>Analyze Now</Button>
                <Button variant="ghost" size="sm" onClick={() => setFile(null)}>
                  <XIcon className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <div className="flex items-center space-x-2 text-primary-600">
                <CheckCircle className="h-5 w-5 animate-pulse" />
                <span className="text-sm font-medium">Uploading...</span>
              </div>
            )}
          </div>
        </div>
      )}
      {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
    </div>
  );
}

