import { useState } from 'react';
import * as Progress from '@radix-ui/react-progress';

type TestStatus = 'untested' | 'works' | 'partial' | 'failed';

interface Strategy {
  name: string;
  status: TestStatus;
}

export function StrategiesPanel() {
  const [strategies, setStrategies] = useState<Strategy[]>([
    { name: 'ALT', status: 'untested' },
    { name: 'ALT2', status: 'untested' },
    { name: 'ALT3', status: 'works' },
    { name: 'ALT4', status: 'untested' },
    { name: 'ALT5', status: 'untested' },
    { name: 'ALT6', status: 'untested' },
    { name: 'ALT7', status: 'untested' },
    { name: 'ALT8', status: 'untested' },
    { name: 'ALT9', status: 'untested' },
    { name: 'ALT10', status: 'untested' },
    { name: 'ALT11', status: 'untested' },
    { name: 'FAKE TLS AUTO', status: 'partial' },
    { name: 'FAKE TLS AUTO ALT', status: 'untested' },
    { name: 'FAKE TLS AUTO ALT2', status: 'failed' },
    { name: 'FAKE TLS AUTO ALT3', status: 'untested' },
    { name: 'SIMPLE FAKE', status: 'untested' },
    { name: 'SIMPLE FAKE ALT', status: 'untested' },
    { name: 'SIMPLE FAKE ALT2', status: 'untested' },
    { name: 'general', status: 'untested' },
  ]);

  const [selectedDomains, setSelectedDomains] = useState<string[]>(['discord.com', 'youtube.com']);
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTest, setCurrentTest] = useState('');

  const domains = ['discord.com', 'youtube.com', 'faceit.com', 'instagram.com', 'twitch.tv', 'spotify.com'];

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

  const runTest = () => {
    setTesting(true);
    setProgress(0);
    setCurrentTest('ALT');

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setTesting(false);
          setCurrentTest('');
          return 100;
        }
        return prev + 5;
      });
    }, 200);
  };

  const strategyGroups = [
    { name: 'ALT', strategies: strategies.slice(0, 11) },
    { name: 'FAKE TLS AUTO', strategies: strategies.slice(11, 15) },
    { name: 'SIMPLE FAKE', strategies: strategies.slice(15, 18) },
    { name: 'General', strategies: strategies.slice(18) },
  ];

  return (
    <div className="p-8">
      <h2 className="mb-6">Strategies</h2>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 h-fit">
          <h3 className="mb-4">All Strategies</h3>

          <div className="space-y-6 max-h-[600px] overflow-y-auto pr-2">
            {strategyGroups.map((group) => (
              <div key={group.name}>
                <div className="text-sm text-gray-500 mb-2">{group.name}</div>
                <div className="space-y-1">
                  {group.strategies.map((strategy) => (
                    <div
                      key={strategy.name}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
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
                    className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                      selectedDomains.includes(domain)
                        ? 'bg-[#534AB7] text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
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
              {testing ? 'Testing...' : 'Run test for all 20 strategies'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
