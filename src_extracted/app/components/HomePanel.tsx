import { Power } from 'lucide-react';
import { useState } from 'react';

export function HomePanel() {
  const [isActive, setIsActive] = useState(false);

  return (
    <div className="p-8">
      <h2 className="mb-6">Home</h2>

      <div className="max-w-2xl">
        <div className="flex flex-col items-center mb-8 p-8 bg-white rounded-lg border border-gray-200">
          <button
            onClick={() => setIsActive(!isActive)}
            className={`w-16 h-16 rounded-full flex items-center justify-center transition-all mb-4 ${
              isActive
                ? 'bg-[#534AB7] hover:bg-[#4239a0]'
                : 'bg-gray-300 hover:bg-gray-400'
            }`}
          >
            <Power className="w-8 h-8 text-white" />
          </button>

          <span
            className={`inline-flex px-3 py-1 rounded-full text-sm ${
              isActive
                ? 'bg-[#eaf3de] text-[#3B6D11]'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {isActive ? 'Active' : 'Inactive'}
          </span>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Current Strategy</div>
            <div className="text-gray-900">{isActive ? 'ALT3' : 'None'}</div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Domain Count</div>
            <div className="text-gray-900">247 domains enabled</div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Process Status</div>
            <div className="text-gray-900">
              {isActive ? 'winws.exe running (PID: 4832)' : 'Not running'}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="text-sm text-gray-500 mb-1">Autostart</div>
            <div className="text-gray-900">Enabled</div>
          </div>
        </div>
      </div>
    </div>
  );
}
