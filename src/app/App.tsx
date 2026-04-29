import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { HomePanel } from './components/HomePanel';
import { StrategiesPanel } from './components/StrategiesPanel';
import { DomainsPanel } from './components/DomainsPanel';
import { LogsPanel } from './components/LogsPanel';
import { SettingsPanel } from './components/SettingsPanel';

export default function App() {
  const [activePanel, setActivePanel] = useState('home');

  const renderPanel = () => {
    switch (activePanel) {
      case 'home':
        return <HomePanel />;
      case 'strategies':
        return <StrategiesPanel />;
      case 'domains':
        return <DomainsPanel />;
      case 'logs':
        return <LogsPanel />;
      case 'settings':
        return <SettingsPanel />;
      default:
        return <HomePanel />;
    }
  };

  return (
    <div className="size-full flex bg-white">
      <Sidebar activePanel={activePanel} onPanelChange={setActivePanel} />
      <main className="flex-1 overflow-auto bg-[#fafafa]">
        {renderPanel()}
      </main>
    </div>
  );
}