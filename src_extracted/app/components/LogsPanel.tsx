import { useEffect, useRef, useState } from 'react';

export function LogsPanel() {
  const [logs, setLogs] = useState<string[]>([
    '[2026-04-29 14:32:15] Starting winws.exe with strategy: ALT3',
    '[2026-04-29 14:32:15] Loading domain lists...',
    '[2026-04-29 14:32:15] Loaded 247 domains from lists/',
    '[2026-04-29 14:32:16] Applying strategy: --wf-tcp=80,443 --wf-udp=443,50000-50099',
    '[2026-04-29 14:32:16] Fake packets: --wssize 1:6 --wf-l3=ipv4,ipv6',
    '[2026-04-29 14:32:16] winws.exe process started (PID: 4832)',
    '[2026-04-29 14:32:16] Monitoring network traffic...',
    '[2026-04-29 14:32:20] TCP connection intercepted: discord.com:443',
    '[2026-04-29 14:32:20] Applying DPI bypass for discord.com',
    '[2026-04-29 14:32:21] TCP connection intercepted: youtube.com:443',
    '[2026-04-29 14:32:21] Applying DPI bypass for youtube.com',
    '[2026-04-29 14:32:25] TCP connection intercepted: faceit.com:443',
    '[2026-04-29 14:32:25] Applying DPI bypass for faceit.com',
  ]);

  const logsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div className="p-8 h-full flex flex-col">
      <h2 className="mb-6">Logs</h2>

      <div className="flex-1 bg-gray-900 rounded-lg border border-gray-700 p-4 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto font-mono text-sm text-green-400">
          {logs.map((log, index) => (
            <div key={index} className="mb-1">
              {log}
            </div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        Auto-scroll enabled • {logs.length} log entries
      </div>
    </div>
  );
}
