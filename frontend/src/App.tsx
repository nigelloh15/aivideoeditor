import { useRef, useState } from 'react';
import { Upload, Play, Download, ClosedCaption } from 'lucide-react';
import './App.css';
import { useRef, useState } from 'react';
import { Upload, Play, Download, ClosedCaption } from 'lucide-react';
import './App.css';

function App() {
  const [files, setFiles] = useState<File[]>([]);
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
      {/* Header */}
      <header className="h-20 bg-gray-800 flex items-center justify-between px-6">
        {/* Upload button and captions */}
        <div className="flex space-x-10">
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
        {/* Upload button and captions */}
        <div className="flex space-x-10">
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
        <div className="flex space-x-10">
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
        {/* Preview and export buttons */}
        <div className="flex space-x-10">
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
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFilesChange}
        style={{ display: 'none' }}
        multiple
      />

      {/* Main Editor Area */}
      <main className="flex-1 flex flex-row bg-red-900">
        {/* Chat Prompting Area */}
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

        {/* Video Player Display / Editor */}
        <section className="flex-1 bg-gray-700 flex flex-col items-center justify-center space-y-4 p-4">
          {/* Placeholder for video player */}
          <div className="w-4/5 aspect-video bg-black rounded shadow-lg flex items-center justify-center">
            <span className="text-gray-500">[Video Player Here]</span>
          </div>

          {/* Display uploaded files */}
          {files.length > 0 && (
            <div className="w-4/5 bg-gray-800 rounded p-2 text-white">
              <h3 className="font-semibold mb-2">Uploaded Files:</h3>
              <ul className="list-disc list-inside">
                {files.map((file, index) => (
                  <li key={index}>{file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
