import { useMemo } from 'react';
import { 
  BarChart, Bar, 
  LineChart, Line, 
  ScatterChart, Scatter, 
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import type { AgentEvent } from '../../types';
import { PieChart as PieChartIcon, BarChart3, TrendingUp, ScatterChart as ScatterIcon } from 'lucide-react';

interface VisualizationPanelProps {
  events: AgentEvent[];
}

const COLORS = ['#0ea5e9', '#8b5cf6', '#6366f1', '#10b981', '#f59e0b', '#f43f5e', '#ec4899'];

export function VisualizationPanel({ events }: VisualizationPanelProps) {
  // Find the latest successful visualization event
  const latestVizEvent = useMemo(() => {
    return [...events].reverse().find(e => 
      e.status === 'success' && 
      e.tool === 'generate_visualization' && 
      e.result
    );
  }, [events]);

  if (!latestVizEvent) return null;

  let spec: any = null;
  try {
    spec = typeof latestVizEvent.result === 'string' ? JSON.parse(latestVizEvent.result) : latestVizEvent.result;
  } catch (e) {
    return null;
  }

  if (spec?.type !== 'visualization') return null;

  const { chart_type, data, x_column, y_column } = spec;

  const renderChart = () => {
    switch (chart_type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey={x_column} angle={-45} textAnchor="end" tick={{ fontSize: 12, fill: '#6b7280' }} height={60} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip cursor={{ fill: '#f3f4f6' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey={y_column} fill="#0ea5e9" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        );
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
              <XAxis dataKey={x_column} angle={-45} textAnchor="end" tick={{ fontSize: 12, fill: '#6b7280' }} height={60} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Line type="monotone" dataKey={y_column} stroke="#8b5cf6" strokeWidth={2} dot={{ r: 4, fill: '#8b5cf6' }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis type="number" dataKey={x_column} name={x_column} tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis type="number" dataKey={y_column} name={y_column} tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Scatter name={`${y_column} vs ${x_column}`} data={data} fill="#ec4899" />
            </ScatterChart>
          </ResponsiveContainer>
        );
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Pie
                data={data}
                nameKey={x_column}
                dataKey={y_column}
                cx="50%"
                cy="50%"
                outerRadius={120}
                innerRadius={60}
                paddingAngle={2}
                label={{ fill: '#6b7280', fontSize: 12 }}
              >
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        );
      default:
        return (
          <div className="flex items-center justify-center h-full text-gray-500">
            Unsupported chart type: {chart_type}
          </div>
        );
    }
  };

  const ChartIcon = {
    bar: BarChart3,
    line: TrendingUp,
    scatter: ScatterIcon,
    pie: PieChartIcon
  }[chart_type as 'bar'|'line'|'scatter'|'pie'] || BarChart3;

  return (
    <div className="flex flex-col h-full bg-white rounded-xl shadow-md border-gray-200 border ring-1 ring-black/5 overflow-hidden">
      <div className="border-b border-gray-100 bg-white px-4 py-3 flex items-center space-x-2 shrink-0">
         <div className="p-1.5 bg-blue-50 text-blue-600 rounded-lg">
           <ChartIcon className="h-4 w-4" />
         </div>
         <h3 className="font-semibold text-gray-800 text-sm">
           {y_column} by {x_column}
         </h3>
      </div>
      <div className="flex-1 p-4 min-h-[300px]">
        {renderChart()}
      </div>
    </div>
  );
}
