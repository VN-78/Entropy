import axios from 'axios';
import type { FileUploadResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const uploadFile = async (file: File): Promise<FileUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post<FileUploadResponse>(
    `${API_BASE_URL}/files/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  
  return response.data;
};

// Note: For SSE (the /agent/run endpoint), we will use the native fetch API
// inside a custom hook or directly in the component so we can read the stream.
