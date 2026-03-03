import { useEffect, useMemo } from 'react';
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
import { ToolNode, ArtifactNode } from './custom-nodes/CustomNodes';

interface ArtifactFlowProps {
  events: AgentEvent[];
  initialFileName: string;
}

export function ArtifactFlow({ events, initialFileName }: ArtifactFlowProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const nodeTypes = useMemo(() => ({ tool: ToolNode, artifact: ArtifactNode }), []);

  useEffect(() => {
    const newNodes: Node[] = [
      {
        id: 'input',
        type: 'input',
        data: { label: initialFileName },
        position: { x: 50, y: 150 },
        style: { background: '#f9fafb', border: '1px solid #e5e7eb', borderRadius: '8px', padding: '10px' }
      }
    ];
    const newEdges: Edge[] = [];

    let currentParentId = 'input';
    let xOffset = 300;

    // Track the current tool ID being executed to update it upon success
    let pendingToolNodeId: string | null = null;

    events.forEach((event, index) => {
      if (event.status === 'executing') {
        const toolId = `tool-${index}`;
        newNodes.push({
          id: toolId,
          type: 'tool',
          data: { label: event.tool || 'Unknown Tool', args: event.args, status: 'executing' },
          position: { x: xOffset, y: 150 },
        });
        newEdges.push({
          id: `edge-${currentParentId}-${toolId}`,
          source: currentParentId,
          target: toolId,
          animated: true,
          markerEnd: { type: MarkerType.ArrowClosed }
        });
        pendingToolNodeId = toolId;
        currentParentId = toolId;
        xOffset += 300;
      } else if (event.status === 'success') {
          // Mark the pending tool node as success
          if (pendingToolNodeId) {
             const toolNode = newNodes.find(n => n.id === pendingToolNodeId);
             if (toolNode) {
                 toolNode.data = { ...toolNode.data, status: 'success' };
                 // remove animated from edge
                 const incomingEdge = newEdges.find(e => e.target === pendingToolNodeId);
                 if (incomingEdge) incomingEdge.animated = false;
             }
             pendingToolNodeId = null;
          }

          if (event.result) {
              let resultStr = event.result;
              // the tool might return a JSON string
              if (typeof event.result === 'string') {
                  try {
                      const parsed = JSON.parse(event.result);
                      if (parsed.result_uri) {
                          resultStr = parsed.result_uri;
                      } else if (parsed.output_path) {
                          resultStr = parsed.output_path;
                      }
                  } catch (e) {
                      // Ignore parse errors, just use string
                  }
              }
              
              if (typeof resultStr === 'string' && (resultStr.includes('cleaned_') || resultStr.includes('result_'))) {
                 const match = resultStr.match(/(cleaned_|result_)[a-zA-Z0-9_-]+\.parquet/);
                 const label = match ? match[0] : resultStr.split('/').pop()?.replace(/["'}]/g, '') || 'Result';
                 
                 const resultId = `result-${index}`;
                 newNodes.push({
                    id: resultId,
                    type: 'artifact',
                    data: { label },
                    position: { x: xOffset, y: 150 },
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
      } else if (event.status === 'error') {
           if (pendingToolNodeId) {
               const toolNode = newNodes.find(n => n.id === pendingToolNodeId);
               if (toolNode) {
                   toolNode.data = { ...toolNode.data, status: 'error' };
                   toolNode.style = { ...toolNode.style, borderColor: '#f87171' }; // red border
                   const incomingEdge = newEdges.find(e => e.target === pendingToolNodeId);
                   if (incomingEdge) incomingEdge.animated = false;
               }
               pendingToolNodeId = null;
           }
      }
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [events, initialFileName, setNodes, setEdges]);

  return (
    <div className="h-full w-full bg-white rounded-xl overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
      >
        <Background />
        <Controls />
        <Panel position="top-right" className="bg-white/80 backdrop-blur px-3 py-1.5 border border-gray-200 shadow-sm rounded-lg text-xs font-medium text-gray-600">
          Data Lineage
        </Panel>
      </ReactFlow>
    </div>
  );
}
