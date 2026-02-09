import React, { useState, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import './ChatPage.css';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="chat-input-container">
      <textarea
        className="chat-input"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Ask a question about your documents..."
        disabled={disabled}
        rows={1}
      />
      <button
        className="send-button"
        onClick={handleSubmit}
        disabled={disabled || !input.trim()}
        aria-label="Send message"
      >
        <Send size={20} />
      </button>
    </div>
  );
};
