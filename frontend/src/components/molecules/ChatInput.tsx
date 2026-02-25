import { useState, useRef, useEffect } from 'react';
import type { FormEvent, KeyboardEvent } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '../atoms/Button';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, disabled, placeholder = "Ask me to analyze something..." }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [input]);

  const handleSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
      // Reset height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative flex items-end space-x-2 w-full bg-white rounded-xl border border-gray-200 shadow-sm focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-transparent transition-all p-2">
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        className="flex-1 max-h-[200px] min-h-[44px] py-3 px-2 text-sm bg-transparent border-none focus:ring-0 resize-none disabled:opacity-50"
        style={{ height: 'auto' }}
      />
      <Button 
        type="submit" 
        disabled={disabled || !input.trim()}
        className={`rounded-lg h-10 w-10 p-0 flex items-center justify-center transition-all ${
          disabled || !input.trim() ? 'bg-gray-100 text-gray-400' : 'bg-primary-600 text-white hover:bg-primary-700'
        }`}
      >
        {disabled ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
      </Button>
    </form>
  );
}
