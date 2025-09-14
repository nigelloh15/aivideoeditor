import React, { useState, useRef, useImperativeHandle, forwardRef } from "react";

export interface UploadedFile {
  video_id: string;
  filename: string;
  path: string;
}

export interface VideoUploaderHandle {
  importVideos: () => void;
}

interface Props {
  onUploadingChange?: (uploading: boolean) => void; // 🔹 callback to parent
}

const VideoUploader = forwardRef<VideoUploaderHandle, Props>(({ onUploadingChange }, ref) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploaded, setUploaded] = useState<UploadedFile[] | null>(null);

  useImperativeHandle(ref, () => ({
    importVideos: () => {
      fileInputRef.current?.click();
    },
  }));

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;

    const files = Array.from(e.target.files);
    onUploadingChange?.(true); // 🔹 tell parent to show spinner

    try {
      const formData = new FormData();
      formData.append("file", files[0]);

      const res = await fetch("http://localhost:8000/upload-video", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error(`Upload failed: ${res.status} ${res.statusText}`);
      const data = await res.json();
      console.log("Uploaded file:", data);
      setUploaded([data]);
    } catch (err) {
      console.error(err);
    } finally {
      onUploadingChange?.(false); // 🔹 turn spinner off
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div>
      <input
        type="file"
        multiple
        accept="video/*"
        ref={fileInputRef}
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
    </div>
  );
});

export default VideoUploader;
