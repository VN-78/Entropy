import { useState, useCallback, useMemo } from 'react';
import { Brain, Database, FileSpreadsheet, Sparkles, Activity, TableProperties, Share2 } from 'lucide-react';
import { FileUploadZone } from '../molecules/FileUploadZone';
import { ChatInput } from '../molecules/ChatInput';
import { AgentTimeline } from '../organisms/AgentTimeline';
import { ArtifactFlow } from '../organisms/ArtifactFlow';
import { DataTable } from '../organisms/DataTable';
import { VisualizationPanel } from '../organisms/VisualizationPanel';
import { useAgent } from '../../hooks/useAgent';
import type { FileUploadResponse, Message, AgentEvent } from '../../types';
import { Card, CardContent, CardHeader, CardTitle } from '../atoms/Card';

export default function Dashboard() {
  const [file, setFile] = useState<FileUploadResponse | null>(null);
  const [rawFile, setRawFile] = useState<File | null>(null);
  const [allEvents, setAllEvents] = useState<AgentEvent[]>([]);
  const [chatMessages, setChatMessages] = useState<Message[]>([]);
  const [activeTab, setActiveTab] = useState<'lineage' | 'data'>('lineage');

  const handleEvent = useCallback((event: AgentEvent) => {
    if (event.status === 'history_update' && event.messages) {
      setChatMessages(event.messages);
    } else {
      setAllEvents(prev => [...prev, event]);
    }
  }, []);

  const handleComplete = useCallback((message: string) => {
    // History managed by backend history_update
  }, []);

  const { runAgent, isRunning } = useAgent({
    onEvent: handleEvent,
    onComplete: handleComplete
  });

  const handleFileUpload = (response: FileUploadResponse, uploadedFile: File) => {
    setFile(response);
    setRawFile(uploadedFile);
    setAllEvents([]);
    setChatMessages([]);
    setActiveTab('data'); // Switch to data tab so user sees it
  };

  const handlePromptSubmit = (prompt: string) => {
    if (!file) return;
    
    const userMessage: Message = { role: 'user', content: prompt };
    
    // Optimistically update UI
    const userEvent: AgentEvent = { status: 'user_message', message: prompt };
    setAllEvents(prev => [...prev, userEvent]);
    
    // Update history for next context
    const updatedMessages = [...chatMessages, userMessage];
    setChatMessages(updatedMessages);
    
    runAgent(file.uri, updatedMessages);
  };

  const hasVisualization = useMemo(() => {
    return allEvents.some(e => e.status === 'success' && e.tool === 'generate_visualization' && e.result);
  }, [allEvents]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between sticky top-0 z-20 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-br from-primary-500 to-primary-700 p-2 rounded-xl text-white shadow-sm">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-gray-900 leading-none">Entropy</h1>
            <p className="text-xs text-primary-600 font-medium">Data Refinery Platform</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
           <div className="flex items-center space-x-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-100 px-3 py-1.5 rounded-full shadow-sm">
              <Activity className="h-3.5 w-3.5 text-emerald-500" />
              <span>System Online</span>
           </div>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-[1800px] mx-auto w-full grid grid-cols-12 gap-6">
        {/* Left Column: Lineage & Transformation Map (Secondary) */}
        <div className={`col-span-12 ${hasVisualization ? 'lg:col-span-3' : 'lg:col-span-4'} flex flex-col space-y-6 h-[calc(100vh-6rem)] transition-all duration-300`}>
          <Card className="shadow-sm border-gray-200 shrink-0">
            <CardHeader className="pb-4">
              <CardTitle className="flex items-center space-x-2 text-gray-800">
                <FileSpreadsheet className="h-5 w-5 text-primary-600" />
                <span>Dataset Ingestion</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FileUploadZone onUploadSuccess={handleFileUpload} />
            </CardContent>
          </Card>

          <Card className="flex-1 flex flex-col overflow-hidden shadow-sm border-gray-200">
            <div className="border-b border-gray-100 bg-white px-4 py-3 flex space-x-6 shrink-0">
              <button 
                onClick={() => setActiveTab('lineage')}
                className={`flex items-center space-x-2 text-sm font-medium transition-colors ${activeTab === 'lineage' ? 'text-primary-600 border-b-2 border-primary-600 pb-1 -mb-4' : 'text-gray-500 hover:text-gray-700'}`}
              >
                <Share2 className="h-4 w-4" />
                <span>Lineage Map</span>
              </button>
              <button 
                onClick={() => setActiveTab('data')}
                className={`flex items-center space-x-2 text-sm font-medium transition-colors ${activeTab === 'data' ? 'text-primary-600 border-b-2 border-primary-600 pb-1 -mb-4' : 'text-gray-500 hover:text-gray-700'}`}
              >
                <TableProperties className="h-4 w-4" />
                <span>Raw Data</span>
              </button>
            </div>
            <CardContent className="flex-1 p-0 relative min-h-[300px] bg-gray-50/50">
                {activeTab === 'lineage' && (
                  file ? ( <ArtifactFlow events={allEvents} initialFileName={file.filename} /> ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 space-y-4">
                      <Share2 className="h-10 w-10 opacity-20" />
                      <p className="text-sm font-medium">Upload a dataset to map lineage</p>
                    </div>
                  )
                )}
                {activeTab === 'data' && (
                  rawFile ? ( <DataTable file={rawFile} /> ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 space-y-4">
                      <TableProperties className="h-10 w-10 opacity-20" />
                      <p className="text-sm font-medium">Upload a CSV to view data</p>
                    </div>
                  )
                )}
            </CardContent>
          </Card>
        </div>

        {/* Middle/Right Column: AI Chat Interface (Primary) */}
        <div className={`col-span-12 ${hasVisualization ? 'lg:col-span-4' : 'lg:col-span-8'} flex flex-col h-[calc(100vh-6rem)] transition-all duration-300`}>
          {file ? (
            <Card className="flex-1 flex flex-col h-full shadow-md border-primary-100 ring-1 ring-primary-500/10">
              <CardHeader className="border-b border-gray-100 bg-white sticky top-0 z-10 py-4 px-6 shrink-0">
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-primary-600" />
                  <span className="text-gray-800">AI Data Analyst</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col p-0 relative h-full overflow-hidden">
                <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/30 scroll-smooth">
                  <AgentTimeline events={allEvents} />
                </div>
                <div className="p-4 bg-white border-t border-gray-100 shrink-0 shadow-[0_-4px_6px_-1px_rgb(0,0,0,0.02)]">
                  <ChatInput onSend={handlePromptSubmit} disabled={isRunning} />
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400 space-y-6 bg-white rounded-2xl border-2 border-dashed border-gray-200 shadow-sm">
              <div className="p-5 bg-gray-50 rounded-2xl">
                <Brain className="h-12 w-12 text-gray-300" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-700">Ready to Analyze</h3>
                <p className="text-gray-500 text-sm mt-2 max-w-xs">Upload your dataset to initialize the AI analysis environment.</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Visualization Panel */}
        {hasVisualization && (
          <div className="col-span-12 lg:col-span-5 flex flex-col h-[calc(100vh-6rem)] animate-in fade-in slide-in-from-right-4 duration-500">
            <VisualizationPanel events={allEvents} />
          </div>
        )}
      </main>
    </div>
  );
}
