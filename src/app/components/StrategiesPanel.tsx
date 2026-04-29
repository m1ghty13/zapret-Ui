import { useState, useEffect } from 'react';
import * as Progress from '@radix-ui/react-progress';

type TestStatus = 'untested' | 'works' | 'partial' | 'failed';

interface Strategy {
  name: string;
  status: TestStatus;
  score: number;
  total: number;
  group: string;
}

export function StrategiesPanel() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedDomains, setSelectedDomains] = useState<string[]>(['discord.com', 'youtube.com']);
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTest, setCurrentTest] = useState('');

  const domains = ['discord.com', 'youtube.com', 'faceit.com', 'instagram.com', 'twitch.tv', 'spotify.com'];

  const fetchStrategies = async () => {
    try {
      const response = await fetch('/api/strategies');
      const data = await response.json();
      setStrategies(data);
    } catch (error) {
      console.error('Failed to fetch strategies:', error);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const getStatusColor = (status: TestStatus) => {
    switch (status) {
      case 'works':
        return 'bg-[#eaf3de] text-[#3B6D11]';
      case 'partial':
        return 'bg-orange-100 text-orange-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getStatusLabel = (status: TestStatus) => {
    switch (status) {
      case 'works':
        return 'Works';
      case 'partial':
        return 'Partial';
      case 'failed':
        return 'Failed';
      default:
        return 'Untested';
    }
  };

  const toggleDomain = (domain: string) => {
    setSelectedDomains(prev =>
      prev.includes(domain) ? prev.filter(d => d !== domain) : [...prev, domain]
    );
  };

  const selectStrategy = async (name: string) => {
    try {
      await fetch('/api/strategies/select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
    } catch (error) {
      console.error('Failed to select strategy:', error);
    }
  };

  const runTest = async () => {
    setTesting(true);
    setProgress(0);
    setCurrentTest('');

    try {
      // Start the test
      await fetch('/api/test/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domains: selectedDomains }),
      });

      // Listen to SSE events
      const eventSource = new EventSource('/api/test/events');

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'progress') {
          setCurrentTest(data.strategy);
          setProgress(data.percent);
        } else if (data.type === 'result') {
          // Update strategy status
          setStrategies(prev =>
            prev.map(s =>
              s.name === data.strategy
                ? { ...s, status: data.status, score: data.score, total: data.total }
                : s
            )
          );
        } else if (data.type === 'done') {
          setTesting(false);
          setCurrentTest('');
          setProgress(100);
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        setTesting(false);
        eventSource.close();
      };
    } catch (error) {
      console.error('Failed to run test:', error);
      setTesting(false);
    }
  };

  // Group strategies by their group field
  const strategyGroups = strategies.reduce((acc, strategy) => {
    const group = strategy.group || 'General';
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(strategy);
    return acc;
  }, {} as Record<string, Strategy[]>);

  const groupOrder = ['ALT', 'FAKE TLS AUTO', 'SIMPLE FAKE', 'General'];
  const sortedGroups = groupOrder
    .filter(name => strategyGroups[name])
    .map(name => ({ name, strategies: strategyGroups[name] }));

  return (
    <div className="p-8">
      <h2 className="mb-6">Strategies</h2>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 h-fit">
          <h3 className="mb-4">All Strategies</h3>

          <div className="space-y-6 max-h-[600px] overflow-y-auto pr-2">
            {sortedGroups.map((group) => (
              <div key={group.name}>
                <div className="text-sm text-gray-500 mb-2">{group.name}</div>
                <div className="space-y-1">
                  {group.strategies.map((strategy) => (
                    <div
                      key={strategy.name}
                      onClick={() => selectStrategy(strategy.name)}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
                    >
                      <span className="text-sm">{strategy.name}</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(strategy.status)}`}>
                        {getStatusLabel(strategy.status)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-6 h-fit">
          <h3 className="mb-4">Auto-test</h3>

          <div className="space-y-4">
            <div>
              <div className="text-sm text-gray-500 mb-2">Test Domains</div>
              <div className="flex flex-wrap gap-2">
                {domains.map((domain) => (
                  <button
                    key={domain}
                    onClick={() => toggleDomain(domain)}
                    disabled={testing}
                    className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                      selectedDomains.includes(domain)
                        ? 'bg-[#534AB7] text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    } ${testing ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    {domain}
                  </button>
                ))}
              </div>
            </div>

            {testing && (
              <>
                <div>
                  <div className="text-sm text-gray-500 mb-2">
                    Testing: {currentTest}
                  </div>
                  <Progress.Root className="relative overflow-hidden bg-gray-200 rounded-full w-full h-2">
                    <Progress.Indicator
                      className="bg-[#534AB7] w-full h-full transition-transform duration-300 ease-out"
                      style={{ transform: `translateX(-${100 - progress}%)` }}
                    />
                  </Progress.Root>
                  <div className="text-xs text-gray-500 mt-1">{progress}% complete</div>
                </div>

                <div className="text-sm text-gray-600">
                  Testing all strategies against selected domains...
                </div>
              </>
            )}

            <button
              onClick={runTest}
              disabled={testing || selectedDomains.length === 0}
              className="w-full bg-[#534AB7] hover:bg-[#4239a0] disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-4 py-2.5 rounded-md transition-colors"
            >
              {testing ? 'Testing...' : `Run test for all ${strategies.length} strategies`}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
