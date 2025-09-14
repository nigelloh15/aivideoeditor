import { useRef, useState } from 'react';
import {
  Upload,
  Play,
  Download,
  ClosedCaption,
  Pause,
  Rewind,
  FastForward,
  Loader2
} from 'lucide-react';
import './App.css';
import VideoUploader from "./VideoUpload";
import type { VideoUploaderHandle } from "./VideoUpload";

function App() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isUploading, setIsUploading] = useState(false); // 🔹 controls spinner
  const uploaderRef = useRef<VideoUploaderHandle>(null);
  const videoContainerRef = useRef<HTMLDivElement | null>(null);

  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);

  const handlePreviewClick = () => {
    if (videoContainerRef.current) {
      if (videoContainerRef.current.requestFullscreen) {
        videoContainerRef.current.requestFullscreen();
      } else if ((videoContainerRef.current as any).webkitRequestFullscreen) {
        (videoContainerRef.current as any).webkitRequestFullscreen();
      } else if ((videoContainerRef.current as any).msRequestFullscreen) {
        (videoContainerRef.current as any).msRequestFullscreen();
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-700 text-white">
      {/* Header */}
      <header className="h-20 bg-gray-800 flex items-center justify-between px-6 animate-fadeIn">
        {/* Upload + captions */}
        <div className="flex space-x-5">
          <button
            disabled={isUploading}
            className={`flex flex-col items-center transition-transform duration-200 hover:scale-105 ${
              isUploading ? "text-blue-400 cursor-wait" : "hover:text-blue-400"
            }`}
            onClick={() => uploaderRef.current?.importVideos()}
          >
            {isUploading ? (
              <Loader2 className="h-7 w-7 animate-spin" />
            ) : (
              <Upload className="h-7 w-7" />
            )}
            <span className="text-xs">{isUploading ? "Uploading…" : "Import"}</span>
            <VideoUploader ref={uploaderRef} onUploadingChange={setIsUploading} />
          </button>

          <button className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-105">
            <ClosedCaption className="h-7 w-7" />
            <span className="text-xs">Captions</span>
          </button>
        </div>

        {/* Editable title */}
        <div
          contentEditable
          suppressContentEditableWarning
          onKeyDown={(e) => e.key === "Enter" && e.preventDefault()}
          className="text-white text-lg font-semibold text-center outline-none bg-gray-700 px-3 py-1 rounded inline-block whitespace-nowrap overflow-hidden"
        >
          Project Title
        </div>

        {/* Preview + Export */}
        <div className="flex space-x-6">
          <button
            className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-105"
            onClick={handlePreviewClick}
          >
            <Play className="h-7 w-7" />
            <span className="text-xs">Preview</span>
          </button>
          <button className="flex flex-col items-center hover:text-blue-400 transition-transform duration-200 hover:scale-105">
            <Download className="h-7 w-7" />
            <span className="text-xs">Export</span>
          </button>
        </div>
      </header>

      {/* Main editor */}
      <main className="flex-1 flex flex-row bg-gray-700">
        {/* Prompting */}
        <section className="w-1/6 min-w-[180px] max-w-xs bg-gray-700 flex flex-col p-2 border-r border-gray-700 my-5 mx-2">
          <div className="flex flex-col flex-1 rounded-lg justify-center h-1/2 animate-fadeIn-1">
            <form
              className="flex flex-col h-full"
              onSubmit={async (e) => {
                e.preventDefault();
                setIsGenerating(true);
                setProgress(0);

                for (let i = 1; i <= 100; i++) {
                  await new Promise((res) => setTimeout(res, 20));
                  setProgress(i);
                }

                await new Promise((res) => setTimeout(res, 300));
                setIsGenerating(false);
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
                className="flex-1 min-w-0 rounded-xl bg-gray-800 text-white px-5 py-5 focus:outline-none resize-none mb-2 min-h-[120px]"
                placeholder="Enter prompt..."
                rows={4}
              />
              <button
                type="submit"
                disabled={isGenerating}
                className={`bg-blue-600 hover:bg-blue-700 rounded-xl px-3 py-1 text-white transition-transform duration-200 hover:scale-105 ${
                  isGenerating ? "opacity-50 cursor-not-allowed" : ""
                }`}
              >
                {isGenerating ? "Generating..." : "Generate !"}
              </button>
            </form>
          </div>
        </section>

        {/* Video player */}
        <section className="flex-1 bg-gray-700 flex flex-col items-center justify-center">
          <div className="flex flex-row w-5/6 items-center justify-center animate-fadeIn-1">
            <div className="flex flex-col items-center justify-center bg-gray-800 rounded-lg py-6 px-3 mr-2 space-y-4 shadow">
              <button className="hover:text-blue-400 transition-transform duration-200 hover:scale-110">
                <Rewind className="h-8 w-8" strokeWidth={2} />
              </button>
              <button
                className="hover:text-blue-400 transition-transform duration-200 hover:scale-125"
                onClick={() => setIsPlaying((prev) => !prev)}
              >
                {isPlaying ? (
                  <Pause className="h-8 w-8" strokeWidth={2} />
                ) : (
                  <Play className="h-8 w-8" strokeWidth={2} />
                )}
              </button>
              <button className="hover:text-blue-400 transition-transform duration-200 hover:scale-110">
                <FastForward className="h-8 w-8" strokeWidth={2} />
              </button>
            </div>

            <div
              className="aspect-video bg-black rounded-xl shadow-lg flex-1 flex items-center justify-center min-w-[320px] max-w-[1920px]"
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
