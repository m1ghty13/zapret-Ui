import { useState } from 'react';
import * as Switch from '@radix-ui/react-switch';

interface DomainGroup {
  name: string;
  enabled: boolean;
  domains: string[];
}

export function DomainsPanel() {
  const [groups, setGroups] = useState<DomainGroup[]>([
    {
      name: 'Discord',
      enabled: true,
      domains: ['discord.com', 'discordapp.com', 'discord.gg', 'discord.media'],
    },
    {
      name: 'YouTube',
      enabled: true,
      domains: ['youtube.com', 'youtu.be', 'googlevideo.com', 'ytimg.com'],
    },
    {
      name: 'Faceit',
      enabled: true,
      domains: ['faceit.com', 'faceit-cdn.net'],
    },
    {
      name: 'Instagram/Meta',
      enabled: false,
      domains: ['instagram.com', 'cdninstagram.com', 'facebook.com', 'fbcdn.net'],
    },
    {
      name: 'Twitter/X',
      enabled: false,
      domains: ['twitter.com', 'x.com', 'twimg.com'],
    },
    {
      name: 'Twitch',
      enabled: true,
      domains: ['twitch.tv', 'ttvnw.net', 'jtvnw.net'],
    },
    {
      name: 'Steam',
      enabled: false,
      domains: ['steampowered.com', 'steamcommunity.com', 'steamstatic.com'],
    },
    {
      name: 'Epic/Riot',
      enabled: false,
      domains: ['epicgames.com', 'riotgames.com', 'leagueoflegends.com'],
    },
    {
      name: 'Spotify',
      enabled: true,
      domains: ['spotify.com', 'scdn.co'],
    },
    {
      name: 'TikTok',
      enabled: false,
      domains: ['tiktok.com', 'tiktokcdn.com', 'musical.ly'],
    },
    {
      name: 'Telegram',
      enabled: false,
      domains: ['telegram.org', 't.me', 'telegram.me'],
    },
  ]);

  const toggleGroup = (index: number) => {
    setGroups(prev => {
      const updated = [...prev];
      updated[index] = { ...updated[index], enabled: !updated[index].enabled };
      return updated;
    });
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
            {groups.map((group, index) => (
              <div
                key={group.name}
                className="p-4 bg-gray-50 rounded-md border border-gray-200"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <Switch.Root
                      checked={group.enabled}
                      onCheckedChange={() => toggleGroup(index)}
                      className="w-11 h-6 bg-gray-300 data-[state=checked]:bg-[#534AB7] rounded-full relative transition-colors"
                    >
                      <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
                    </Switch.Root>
                    <span className="font-medium text-gray-900">{group.name}</span>
                  </div>
                  <span className="text-xs text-gray-500">{group.domains.length} domains</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {group.domains.map((domain) => (
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
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
