import { useRef, useState } from 'react';
import { Upload, Play, Download, ClosedCaption, Pause, Rewind, FastForward } from 'lucide-react';
import './App.css';

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [isPlaying, setIsPlaying] = useState(false); // Add this line
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="h-20 bg-gray-800 flex items-center justify-between px-6">
        {/* Upload button and captions */}
        <div className="flex space-x-5">
          <button
            className="flex flex-col items-center hover:text-blue-400"
            onClick={handleUploadClick}
          >
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
          onKeyDown={(e) => {
            if (e.key === "Enter") {
            e.preventDefault(); // prevent new line
    }
  }}
  className="text-white text-lg font-semibold text-center outline-none bg-gray-700 px-3 py-1 rounded inline-block whitespace-nowrap overflow-hidden"
>
  Project Title
</div>

        {/* Preview and export buttons */}
        <div className="flex space-x-6">
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

      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFilesChange}
        style={{ display: 'none' }}
        multiple
      />

      {/* Main Editor Area */}
      <main className="flex-1 flex flex-row bg-gray-700">
        {/* Chat Prompting Area (10-15%) */}
        <section className="w-1/6 min-w-[180px] max-w-xs bg-gray-700 flex flex-col p-2 border-r border-gray-700 my-5 mx-2">
          <div className="flex flex-col flex-1 rounded-lg justify-center h-1/2">
            <form className="flex flex-col h-full">
              <textarea
                className="flex-1 min-w-0 rounded-xl bg-gray-800 text-white px-5 py-5 focus:outline-none resize-none mb-2 min-h-[120px]"
                placeholder="Enter prompt..."
                rows={4}
              />
              <button
                type="submit"
                className="bg-blue-600 hover:bg-blue-700 rounded-xl px-3 py-1 text-white"
              >
                Generate !
              </button>
            </form>
          </div>
        </section>
      
        {/* Video Player Display (rest of the space) */}
        <section className="flex-1 bg-gray-700 flex flex-col items-center justify-center">
          <div className="flex flex-row w-5/6 items-center justify-center">
            {/* Vertical Control Bar */}
            <div className="flex flex-col items-center justify-center bg-gray-800 rounded-lg py-6 px-3 mr-2 space-y-4 shadow">

              <button className="hover:text-blue-400">
                <Rewind className="h-8 w-8" strokeWidth={2} />
              </button>
              <button
                className="hover:text-blue-400"
                onClick={() => setIsPlaying((prev) => !prev)}
              >
                {isPlaying ? (
                  <Pause className="h-8 w-8" strokeWidth={2} />
                ) : (
                  <Play className="h-8 w-8" strokeWidth={2} />
                )}
              </button>
              <button className="hover:text-blue-400">
                <FastForward className="h-8 w-8" strokeWidth={2} />
              </button>
            </div>
            {/* Video Player */}
            <div className="aspect-video bg-black rounded-r-lg shadow-lg flex-1 flex items-center justify-center min-w-[320px] max-w-[1920px]">
              <span className="text-gray-500">[Video Player Here]</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
