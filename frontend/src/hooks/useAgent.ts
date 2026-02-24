import { useState, useCallback, useRef } from 'react';
import type { AgentEvent, Message } from '../types';

interface UseAgentProps {
  onEvent?: (event: AgentEvent) => void;
  onComplete?: (message: string) => void;
  onError?: (error: string) => void;
}

export function useAgent({ onEvent, onComplete, onError }: UseAgentProps = {}) {
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const runAgent = useCallback(async (fileUri: string, messages: Message[]) => {
    setIsRunning(true);
    setEvents([]); // Reset events

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('http://localhost:8000/api/v1/agent/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file_uri: fileUri, messages }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // SSE messages are separated by double newlines
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || ''; // Keep the incomplete part in the buffer

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const dataStr = part.replace('data: ', '');
            try {
              const event: AgentEvent = JSON.parse(dataStr);
              setEvents(prev => [...prev, event]);
              if (onEvent) onEvent(event);

              if (event.status === 'complete') {
                if (onComplete) onComplete(event.message);
                setIsRunning(false);
              } else if (event.status === 'error') {
                if (onError) onError(event.message);
                setIsRunning(false);
              }
            } catch (err) {
              console.error('Failed to parse SSE event:', err);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name !== 'AbortError') {
        setEvents(prev => [...prev, { status: 'error', message: error.message }]);
        if (onError) onError(error.message);
      }
      setIsRunning(false);
    }
  }, [onEvent, onComplete, onError]);

  const stopAgent = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsRunning(false);
  }, []);

  return {
    runAgent,
    stopAgent,
    isRunning,
    events,
  };
}
