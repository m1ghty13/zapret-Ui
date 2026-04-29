import { useState, useEffect } from 'react';
import * as Switch from '@radix-ui/react-switch';

interface DomainGroup {
  name: string;
  enabled: boolean;
  domains: string[];
  count: number;
}

export function DomainsPanel() {
  const [groups, setGroups] = useState<DomainGroup[]>([]);

  const fetchDomains = async () => {
    try {
      const response = await fetch('/api/domains');
      const data = await response.json();
      setGroups(data);
    } catch (error) {
      console.error('Failed to fetch domains:', error);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  const toggleGroup = async (name: string) => {
    try {
      await fetch('/api/domains/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      await fetchDomains();
    } catch (error) {
      console.error('Failed to toggle domain group:', error);
    }
  };

  return (
    <div className="p-8">
      <h2 className="mb-6">Domains</h2>

      <div className="max-w-4xl">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <p className="text-sm text-gray-500 mb-6">
            Enable or disable domain groups to control which services use DPI bypass.
          </p>

          <div className="space-y-4">
            {groups.map((group) => (
              <div
                key={group.name}
                className="p-4 bg-gray-50 rounded-md border border-gray-200"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Switch.Root
                      checked={group.enabled}
                      onCheckedChange={() => toggleGroup(group.name)}
                      className="w-11 h-6 bg-gray-300 data-[state=checked]:bg-[#534AB7] rounded-full relative transition-colors"
                    >
                      <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
                    </Switch.Root>
                    <span className="font-medium text-gray-900">{group.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{group.count} domains</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {group.domains.slice(0, 10).map((domain) => (
                    <span
                      key={domain}
                      className={`text-xs px-2 py-1 rounded ${
                        group.enabled
                          ? 'bg-[#534AB7] text-white'
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {domain}
                    </span>
                  ))}
                  {group.domains.length > 10 && (
                    <span className="text-xs px-2 py-1 text-gray-500">
                      +{group.domains.length - 10} more
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
