import React from 'react';
import { MessageCircle } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import './ChatPage.css';

export const ChatPage: React.FC = () => {
  const { messages, isLoading, error, sendMessage } = useChat();

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-title">
          <MessageCircle size={28} />
          <div>
            <h1>Chat with Documents</h1>
            <p className="subtitle">Ask questions and get answers from your knowledge base</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="chat-container">
        <MessageList messages={messages} />
        <ChatInput onSend={sendMessage} disabled={isLoading} />
      </div>
    </div>
  );
};
