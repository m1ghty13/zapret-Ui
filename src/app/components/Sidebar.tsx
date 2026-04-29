import { Home, Zap, Globe, FileText, Settings } from 'lucide-react';

interface SidebarProps {
  activePanel: string;
  onPanelChange: (panel: string) => void;
}

export function Sidebar({ activePanel, onPanelChange }: SidebarProps) {
  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'strategies', label: 'Strategies', icon: Zap },
    { id: 'domains', label: 'Domains', icon: Globe },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-[180px] bg-[#f5f5f5] border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-[#534AB7] font-semibold">Zapret UI</h1>
      </div>

      <nav className="flex-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePanel === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onPanelChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md mb-1 transition-colors ${
                isActive
                  ? 'bg-[#534AB7] text-white'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="text-sm">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
