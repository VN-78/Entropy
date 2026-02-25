import { 
  Search, 
  Database, 
  Wand2, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Info,
  BrainCircuit,
  ChevronDown,
  ChevronRight,
  Sparkles,
  User
} from 'lucide-react';
import { useState } from 'react';
import type { AgentEvent } from '../../types';
import { cn } from '../../lib/utils';

interface AgentTimelineProps {
  events: AgentEvent[];
}

function parseMessage(message: string) {
  const thinkMatch = message.match(/<think>([\s\S]*?)<\/think>/);
  const thinkContent = thinkMatch ? thinkMatch[1].trim() : null;
  const cleanMessage = message.replace(/<think>[\s\S]*?<\/think>/, '').trim();
  
  return { thinkContent, cleanMessage };
}

function CollapsibleThought({ content }: { content: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mt-4 mb-4 border border-purple-100 rounded-lg overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-3 bg-purple-50 hover:bg-purple-100 transition-colors text-left"
      >
        <div className="flex items-center space-x-2 text-purple-700 font-medium text-sm">
          <BrainCircuit className="h-4 w-4" />
          <span>Reasoning Process</span>
        </div>
        {isOpen ? <ChevronDown className="h-4 w-4 text-purple-500" /> : <ChevronRight className="h-4 w-4 text-purple-500" />}
      </button>
      {isOpen && (
        <div className="p-4 bg-white text-gray-600 text-sm font-mono whitespace-pre-wrap leading-relaxed border-t border-purple-100">
          {content}
        </div>
      )}
    </div>
  );
}

export function AgentTimeline({ events }: AgentTimelineProps) {
  const getIcon = (event: AgentEvent) => {
    if (event.status === 'user_message') return <User className="h-5 w-5 text-white" />;
    if (event.status === 'thinking') return <BrainCircuit className="h-5 w-5 text-purple-500" />;
    if (event.status === 'executing') {
      if (event.tool === 'inspect_dataset') return <Search className="h-5 w-5 text-blue-500" />;
      if (event.tool === 'run_sql_query') return <Database className="h-5 w-5 text-indigo-500" />;
      if (event.tool === 'clean_dataset') return <Wand2 className="h-5 w-5 text-emerald-500" />;
      return <Loader2 className="h-5 w-5 text-gray-500 animate-spin" />;
    }
    if (event.status === 'success') return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    if (event.status === 'error') return <AlertCircle className="h-5 w-5 text-red-500" />;
    if (event.status === 'info') return <Info className="h-5 w-5 text-sky-500" />;
    return <Info className="h-5 w-5 text-gray-400" />;
  };

  return (
    <div className="flex flex-col space-y-4">
      {events.map((event, index) => {
        // Special handling for user messages
        if (event.status === 'user_message') {
          return (
            <div key={index} className="flex justify-end animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className="bg-primary-600 text-white p-4 rounded-xl rounded-tr-none max-w-[80%] shadow-sm">
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{event.message}</p>
              </div>
            </div>
          );
        }

        // Special handling for completion events which might contain <think> blocks
        if (event.status === 'complete') {
          const { thinkContent, cleanMessage } = parseMessage(event.message);
          
          return (
            <div 
              key={index} 
              className="flex flex-col space-y-2 animate-in fade-in slide-in-from-bottom-2 duration-300"
            >
              {/* If there's a think block, show it first */}
              {thinkContent && <CollapsibleThought content={thinkContent} />}
              
              {/* The final answer */}
              <div className="flex items-start space-x-4 p-4 rounded-xl bg-white border border-gray-200 shadow-sm">
                <div className="mt-1 bg-primary-100 p-1.5 rounded-lg">
                  <Sparkles className="h-5 w-5 text-primary-600" />
                </div>
                <div className="flex-1 text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                  {cleanMessage}
                </div>
              </div>
            </div>
          );
        }

        return (
          <div 
            key={index} 
            className={cn(
              "flex items-start space-x-4 p-3 rounded-lg border text-sm animate-in fade-in slide-in-from-bottom-2 duration-300",
              {
                "bg-purple-50 border-purple-100": event.status === 'thinking',
                "bg-blue-50 border-blue-100": event.status === 'executing',
                "bg-green-50 border-green-100": event.status === 'success',
                "bg-red-50 border-red-100": event.status === 'error',
                "bg-gray-50 border-gray-200": event.status === 'info',
              }
            )}
          >
            <div className="mt-0.5">
              {getIcon(event)}
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <p className={cn(
                  "font-medium capitalize",
                  {
                    "text-purple-700": event.status === 'thinking',
                    "text-blue-700": event.status === 'executing',
                    "text-green-700": event.status === 'success',
                    "text-red-700": event.status === 'error',
                    "text-gray-700": event.status === 'info',
                  }
                )}>
                  {event.status === 'executing' ? `Running ${event.tool}` : event.status}
                </p>
                {event.status === 'executing' && <Loader2 className="h-3 w-3 animate-spin text-blue-400" />}
              </div>
              <p className="text-gray-600 mt-1">{event.message}</p>
              
              {event.args && (
                <div className="mt-2 p-2 bg-black/5 rounded text-[10px] font-mono overflow-x-auto text-gray-700">
                  <pre>{JSON.stringify(event.args, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        );
      })}
      
      {events.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-gray-400 opacity-50">
          <BrainCircuit className="h-12 w-12 mb-4" />
          <p>Agent is waiting for instructions...</p>
        </div>
      )}
    </div>
  );
}
