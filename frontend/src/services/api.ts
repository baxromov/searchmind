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

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface Source {
  file_name: string;
  page_number: number;
  text: string;
  score: number;
}

export interface StreamCallbacks {
  onSources?: (sources: Source[]) => void;
  onQuery?: (query: string) => void;
  onChunk?: (text: string) => void;
  onDone?: () => void;
  onError?: (error: Error) => void;
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

export const streamChatMessage = async (
  message: string,
  history: ChatMessage[],
  callbacks: StreamCallbacks
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      history: history || [],
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to start chat stream');
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    throw new Error('No response body');
  }

  try {
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');

      // Keep the last incomplete chunk in buffer
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;

        const parts = line.split('\n');
        let event = '';
        let data = '';

        for (const part of parts) {
          if (part.startsWith('event:')) {
            event = part.substring(6).trim();
          } else if (part.startsWith('data:')) {
            data = part.substring(5).trim();
          }
        }

        if (!event || !data) continue;

        try {
          const parsedData = JSON.parse(data);

          switch (event) {
            case 'sources':
              callbacks.onSources?.(parsedData.sources);
              break;
            case 'query':
              callbacks.onQuery?.(parsedData.rewritten_query);
              break;
            case 'chunk':
              callbacks.onChunk?.(parsedData.text);
              break;
            case 'done':
              callbacks.onDone?.();
              break;
            case 'error':
              callbacks.onError?.(new Error(parsedData.error));
              break;
          }
        } catch (e) {
          console.error('Failed to parse SSE data:', e);
        }
      }
    }
  } catch (error) {
    callbacks.onError?.(error as Error);
  } finally {
    reader.releaseLock();
  }
};
