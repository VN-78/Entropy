import { useState, useCallback } from 'react';
import { Brain, Database, FileSpreadsheet, Sparkles, Activity } from 'lucide-react';
import { FileUploadZone } from '../molecules/FileUploadZone';
import { ChatInput } from '../molecules/ChatInput';
import { AgentTimeline } from '../organisms/AgentTimeline';
import { ArtifactFlow } from '../organisms/ArtifactFlow';
import { useAgent } from '../../hooks/useAgent';
import type { FileUploadResponse, Message, AgentEvent } from '../../types';
import { Card, CardContent, CardHeader, CardTitle } from '../atoms/Card';

export default function Dashboard() {
  const [file, setFile] = useState<FileUploadResponse | null>(null);
  const [allEvents, setAllEvents] = useState<AgentEvent[]>([]);
  const [chatMessages, setChatMessages] = useState<Message[]>([]);

  const handleEvent = useCallback((event: AgentEvent) => {
    setAllEvents(prev => [...prev, event]);
  }, []);

  const handleComplete = useCallback((message: string) => {
    // Only capture the *clean* message content for history (stripping <think> tags if backend sent them in raw message, 
    // but usually 'message' here is the final content string).
    // The backend sends message.content.
    const assistantMessage: Message = { role: 'assistant', content: message };
    setChatMessages(prev => [...prev, assistantMessage]);
  }, []);

  const { runAgent, isRunning } = useAgent({
    onEvent: handleEvent,
    onComplete: handleComplete
  });

  const handleFileUpload = (response: FileUploadResponse) => {
    setFile(response);
    setAllEvents([]);
    setChatMessages([]);
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

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center space-x-2">
          <div className="bg-primary-600 p-2 rounded-lg text-white">
            <Brain className="h-6 w-6" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Entropy <span className="text-primary-600">Refinery</span></h1>
        </div>
        <div className="flex items-center space-x-4">
           <div className="flex items-center space-x-1 text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              <Activity className="h-3 w-3 text-green-500" />
              <span>Backend Connected</span>
           </div>
        </div>
      </header>

      <main className="flex-1 p-8 max-w-7xl mx-auto w-full grid grid-cols-12 gap-8">
        {/* Left Column: Lineage & Transformation Map (Secondary) */}
        <div className="col-span-12 lg:col-span-4 flex flex-col space-y-8 h-[800px] lg:h-auto">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileSpreadsheet className="h-5 w-5 text-primary-600" />
                <span>Dataset Ingestion</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <FileUploadZone onUploadSuccess={handleFileUpload} />
            </CardContent>
          </Card>

          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="border-b border-gray-100">
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-primary-600" />
                <span>Lineage Map</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 p-0 relative min-h-[400px]">
                {file ? ( <ArtifactFlow events={allEvents} initialFileName={file.filename} /> ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 opacity-50 space-y-4">
                    <Database className="h-12 w-12" />
                    <p className="text-sm font-medium">Upload a dataset to see the flow</p>
                  </div>
                )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: AI Chat Interface (Primary) */}
        <div className="col-span-12 lg:col-span-8 flex flex-col h-[800px]">
          {file ? (
            <Card className="flex-1 flex flex-col h-full shadow-lg border-primary-100">
              <CardHeader className="border-b border-gray-100 bg-white sticky top-0 z-10">
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-primary-600" />
                  <span>AI Data Analyst</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col p-0 relative h-full">
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                  <AgentTimeline events={allEvents} />
                </div>
                <div className="p-4 bg-white border-t border-gray-100 sticky bottom-0">
                  <ChatInput onSend={handlePromptSubmit} disabled={isRunning} />
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-400 space-y-6 bg-white rounded-xl border border-dashed border-gray-300">
              <div className="p-4 bg-gray-50 rounded-full">
                <Brain className="h-16 w-16 text-gray-300" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">Ready to Analyze</h3>
                <p className="text-gray-500 max-w-sm mt-2">Upload a dataset to start the AI analysis session.</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
