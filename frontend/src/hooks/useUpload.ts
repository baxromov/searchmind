import { useState } from 'react';
import { uploadDocument } from '../services/api';
import type { UploadResponse } from '../services/api';

export const useUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);

  const upload = async (file: File) => {
    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const response = await uploadDocument(file);
      setResult(response);
      return response;
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Upload failed';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const reset = () => {
    setError(null);
    setResult(null);
  };

  return { upload, uploading, error, result, reset };
};
