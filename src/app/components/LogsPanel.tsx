import { useEffect, useRef, useState } from 'react';

export function LogsPanel() {
  const [logs, setLogs] = useState<string[]>([]);
  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Fetch initial logs
    const fetchLogs = async () => {
      try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        setLogs(data.lines || []);
      } catch (error) {
        console.error('Failed to fetch logs:', error);
      }
    };

    fetchLogs();

    // Connect to SSE stream for new logs
    const eventSource = new EventSource('/api/logs/stream');

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.line) {
          setLogs(prev => [...prev, data.line]);
        }
      } catch (error) {
        console.error('Failed to parse log event:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Log stream error:', error);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="p-8 h-full flex flex-col">
      <h2 className="mb-6">Logs</h2>

      <div className="flex-1 bg-gray-900 rounded-lg border border-gray-700 p-4 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto font-mono text-sm text-green-400">
          {logs.length === 0 ? (
            <div className="text-gray-500">No logs yet...</div>
          ) : (
            logs.map((log, index) => (
              <div key={index} className="mb-1">
                {log}
              </div>
            ))
          )}
          <div ref={logsEndRef} />
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        Auto-scroll enabled • {logs.length} log entries
      </div>
    </div>
  );
}
