"use client";

import { useState, useRef } from "react";
import Image from "next/image";

interface AnalysisResult {
  caption: string;
  summary: string;
  objects: string[];
  emotion: string;
  story: string;
}

export default function Home() {
  const [cameraReady, setCameraReady] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const [useCamera, setUseCamera] = useState(false);

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
    setError(null);
  };
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
        audio: false,
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setCameraReady(true);
        };
      }

      setUseCamera(true);
    } catch (err) {
      alert("Unable to access camera");
      console.error(err);
    }
  };

  const captureFromCamera = () => {
    if (!videoRef.current || !cameraReady) {
      alert("Camera not ready yet");
      return;
    }

    const video = videoRef.current;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0);

    canvas.toBlob((blob) => {
      if (!blob) return;

      const file = new File([blob], "camera.jpg", { type: "image/jpeg" });
      setFile(file);
      setPreview(URL.createObjectURL(blob));
      setUseCamera(false);
      setCameraReady(false);

      const stream = video.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
    }, "image/jpeg");
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("http://127.0.0.1:8000/analyze/", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-linear-to-br from-[#f4f8f6] via-[#fbfdfc] to-[#eef3f1] px-6 py-10">

      {/* Navbar */}
      <header className="w-full bg-emerald-100 border-b border-emerald-200 mb-12">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <span className="text-lg font-semibold text-emerald-700">
            VisionAI
          </span>
          <span className="text-sm text-emerald-700/70">
            Multimodal Image Understanding
          </span>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-3xl mx-auto text-center mb-14 pt-10">
        <span className="inline-block mb-4 rounded-full bg-emerald-100 px-4 py-1 text-sm text-emerald-700">
          Powered by intelligent vision
        </span>

        <h1 className="text-4xl font-serif font-semibold text-gray-900 mb-4">
          Understand Your Images
        </h1>

        <p className="text-gray-500 leading-relaxed">
          Upload or capture an image to receive a clear caption, a descriptive
          summary, detected elements, emotional tone, and a short story inspired
          by what you see.
        </p>
      </section>

      {/* Upload Card */}
      <section className="max-w-3xl mx-auto bg-white/80 backdrop-blur rounded-2xl border border-gray-100 shadow-sm p-8">
        <label className="flex flex-col items-center justify-center border-2 border-dashed border-emerald-200 rounded-xl p-10 cursor-pointer hover:bg-emerald-50 transition">
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          <div className="text-emerald-600 mb-2 text-3xl">📷</div>
          <p className="text-gray-600 font-medium">Drop an image here</p>
          <p className="text-sm text-gray-400 mt-1">or click to browse</p>
        </label>
        <div className="flex justify-center gap-4 mb-6">
          <div className="flex justify-center gap-4 mt-6 mb-6">
            <button
              onClick={startCamera}
              disabled={loading || file !== null}
              className="rounded-full border border-emerald-300 px-6 py-2 text-emerald-700 hover:bg-emerald-50 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Use Camera
            </button>
          </div>
        </div>

        {useCamera && (
          <div className="flex flex-col items-center gap-4 mt-6">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-64 rounded-xl border object-cover bg-black"
            />

            <button
              onClick={captureFromCamera}
              disabled={!cameraReady}
              className="rounded-full bg-emerald-600 px-6 py-2 text-white hover:bg-emerald-700 transition disabled:opacity-50"
            >
              Capture Photo
            </button>
          </div>
        )}

        {preview && (
          <div className="relative mt-6 h-64 w-full rounded-xl overflow-hidden border">
            <Image
              src={preview}
              alt="Preview"
              fill
              className="object-contain bg-white"
            />
          </div>
        )}

        <div className="mt-6 flex justify-center">
          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="rounded-full bg-emerald-600 px-8 py-3 text-white font-medium hover:bg-emerald-700 transition disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Analyze Image"}
          </button>
          {file && !loading && (
            <button
              onClick={() => {
                setFile(null);
                setPreview(null);
                setResult(null);
                setError(null);
              }}
              className="mt-4 text-sm text-gray-500 hover:text-emerald-600 transition"
            >
              Use another image
            </button>
          )}
        </div>

        {error && (
          <div className="mt-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
            {error}
          </div>
        )}
      </section>

      {/* Results */}
      {result && (
        <section className="max-w-4xl mx-auto mt-16 grid gap-6">
          <ResultCard title="Caption">{result.caption}</ResultCard>
          <ResultCard title="Summary">{result.summary}</ResultCard>
          <ResultCard title="Detected Elements">
            {result.objects.join(", ")}
          </ResultCard>
          <ResultCard title="Emotional Tone">{result.emotion}</ResultCard>
          <ResultCard title="Story">{result.story}</ResultCard>
        </section>
      )}
      <Footer />
    </main>
  );
}

function ResultCard({ title, children }: { title: string; children: string }) {
  return (
    <div className="rounded-2xl bg-white border border-gray-100 shadow-sm p-6">
      <h3 className="text-sm uppercase tracking-wide text-emerald-600 mb-2">
        {title}
      </h3>
      <p className="text-gray-700 whitespace-pre-line leading-relaxed">
        {children}
      </p>
    </div>
  );
}
function Footer() {
  return (
    <footer className="mt-24 border-t border-gray-200 bg-white/60 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="text-sm text-gray-500">
          © {new Date().getFullYear()} VisionAI. All rights reserved.
        </div>

        <div className="flex items-center gap-6 text-sm text-gray-500">
          <span className="hover:text-emerald-600 cursor-pointer transition">
            About
          </span>
          <span className="hover:text-emerald-600 cursor-pointer transition">
            How it works
          </span>
          <span className="hover:text-emerald-600 cursor-pointer transition">
            Privacy
          </span>
        </div>
      </div>
    </footer>
  );
}
