import { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { Loader2, AlertCircle } from 'lucide-react';

interface DataTableProps {
  file: File;
}

export function DataTable({ file }: DataTableProps) {
  const [data, setData] = useState<any[]>([]);
  const [headers, setHeaders] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    // If it's a CSV, we can parse it directly
    if (file.name.endsWith('.csv')) {
      Papa.parse(file, {
        header: true,
        preview: 100, // Read only first 100 lines for preview
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length > 0 && results.data.length === 0) {
            setError('Failed to parse CSV file.');
          } else {
            setHeaders(results.meta.fields || []);
            setData(results.data);
          }
          setLoading(false);
        },
        error: (err) => {
          setError(err.message);
          setLoading(false);
        }
      });
    } else {
      // For parquet or other formats, we can't easily parse client-side without heavy libraries.
      setError('Preview is currently only supported for CSV files in the browser.');
      setLoading(false);
    }
  }, [file]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4 text-gray-500">
        <Loader2 className="h-8 w-8 animate-spin text-primary-500" />
        <p>Loading preview...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full space-y-4 text-gray-500 bg-gray-50 rounded-xl p-8 border border-dashed border-gray-200">
        <AlertCircle className="h-10 w-10 text-gray-400" />
        <p className="text-center">{error}</p>
        <p className="text-sm">You can still analyze the file using the AI chat.</p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500">
        <p>No data found.</p>
      </div>
    );
  }

  return (
    <div className="h-full w-full overflow-auto bg-white rounded-xl border border-gray-200">
      <table className="w-full text-sm text-left whitespace-nowrap">
        <thead className="text-xs text-gray-700 uppercase bg-gray-50 sticky top-0 shadow-sm z-10">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-6 py-3 font-medium tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50 transition-colors">
              {headers.map((header) => (
                <td key={`${i}-${header}`} className="px-6 py-4 text-gray-600 truncate max-w-[200px]">
                  {row[header]?.toString() || ''}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
