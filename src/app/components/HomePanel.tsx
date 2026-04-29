import { Power } from 'lucide-react';
import { useState, useEffect } from 'react';

interface Status {
  running: boolean;
  strategy: string | null;
  pid: number | null;
  domain_count: number;
  autostart: boolean;
}

export function HomePanel() {
  const [status, setStatus] = useState<Status>({
    running: false,
    strategy: null,
    pid: null,
    domain_count: 0,
    autostart: false,
  });

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const togglePower = async () => {
    try {
      if (status.running) {
        await fetch('/api/stop', { method: 'POST' });
      } else {
        const strategy = status.strategy || 'ALT';
        await fetch('/api/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ strategy }),
        });
      }
      await fetchStatus();
    } catch (error) {
      console.error('Failed to toggle power:', error);
    }
  };

  return (
    <div className="p-8">
      <h2 className="mb-6">Home</h2>

      <div className="max-w-2xl">
        <div className="flex flex-col items-center mb-8 p-8 bg-white rounded-lg border border-gray-200">
          <button
            onClick={togglePower}
            className={`w-16 h-16 rounded-full flex items-center justify-center transition-all mb-4 ${
              status.running
                ? 'bg-[#534AB7] hover:bg-[#4239a0]'
                : 'bg-gray-300 hover:bg-gray-400'
            }`}
          >
            <Power className="w-8 h-8 text-white" />
          </button>

          <span
            className={`inline-flex px-3 py-1 rounded-full text-sm ${
              status.running
                ? 'bg-[#eaf3de] text-[#3B6D11]'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {status.running ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Current Strategy</div>
            <div className="text-gray-900">{status.strategy || 'None'}</div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Domain Count</div>
            <div className="text-gray-900">{status.domain_count} domains enabled</div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Process Status</div>
            <div className="text-gray-900">
              {status.running && status.pid ? `winws.exe running (PID: ${status.pid})` : 'Not running'}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Autostart</div>
            <div className="text-gray-900">{status.autostart ? 'Enabled' : 'Disabled'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
