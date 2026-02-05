import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface SearchResult {
  text: string;
  metadata: {
    file_name: string;
    page_number: number;
    resource_id: string;
    chunk_id: string;
  };
  rerank_score: number;
  vector_score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_found: number;
  search_time_ms: number;
  has_more: boolean;
  offset: number;
  limit: number;
}

export interface UploadResponse {
  resource_id: string;
  filename: string;
  num_chunks: number;
  status: string;
}

export interface Resource {
  resource_id: string;
  filename: string;
  num_chunks: number;
  uploaded_at: string;
}

export interface PaginatedResourcesResponse {
  resources: Resource[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}

export interface ChunkDetail {
  chunk_id: string;
  text: string;
  page_number: number;
}

// API functions
export const uploadDocument = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/resources/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

export const searchDocuments = async (
  query: string,
  topK: number = 10,
  filters?: Record<string, any>,
  offset: number = 0,
  limit: number = 10
): Promise<SearchResponse> => {
  const response = await apiClient.post('/search', {
    query,
    top_k: topK,
    filters,
    offset,
    limit,
  });

  return response.data;
};

export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const getResources = async (offset: number = 0, limit: number = 20): Promise<PaginatedResourcesResponse> => {
  const response = await apiClient.get('/resources', {
    params: { offset, limit }
  });
  return response.data;
};

export const getResourceDetails = async (resourceId: string): Promise<ChunkDetail[]> => {
  const response = await apiClient.get(`/resources/${resourceId}/chunks`);
  return response.data;
};

export const deleteResource = async (resourceId: string): Promise<void> => {
  await apiClient.delete(`/resources/${resourceId}`);
};
