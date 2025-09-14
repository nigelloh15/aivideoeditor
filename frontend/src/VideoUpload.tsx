import React, { useState, useRef, useImperativeHandle, forwardRef } from "react";

export interface UploadedFile {
  video_id: string;
  filename: string;
  path: string;
}

export interface VideoUploaderHandle {
  importVideos: () => void;
}

const VideoUploader = forwardRef<VideoUploaderHandle>((_, ref) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploaded, setUploaded] = useState<UploadedFile[] | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Expose method to parent
  useImperativeHandle(ref, () => ({
    importVideos: () => {
      fileInputRef.current?.click();
    },
  }));

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const files = Array.from(e.target.files);
    setError(null);
    setUploading(true);

    try {
      if (files.length === 0) return; // no file selected
      const formData = new FormData();
      formData.append("file", files[0]); // only first file, field name matches backend

      const res = await fetch("http://localhost:8000/upload-video", {
        method: "POST",
        body: formData, // browser sets Content-Type automatically
      });

      if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
      const data = await res.json();
      console.log("Uploaded file:", data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = ""; // reset input
    }
  };

  //FOR MULTIPLE FILE UPLOAD:

  //   try {
  //     const formData = new FormData();
  //     files.forEach((file) => formData.append("files", file)); // must match backend

  //     const res = await fetch("http://localhost:8000/upload-video", {
  //       method: "POST",
  //       body: formData,
  //     });

  //     if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`);

  //     const data = await res.json();
  //     setUploaded(data || []);
  //     console.log("Uploaded files:", data);
  //   } catch (err: any) {
  //     setError(err.message || String(err));
  //   } finally {
  //     setUploading(false);
  //     if (fileInputRef.current) fileInputRef.current.value = ""; // reset input
  //   }
  // };

  return (
    <div>
      {/* Hidden file input */}
      <input
        type="file"
        multiple
        accept="video/*"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />

      {/* Upload status / errors */}
      {uploading && <p>Uploading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* Uploaded files list */}
      {uploaded && uploaded.length > 0 && (
        <div>
          <h3>Uploaded</h3>
          <ul>
            {uploaded.map((item) => (
              <li key={item.video_id}>
                {item.filename} -{" "}
                <a href={`http://localhost:8000/video/${item.video_id}`} target="_blank" rel="noreferrer">
                  View
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
});

export default VideoUploader;
