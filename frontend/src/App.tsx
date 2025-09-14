import { useRef, useState, useEffect } from 'react';
import { Upload, Play, Download, ClosedCaption, Pause, Rewind, FastForward } from 'lucide-react';
import './App.css';

interface VideoItem {
  video_id: string;
  filename: string;
}

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [outputVideoUrl, setOutputVideoUrl] = useState<string>('');
  const [prompt, setPrompt] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const videoContainerRef = useRef<HTMLDivElement | null>(null);

  const handleUploadClick = () => fileInputRef.current?.click();

  const handleFilesChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length) {
      const selectedFiles = Array.from(e.target.files);
      setFiles(selectedFiles);

      for (const file of selectedFiles) {
        const formData = new FormData();
        formData.append('file', file);

        try {
          const res = await fetch('http://localhost:8000/upload-video', {
            method: 'POST',
            body: formData,
          });
          if (!res.ok) throw new Error(`Upload failed: ${file.name}`);
          console.log(`Uploaded: ${file.name}`);
        } catch (err) {
          console.error(err);
          alert(`Failed to upload ${file.name}`);
        }
      }

      fetchVideos();
    }
  };

  const fetchVideos = async () => {
    try {
      const res = await fetch('http://localhost:8000/list-videos');
      const data = await res.json();
      setVideos(data);
    } catch (err) {
      console.error(err);
      alert('Failed to fetch videos.');
    }
  };

  const analyzeVideo = async (videoId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/analyze-video/${videoId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: prompt || 'Make it watchable' }),
      });
      const data = await res.json();
      console.log('Instructions:', data.instructions);
      alert(`Video ${videoId} analyzed! Check console.`);
    } catch (err) {
      console.error(err);
      alert('Failed to analyze video.');
    }
  };

  const editVideos = async () => {
    if (!videos.length) {
      alert('No videos available to edit.');
      return;
    }

    try {
      const videoIds = videos.map((v) => v.video_id);
      const res = await fetch('http://localhost:8000/edit-video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_ids: videoIds, prompt: prompt || 'Make it watchable', add_captions: true }),
      });
      const data = await res.json();
      const videoUrl = `http://localhost:8000/${data.output_video}`;
      setOutputVideoUrl(videoUrl);
      alert('Videos edited and spliced successfully!');
    } catch (err) {
      console.error(err);
      alert('Failed to edit videos.');
    }
  };

  const handlePreviewClick = () => {
    if (videoContainerRef.current) {
      if (videoContainerRef.current.requestFullscreen) videoContainerRef.current.requestFullscreen();
      else if ((videoContainerRef.current as any).webkitRequestFullscreen) (videoContainerRef.current as any).webkitRequestFullscreen();
      else if ((videoContainerRef.current as any).msRequestFullscreen) (videoContainerRef.current as any).msRequestFullscreen();
    }
  };

  useEffect(() => {
    fetchVideos();
  }, []);

  return (
    <div className="flex flex-col h-screen bg-gray-700 text-white">
      {/* Header */}
      <header className="h-20 bg-gray-800 flex items-center justify-between px-6">
        <div className="flex space-x-5">
          <button onClick={handleUploadClick} className="flex flex-col items-center hover:text-blue-400">
            <Upload className="h-7 w-7" />
            <span className="text-xs">Import</span>
          </button>
          <button className="flex flex-col items-center hover:text-blue-400">
            <ClosedCaption className="h-7 w-7" />
            <span className="text-xs">Captions</span>
          </button>
        </div>

        <div
          contentEditable
          suppressContentEditableWarning
          className="text-white text-lg font-semibold text-center outline-none bg-gray-700 px-3 py-1 rounded"
        >
          Project Title
        </div>

        <div className="flex space-x-6">
          <button onClick={handlePreviewClick} className="flex flex-col items-center hover:text-blue-400">
            <Play className="h-7 w-7" />
            <span className="text-xs">Preview</span>
          </button>
          <button onClick={editVideos} className="flex flex-col items-center hover:text-blue-400">
            <Download className="h-7 w-7" />
            <span className="text-xs">Generate</span>
          </button>
        </div>
      </header>

      {/* Hidden file input */}
      <input type="file" ref={fileInputRef} style={{ display: 'none' }} onChange={handleFilesChange} multiple />

      <main className="flex-1 flex flex-row bg-gray-700 p-4">
        {/* Sidebar for prompt */}
        <section className="w-1/6 min-w-[180px] max-w-xs bg-gray-700 flex flex-col p-2 border-r border-gray-700">
          <textarea
            className="flex-1 min-w-0 rounded-xl bg-gray-800 text-white px-5 py-5 focus:outline-none resize-none mb-2 min-h-[120px]"
            placeholder="Enter prompt..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          <button onClick={editVideos} className="bg-blue-600 hover:bg-blue-700 rounded-xl px-3 py-1 text-white">
            Generate
          </button>
        </section>

        {/* Video Player & List */}
        <section className="flex-1 bg-gray-700 flex flex-col items-center justify-center">
          <div className="flex flex-row w-full items-start justify-center gap-6">
            {/* Video Player */}
            <div
              className="aspect-video bg-black rounded-xl shadow-lg flex-1 flex items-center justify-center min-w-[320px]"
              ref={videoContainerRef}
            >
              {outputVideoUrl ? (
                <video src={outputVideoUrl} controls className="w-full h-full rounded-xl" />
              ) : (
                <span className="text-gray-500">[Video Player Here]</span>
              )}
            </div>

            {/* Video List */}
            <div className="w-72 bg-gray-800 rounded-lg p-4 flex flex-col gap-2 max-h-[480px] overflow-y-auto">
              <h3 className="text-white text-lg mb-2">Available Videos</h3>
              {videos.length === 0 && <p className="text-gray-400">No videos found.</p>}
              {videos.map((v) => (
                <div key={v.video_id} className="flex justify-between items-center bg-gray-700 p-2 rounded">
                  <span className="truncate max-w-[150px]">{v.filename}</span>
                </div>
              ))}
            </div>
          </div>

          {outputVideoUrl && (
            <a href={outputVideoUrl} download="output.mp4" className="mt-3 text-blue-400 underline">
              Download Video
            </a>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
