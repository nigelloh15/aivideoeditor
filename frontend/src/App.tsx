import { useState } from 'react'
import { Upload, Play, Download,ClosedCaption } from 'lucide-react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <header className="h-16 bg-gray-800 flex items-center justify-between px-6">
      {/* Left group */}
      <div className="flex space-x-8">
        <button className="flex flex-col items-center hover:text-blue-400">
          <Upload className="h-5 w-5" />
          <span className="text-xs">Import</span>
        </button>
        <button className="flex flex-col items-center hover:text-blue-400">
          <ClosedCaption className="h-5 w-5" />
          <span className="text-xs">Captions</span>
        </button>
      </div>

      {/* Right group */}
      <div className="flex space-x-8">
        <button className="flex flex-col items-center hover:text-blue-400">
          <Play className="h-5 w-5" />
          <span className="text-xs">Play</span>
        </button>
        <button className="flex flex-col items-center hover:text-blue-400">
          <Download className="h-5 w-5" />
          <span className="text-xs">Export</span>
        </button>
      </div>
    </header>


      {/* Main Editor Area */}
      <main className="flex-1 flex flex-col">
        <div className="flex-1 bg-gray-700 flex items-center justify-center">
          <p className="text-gray-300">Editor Canvas</p>
        </div>

      </main>
    </div>
  )
}

export default App