import { useState, useEffect } from 'react';
import * as Switch from '@radix-ui/react-switch';
import { FolderOpen } from 'lucide-react';

interface Settings {
  autostart: boolean;
  minimize_to_tray: boolean;
  auto_test: boolean;
  secure_dns: boolean;
  winws_path: string;
}

export function SettingsPanel() {
  const [settings, setSettings] = useState<Settings>({
    autostart: false,
    minimize_to_tray: true,
    auto_test: false,
    secure_dns: true,
    winws_path: 'bin/winws.exe',
  });

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch settings:', error);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  const updateSetting = async (key: string, value: any) => {
    try {
      await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key, value }),
      });
      setSettings(prev => ({ ...prev, [key]: value }));
    } catch (error) {
      console.error('Failed to update setting:', error);
    }
  };

  const browsePath = async () => {
    try {
      // Call pywebview bridge
      if (window.pywebview && window.pywebview.api) {
        const path = await window.pywebview.api.browse_file();
        if (path) {
          updateSetting('winws_path', path);
        }
      }
    } catch (error) {
      console.error('Failed to browse file:', error);
    }
  };

  return (
    <div className="p-8">
      <h2 className="mb-6">Settings</h2>

      <div className="max-w-2xl">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="space-y-6">
            <div className="flex items-center justify-between pb-6 border-b border-gray-200">
              <div>
                <div className="font-medium text-gray-900">Autostart with Windows</div>
                <div className="text-sm text-gray-500 mt-1">
                  Launch Zapret UI when Windows starts
                </div>
              </div>
              <Switch.Root
                checked={settings.autostart}
                onCheckedChange={(checked) => updateSetting('autostart', checked)}
                className="w-11 h-6 bg-gray-300 data-[state=checked]:bg-[#534AB7] rounded-full relative transition-colors"
              >
                <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
              </Switch.Root>
            </div>

            <div className="flex items-center justify-between pb-6 border-b border-gray-200">
              <div>
                <div className="font-medium text-gray-900">Minimize to tray on close</div>
                <div className="text-sm text-gray-500 mt-1">
                  Keep running in system tray when window is closed
                </div>
              </div>
              <Switch.Root
                checked={settings.minimize_to_tray}
                onCheckedChange={(checked) => updateSetting('minimize_to_tray', checked)}
                className="w-11 h-6 bg-gray-300 data-[state=checked]:bg-[#534AB7] rounded-full relative transition-colors"
              >
                <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
              </Switch.Root>
            </div>

            <div className="flex items-center justify-between pb-6 border-b border-gray-200">
              <div>
                <div className="font-medium text-gray-900">Auto-test on first launch</div>
                <div className="text-sm text-gray-500 mt-1">
                  Automatically test all strategies on first run
                </div>
              </div>
              <Switch.Root
                checked={settings.auto_test}
                onCheckedChange={(checked) => updateSetting('auto_test', checked)}
                className="w-11 h-6 bg-gray-300 data-[state=checked]:bg-[#534AB7] rounded-full relative transition-colors"
              >
                <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
              </Switch.Root>
            </div>

            <div className="flex items-center justify-between pb-6 border-b border-gray-200">
              <div>
                <div className="font-medium text-gray-900">Secure DNS (DoH)</div>
                <div className="text-sm text-gray-500 mt-1">
                  Use DNS-over-HTTPS for enhanced privacy
                </div>
              </div>
              <Switch.Root
                checked={settings.secure_dns}
                onCheckedChange={(checked) => updateSetting('secure_dns', checked)}
                className="w-11 h-6 bg-gray-300 data-[state=checked]:bg-[#534AB7] rounded-full relative transition-colors"
              >
                <Switch.Thumb className="block w-5 h-5 bg-white rounded-full transition-transform translate-x-0.5 data-[state=checked]:translate-x-[22px]" />
              </Switch.Root>
            </div>

            <div>
              <label className="block font-medium text-gray-900 mb-2">
                Path to winws.exe
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={settings.winws_path}
                  onChange={(e) => updateSetting('winws_path', e.target.value)}
                  className="flex-1 px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#534AB7] focus:border-transparent"
                />
                <button
                  onClick={browsePath}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors flex items-center gap-2"
                >
                  <FolderOpen className="w-4 h-4" />
                  Browse
                </button>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                Location of the winws.exe executable file
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
