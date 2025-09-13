import { useState } from 'react'
import { Upload, Scissors, Play, Download } from 'lucide-react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <aside className="w-20 bg-gray-800 flex flex-col justify-between p-4">
        <div className="space-y-4">
          <button className="flex flex-col items-center space-y-1 hover:text-blue-400">
            <Upload className="h-6 w-6" />
            <span className="text-xs">Import</span>
          </button>
          <button className="flex flex-col items-center space-y-1 hover:text-blue-400">
            <Scissors className="h-6 w-6" />
            <span className="text-xs">Cut</span>
          </button>
          <button className="flex flex-col items-center space-y-1 hover:text-blue-400">
            <Play className="h-6 w-6" />
            <span className="text-xs">Play</span>
          </button>
        </div>
        <div>
          <button className="flex flex-col items-center space-y-1 hover:text-blue-400">
            <Download className="h-6 w-6" />
            <span className="text-xs">Export</span>
          </button>
        </div>
      </aside>

      {/* Main Editor Area */}
      <main className="flex-1 flex flex-col">
        <div className="flex-1 bg-gray-700 flex items-center justify-center">
          <p className="text-gray-300">Editor Canvas</p>
        </div>

        {/* Timeline */}
        <div className="h-40 bg-gray-800 border-t border-gray-700 flex items-center justify-center">
          <p className="text-gray-400">Timeline Area</p>
        </div>
      </main>
    </div>
  )
}

export default App
