import { useState } from 'react'
import { Upload, Play, Download, ClosedCaption } from 'lucide-react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <header className="h-20 bg-gray-800 flex items-center justify-between px-6">
      {/* Upload button and caption button*/}
      <div className="flex space-x-20">
        <button className="flex flex-col items-center hover:text-blue-400">
          <Upload className="h-7 w-7" />
          <span className="text-xs">Import</span>
        </button>
        <button className="flex flex-col items-center hover:text-blue-400">
          <ClosedCaption className="h-7 w-7" />
          <span className="text-xs">Captions</span>
        </button>
      </div>

      {/* Editable title in center */}
      <div
        contentEditable
        suppressContentEditableWarning={true}
        className="text-white text-lg font-semibold text-center outline-none bg-gray-700 px-3 py-1 rounded inline-block"
      >
        Project Title
      </div>

      {/* Preview and export button */}
      <div className="flex space-x-20">
        <button className="flex flex-col items-center hover:text-blue-400">
          <Play className="h-7 w-7" />
          <span className="text-xs">Preview</span>
        </button>
        <button className="flex flex-col items-center hover:text-blue-400">
          <Download className="h-7 w-7" />
          <span className="text-xs">Export</span>
        </button>
      </div>
      </header>

      {/* Main Editor Area */}
      <main className="flex-1 flex flex-row bg-red-900">
        {/* Chat Prompting Area (10-15%) */}
        <section className="w-1/6 min-w-[180px] max-w-xs bg-red-800 flex flex-col p-2 border-r border-gray-700">
          <div className="flex flex-col flex-1 bg-red-400 rounded-lg shadow-lg justify-center min-h-0">
            <form className="flex w-full h-full">
              <input
                type="text"
                className="flex-1 min-w-0 rounded-xl bg-gray-700 text-white px-2 py-1 focus:outline-none"
                placeholder="Enter prompt..."
              />

            </form>
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 rounded-xl px-3 py-1 my-1 mx-1 text-white"
            >
              Generate !
            </button>
          </div>
        </section>
      
        {/* Video Player Display (rest of the space) */}
        <section className="flex-1 bg-gray-700 flex flex-col items-center justify-center">
          <h2 className="text-gray-200 text-lg mb-4">Editor Canvas</h2>
          {/* Placeholder for video player */}
          <div className="w-4/5 aspect-video bg-black rounded shadow-lg flex items-center justify-center">
            <span className="text-gray-500">[Video Player Here]</span>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
