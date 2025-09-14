import { useRef, useState } from 'react';
import { Upload, Play, Download, ClosedCaption, Pause, Rewind, FastForward } from 'lucide-react';
import './App.css';

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoContainerRef = useRef<HTMLDivElement | null>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isLocked, setIsLocked] = useState(false); // NEW: lock after first generate

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handlePreviewClick = () => {
    if (videoContainerRef.current) {
      if (videoContainerRef.current.requestFullscreen) {
        videoContainerRef.current.requestFullscreen();
      } else if ((videoContainerRef.current as any).webkitRequestFullscreen) {
        (videoContainerRef.current as any).webkitRequestFullscreen(); // Safari
      } else if ((videoContainerRef.current as any).msRequestFullscreen) {
        (videoContainerRef.current as any).msRequestFullscreen(); // IE/Edge
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-700 text-white">
      {/* Header */}
      <header className="h-20 bg-gray-800 flex items-center justify-between px-6 animate-fadeIn">
        {/* Upload button and captions */}
        <div className="flex space-x-5">
          <button
            className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-102"
            onClick={handleUploadClick}
          >
            <Upload className="h-7 w-7" />
            <span className="text-xs">Import</span>
          </button>
          <button className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-102">
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
          <button
            className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-102"
            onClick={handlePreviewClick}
          >
            <Play className="h-7 w-7" />
            <span className="text-xs">Preview</span>
          </button>
          <button className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-102">
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
        {/* Chat Prompting Area */}
        <section className="w-1/6 min-w-[180px] max-w-xs bg-gray-700 flex flex-col p-2 border-r border-gray-700 my-5 mx-2">
          <div className="flex flex-col flex-1 rounded-lg justify-center h-1/2 animate-fadeIn-1">
            <form
              className="flex flex-col h-full"
              onSubmit={async (e) => {
                e.preventDefault();
                setIsGenerating(true);
                setProgress(0);

                // Simulate progress
                for (let i = 1; i <= 100; i++) {
                  await new Promise((res) => setTimeout(res, 20));
                  setProgress(i);
                }

                await new Promise((res) => setTimeout(res, 300));
                setIsGenerating(false);
                setIsLocked(true); // lock permanently after first generate
              }}
            >
              {isGenerating && (
                <div className="w-full h-3 bg-gray-600 rounded mb-3 overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
              <textarea
                className="flex-1 min-w-0 rounded-xl bg-gray-800 text-white px-5 py-5 focus:outline-none resize-none mb-2 min-h-[120px] transition-shadow duration-300"
                placeholder="What would you like to create?"
                rows={4}
                disabled={isLocked || isGenerating} // disable when generating OR after finished once
                style={{
                  backgroundColor: (isLocked || isGenerating) ? "#4B5563" : undefined,
                  cursor: (isLocked || isGenerating) ? "not-allowed" : undefined,
                  opacity: (isLocked || isGenerating) ? 0.7 : 1,
                }}
              />
              <button
                type="submit"
                disabled={isGenerating}
                className={`bg-blue-600 hover:bg-blue-700 rounded-xl px-3 py-1 text-white transition-transform duration-200 hover:scale-102 focus:shadow-[0_0_0_3px_rgba(59,130,246,0.4)] outline-none button-pulse ${isGenerating ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {isGenerating ? "Generating..." : "Generate !"}
              </button>
            </form>
          </div>
        </section>

        {/* Video Player Display */}
        <section className="flex-1 bg-gray-700 flex flex-col items-center justify-center">
          <div className="flex flex-row w-5/6 items-center justify-center animate-fadeIn-1">
            {/* Vertical Control Bar */}
            <div className="flex flex-col items-center justify-center bg-gray-800 rounded-lg py-6 px-3 mr-2 space-y-4 shadow">
              <button className="hover:text-blue-400 transition-transform duration-200 hover:scale-110">
                <Rewind className="h-8 w-8" strokeWidth={2} />
              </button>
              <button
                className="hover:text-blue-400 transition-transform duration-200 hover:scale-125 group"
                onClick={() => setIsPlaying((prev) => !prev)}
              >
                {isPlaying ? (
                  <Pause className="h-8 w-8" strokeWidth={2} />
                ) : (
                  <Play className="h-8 w-8 group-hover:animate-spin" strokeWidth={2} />
                )}
              </button>
              <button className="hover:text-blue-400 transition-transform duration-200 hover:scale-110">
                <FastForward className="h-8 w-8" strokeWidth={2} />
              </button>
            </div>
            {/* Video Player */}
            <div
              className="aspect-video bg-black rounded-xl shadow-lg flex-1 flex items-center justify-center min-w-[320px] max-w-[1920px] pulse-shadow transition-shadow"
              ref={videoContainerRef}
            >
              <span className="text-gray-500">[Video Player Here]</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
