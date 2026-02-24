import { useState } from 'react';
import { Brain, Database, FileSpreadsheet, Sparkles, Activity } from 'lucide-react';
import { FileUploadZone } from '../molecules/FileUploadZone';
import { ChatInput } from '../molecules/ChatInput';
import { AgentTimeline } from '../organisms/AgentTimeline';
import { ArtifactFlow } from '../organisms/ArtifactFlow';
import { useAgent } from '../../hooks/useAgent';
import type { FileUploadResponse, Message } from '../../types';
import { Card, CardContent, CardHeader, CardTitle } from '../atoms/Card';

export default function Dashboard() {
  const [file, setFile] = useState<FileUploadResponse | null>(null);
  const { runAgent, isRunning, events } = useAgent();

  const handleFileUpload = (response: FileUploadResponse) => {
    setFile(response);
  };

  const handlePromptSubmit = (prompt: string) => {
    if (!file) return;
    
    const userMessage: Message = { role: 'user', content: prompt };
    runAgent(file.uri, [userMessage]);
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
        {/* Left Column: Input and Progress */}
        <div className="col-span-12 lg:col-span-5 flex flex-col space-y-8">
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

          {file && (
            <Card className="flex-1 flex flex-col">
              <CardHeader className="border-b border-gray-100">
                <CardTitle className="flex items-center space-x-2">
                  <Sparkles className="h-5 w-5 text-primary-600" />
                  <span>AI Data Analyst</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col p-0">
                <div className="flex-1 overflow-y-auto p-6 max-h-[500px]">
                  <AgentTimeline events={events} />
                </div>
                <div className="p-4 bg-gray-50 border-t border-gray-100 mt-auto">
                  <ChatInput onSend={handlePromptSubmit} disabled={isRunning} />
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Column: Visualization Map */}
        <div className="col-span-12 lg:col-span-7 flex flex-col h-[700px] lg:h-auto">
          <Card className="flex-1 flex flex-col overflow-hidden">
            <CardHeader className="border-b border-gray-100">
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5 text-primary-600" />
                <span>Lineage & Transformation Map</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 p-0 relative">
                {file ? ( <ArtifactFlow events={events} initialFileName={file.filename} /> ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-gray-400 opacity-50 space-y-4">
                    <Database className="h-16 w-16" />
                    <p className="text-lg font-medium">Upload a dataset to see the flow</p>
                  </div>
                )}
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
