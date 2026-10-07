import React, { useState, useEffect } from 'react';
import { ArtMode, StepLayer } from './types/art';
import { ModeSelector } from './components/ModeSelector';
import { CanvasEditor } from './components/CanvasEditor';
import { StepReplay } from './components/StepReplay';
import { LayerPanel } from './components/LayerPanel';
import { Sparkles, Upload, Send, Loader2, Palette, Info, CheckCircle2 } from 'lucide-react';

export function App() {
  const [mode, setMode] = useState<ArtMode>('sketch');
  const [prompt, setPrompt] = useState<string>('Classic Human Anatomy');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [filePreview, setFilePreview] = useState<string | null>(null);
  
  const [steps, setSteps] = useState<StepLayer[]>([]);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [onionSkinning, setOnionSkinning] = useState<boolean>(true);
  const [onionOpacity, setOnionOpacity] = useState<number>(0.35);

  // Initial generation fetch
  useEffect(() => {
    fetchTutorialSteps(mode, prompt, selectedFile);
  }, []);

  const handleModeChange = (newMode: ArtMode) => {
    setMode(newMode);
    setCurrentStepIndex(0);
    fetchTutorialSteps(newMode, prompt, selectedFile);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setFilePreview(URL.createObjectURL(file));
    }
  };

  const handleGenerate = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    fetchTutorialSteps(mode, prompt, selectedFile);
  };

  const fetchTutorialSteps = async (
    targetMode: ArtMode,
    targetPrompt: string,
    file: File | null
  ) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      if (file) {
        formData.append('file', file);
      }
      if (targetPrompt) {
        formData.append('prompt', targetPrompt);
      }

      const endpoint = `/api/v1/generate/${targetMode}`;
      const res = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`API generation failed with status ${res.status}`);
      }

      const data = await res.json();
      if (data.status === 'success' && data.steps) {
        setSteps(data.steps);
        setCurrentStepIndex(0);
      } else {
        throw new Error(data.detail || 'Failed to generate tutorial steps');
      }
    } catch (err: any) {
      console.warn('API error, using client synthetic fallback', err);
      // Client fallback mock data generator if backend server isn't live
      generateFallbackSteps(targetMode, targetPrompt);
    } finally {
      setLoading(false);
    }
  };

  const generateFallbackSteps = (targetMode: ArtMode, targetPrompt: string) => {
    const defaultDescriptions = [
      { name: 'Stage 1: Gesture & Scaffolding', technique: 'Scaffolding', desc: 'Loose bounding boxes and perspective lines.' },
      { name: 'Stage 2: Primary Contour', technique: 'Block-in', desc: 'Outer silhouette superimposed over scaffolding.' },
      { name: 'Stage 3: Plane Breaks & Features', technique: 'Seams', desc: 'Secondary features and terminator lines.' },
      { name: 'Stage 4: Value & Hatching', technique: 'Cross-hatch', desc: 'Planar shading and directional hatching.' },
      { name: 'Stage 5: Line Weight Accents', technique: 'Fine Details', desc: 'Final dark accents and textures.' }
    ];

    const fallbackSteps: StepLayer[] = defaultDescriptions.map((d, i) => ({
      stage: i + 1,
      name: d.name,
      technique: d.technique,
      description: d.desc,
      image_url: '',
      width: 512,
      height: 512,
      opacity: 1.0,
      visible: true
    }));

    setSteps(fallbackSteps);
    setCurrentStepIndex(0);
  };

  const handleToggleLayerVisibility = (index: number) => {
    setSteps((prev) =>
      prev.map((step, i) =>
        i === index ? { ...step, visible: !(step.visible ?? true) } : step
      )
    );
  };

  const handleChangeLayerOpacity = (index: number, opacity: number) => {
    setSteps((prev) =>
      prev.map((step, i) => (i === index ? { ...step, opacity } : step))
    );
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 font-sans">
      {/* Header Bar */}
      <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-white">
              <Palette className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400">
                  NEURS ART ENGINE
                </h1>
                <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-cyan-950 text-cyan-400 border border-cyan-800/80 rounded-full">
                  v1.0.0-final
                </span>
              </div>
              <p className="text-xs text-slate-400">Teaching Anyone to Create Art, Step by Step</p>
            </div>
          </div>

          <ModeSelector
            currentMode={mode}
            onSelectMode={handleModeChange}
            disabled={loading}
          />
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col gap-6">
        {/* Prompt Input & Reference Image Uploader Bar */}
        <form onSubmit={handleGenerate} className="glass-panel p-4 rounded-2xl border border-slate-800 flex items-center gap-4 flex-wrap">
          <div className="flex-1 flex items-center gap-3 bg-slate-900/90 px-4 py-2.5 rounded-xl border border-slate-800">
            <Sparkles className="w-4 h-4 text-cyan-400 shrink-0" />
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to draw/paint (e.g. Cyberpunk Helmet, Renaissance Portrait)..."
              className="bg-transparent border-none outline-none text-sm text-slate-100 placeholder-slate-500 w-full"
            />
          </div>

          {/* Reference Image Upload Button */}
          <label className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 hover:bg-slate-800 cursor-pointer transition-colors text-xs font-semibold text-slate-300">
            <Upload className="w-4 h-4 text-cyan-400" />
            <span>{selectedFile ? selectedFile.name : 'Upload Reference'}</span>
            <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
          </label>

          {/* Generate Button */}
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/25 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Generating Steps...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Decompose Art</span>
              </>
            )}
          </button>
        </form>

        {/* Central Workspace Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
          {/* HTML5 Canvas Editor (3 cols) */}
          <div className="lg:col-span-3 flex flex-col gap-6">
            <CanvasEditor
              steps={steps}
              currentStepIndex={currentStepIndex}
              onionSkinning={onionSkinning}
              onionOpacity={onionOpacity}
              mode={mode}
            />

            {/* Interactive Timeline Scrub Bar */}
            <StepReplay
              steps={steps}
              currentStepIndex={currentStepIndex}
              onSelectStep={setCurrentStepIndex}
              onionSkinning={onionSkinning}
              onToggleOnion={() => setOnionSkinning(!onionSkinning)}
              onionOpacity={onionOpacity}
              onChangeOnionOpacity={setOnionOpacity}
            />
          </div>

          {/* Layer Panel (1 col) */}
          <div className="lg:col-span-1 h-full min-h-[500px]">
            <LayerPanel
              steps={steps}
              currentStepIndex={currentStepIndex}
              onSelectStep={setCurrentStepIndex}
              onToggleLayerVisibility={handleToggleLayerVisibility}
              onChangeLayerOpacity={handleChangeLayerOpacity}
            />
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 px-6 text-center text-xs text-slate-500">
        NEURS Art Engine | Developed at Woxsen University under Prof. Geeta Tripathi by Akhil Uppula, Akshay Jai, Trilochan Singh & Adarsh Tupsakri
      </footer>
    </div>
  );
}
