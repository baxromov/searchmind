import React, { useEffect, useRef, useState } from 'react';
import { User, Bot, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { Message } from '../../hooks/useChat';
import './ChatPage.css';

interface MessageListProps {
  messages: Message[];
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleSources = (messageId: string) => {
    setExpandedSources(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  return (
    <div className="message-list">
      {messages.length === 0 && (
        <div className="empty-state">
          <Bot size={48} className="empty-icon" />
          <h3>Start a conversation</h3>
          <p>Ask me anything about your uploaded documents</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.role}`}
        >
          <div className="message-avatar">
            {message.role === 'user' ? (
              <User size={20} />
            ) : (
              <Bot size={20} />
            )}
          </div>

          <div className="message-content">
            <div className="message-text">
              {message.content}
              {message.isStreaming && (
                <span className="streaming-cursor">▋</span>
              )}
            </div>

            {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
              <div className="message-sources">
                <button
                  className="sources-toggle"
                  onClick={() => toggleSources(message.id)}
                >
                  <FileText size={16} />
                  <span>{message.sources.length} sources</span>
                  {expandedSources.has(message.id) ? (
                    <ChevronUp size={16} />
                  ) : (
                    <ChevronDown size={16} />
                  )}
                </button>

                {expandedSources.has(message.id) && (
                  <div className="sources-list">
                    {message.sources.map((source, idx) => (
                      <div key={idx} className="source-item">
                        <div className="source-header">
                          <FileText size={14} />
                          <span className="source-file">
                            {source.file_name} (Page {source.page_number})
                          </span>
                          <span className="source-score">
                            {(source.score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="source-text">
                          {source.text.substring(0, 200)}
                          {source.text.length > 200 && '...'}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      ))}

      <div ref={messagesEndRef} />
    </div>
  );
};
