import { useEffect } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  Panel,
  useNodesState,
  useEdgesState,
  MarkerType,
  type Node,
  type Edge,
} from '@xyflow/react';
import type { AgentEvent } from '../../types';

interface ArtifactFlowProps {
  events: AgentEvent[];
  initialFileName: string;
}

export function ArtifactFlow({ events, initialFileName }: ArtifactFlowProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  useEffect(() => {
    const newNodes: Node[] = [
      {
        id: 'input',
        type: 'input',
        data: { label: initialFileName },
        position: { x: 50, y: 50 },
        style: { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '10px' }
      }
    ];
    const newEdges: Edge[] = [];

    let currentParentId = 'input';
    let xOffset = 300;

    events.forEach((event, index) => {
      if (event.status === 'executing') {
        const toolId = `tool-${index}`;
        newNodes.push({
          id: toolId,
          data: { label: event.tool || 'Unknown Tool' },
          position: { x: xOffset, y: 50 },
          style: { background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '50px', padding: '10px' }
        });
        newEdges.push({
          id: `edge-${currentParentId}-${toolId}`,
          source: currentParentId,
          target: toolId,
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed }
        });
        currentParentId = toolId;
        xOffset += 200;
      } else if (event.status === 'success' && event.result) {
          // If the result looks like a file path or URI
          if (typeof event.result === 'string' && (event.result.includes('cleaned_') || event.result.includes('result_'))) {
             const resultId = `result-${index}`;
             const label = event.result.split('/').pop() || 'Result';
             newNodes.push({
                id: resultId,
                data: { label },
                position: { x: xOffset, y: 50 },
                style: { background: '#ecfdf5', border: '1px solid #a7f3d0', borderRadius: '8px', padding: '10px' }
             });
             newEdges.push({
                id: `edge-${currentParentId}-${resultId}`,
                source: currentParentId,
                target: resultId,
                markerEnd: { type: MarkerType.ArrowClosed }
             });
             currentParentId = resultId;
             xOffset += 250;
          }
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [events, initialFileName, setNodes, setEdges]);

  return (
    <div className="h-full w-full bg-white rounded-xl border border-gray-200 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
        <Panel position="top-right" className="bg-white/80 backdrop-blur p-2 border border-gray-100 rounded text-[10px] text-gray-500">
          Data Transformation Map
        </Panel>
      </ReactFlow>
    </div>
  );
}
