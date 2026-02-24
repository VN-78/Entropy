import { 
  Search, 
  Database, 
  Wand2, 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  Info,
  BrainCircuit
} from 'lucide-react';
import type { AgentEvent } from '../../types';
import { cn } from '../../lib/utils';

interface AgentTimelineProps {
  events: AgentEvent[];
}

export function AgentTimeline({ events }: AgentTimelineProps) {
  const getIcon = (event: AgentEvent) => {
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
      {events.map((event, index) => (
        <div 
          key={index} 
          className={cn(
            "flex items-start space-x-4 p-4 rounded-xl border animate-in fade-in slide-in-from-bottom-2 duration-300",
            {
              "bg-purple-50 border-purple-100": event.status === 'thinking',
              "bg-blue-50 border-blue-100": event.status === 'executing',
              "bg-green-50 border-green-100": event.status === 'success',
              "bg-red-50 border-red-100": event.status === 'error',
              "bg-white border-gray-100": event.status === 'info' || event.status === 'complete',
            }
          )}
        >
          <div className="mt-0.5">
            {getIcon(event)}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <p className={cn(
                "text-sm font-semibold capitalize",
                {
                  "text-purple-700": event.status === 'thinking',
                  "text-blue-700": event.status === 'executing',
                  "text-green-700": event.status === 'success',
                  "text-red-700": event.status === 'error',
                  "text-gray-700": event.status === 'info' || event.status === 'complete',
                }
              )}>
                {event.status === 'executing' ? `Running ${event.tool}` : event.status}
              </p>
              {event.status === 'executing' && <Loader2 className="h-3 w-3 animate-spin text-blue-400" />}
            </div>
            <p className="text-sm text-gray-600 mt-1">{event.message}</p>
            
            {event.args && (
              <div className="mt-2 p-2 bg-black/5 rounded text-[10px] font-mono overflow-x-auto">
                <pre>{JSON.stringify(event.args, null, 2)}</pre>
              </div>
            )}
            
            {event.status === 'complete' && (
              <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                {event.message}
              </div>
            )}
          </div>
        </div>
      ))}
      
      {events.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12 text-gray-400 opacity-50">
          <BrainCircuit className="h-12 w-12 mb-4" />
          <p>Agent is waiting for instructions...</p>
        </div>
      )}
    </div>
  );
}
