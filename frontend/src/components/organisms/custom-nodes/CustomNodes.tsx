import { memo, useState } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Settings, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '../../../lib/utils';

export const ToolNode = memo(({ data }: any) => {
  const [expanded, setExpanded] = useState(false);
  const { label, args, status } = data;

  return (
    <div className={cn(
      "px-4 py-3 shadow-md rounded-xl border-2 bg-white min-w-[200px] transition-all",
      status === 'success' ? "border-blue-300" : "border-gray-200"
    )}>
      <Handle type="target" position={Position.Left} className="w-2 h-2 !bg-blue-400" />
      
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
            <Settings className="h-4 w-4" />
          </div>
          <div className="font-medium text-sm text-gray-800">{label}</div>
        </div>
        <button 
          onClick={() => setExpanded(!expanded)} 
          className="text-gray-400 hover:text-gray-600 p-1"
        >
          {expanded ? <ChevronUp className="h-4 w-4"/> : <ChevronDown className="h-4 w-4"/>}
        </button>
      </div>

      {expanded && args && (
        <div className="mt-3 text-xs bg-gray-50 p-2 rounded border border-gray-100 font-mono text-gray-600 overflow-x-auto max-w-[250px]">
          <pre>{JSON.stringify(args, null, 2)}</pre>
        </div>
      )}
      
      <Handle type="source" position={Position.Right} className="w-2 h-2 !bg-blue-400" />
    </div>
  );
});

export const ArtifactNode = memo(({ data }: any) => {
  const { label } = data;

  return (
    <div className="px-4 py-3 shadow-md rounded-xl border-2 border-emerald-300 bg-white min-w-[150px]">
      <Handle type="target" position={Position.Left} className="w-2 h-2 !bg-emerald-400" />
      
      <div className="flex items-center space-x-2">
        <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-lg">
          <CheckCircle2 className="h-4 w-4" />
        </div>
        <div className="font-medium text-sm text-gray-800 break-all">{label}</div>
      </div>
      
      <Handle type="source" position={Position.Right} className="w-2 h-2 !bg-emerald-400" />
    </div>
  );
});
