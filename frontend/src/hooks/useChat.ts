import { useState, useCallback } from 'react';
import { type ChatMessage, type Source, streamChatMessage } from '../services/api';

export interface Message extends ChatMessage {
  id: string;
  sources?: Source[];
  rewritten_query?: string;
  isStreaming?: boolean;
}

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setIsLoading(true);
    setError(null);

    // Add user message immediately
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
    };

    setMessages(prev => [...prev, userMessage]);

    // Create placeholder for assistant message
    const assistantMessageId = `assistant-${Date.now()}`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      isStreaming: true,
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      // Get chat history (exclude the current user message)
      const history: ChatMessage[] = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      await streamChatMessage(
        content,
        history,
        {
          onSources: (sources) => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, sources }
                  : msg
              )
            );
          },
          onQuery: (rewritten_query) => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, rewritten_query }
                  : msg
              )
            );
          },
          onChunk: (text) => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, content: msg.content + text }
                  : msg
              )
            );
          },
          onDone: () => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? { ...msg, isStreaming: false }
                  : msg
              )
            );
            setIsLoading(false);
          },
          onError: (err) => {
            setError(err.message);
            setMessages(prev =>
              prev.map(msg =>
                msg.id === assistantMessageId
                  ? {
                      ...msg,
                      content: 'Sorry, I encountered an error. Please try again.',
                      isStreaming: false,
                    }
                  : msg
              )
            );
            setIsLoading(false);
          },
        }
      );
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMsg);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: 'Sorry, I encountered an error. Please try again.',
                isStreaming: false,
              }
            : msg
        )
      );
      setIsLoading(false);
    }
  }, [messages]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
    setIsLoading(false);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearChat,
  };
};
