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
    const promptLower = (targetPrompt || '').toLowerCase();
    const isVehicle = ['car', 'vehicle', 'robot', 'helmet', 'ship', 'cyber', 'bike'].some(k => promptLower.includes(k));
    const isCreature = ['cat', 'dog', 'dragon', 'animal', 'lion', 'bird', 'creature'].some(k => promptLower.includes(k));
    const isLandscape = ['tree', 'mountain', 'landscape', 'castle', 'building', 'city', 'house'].some(k => promptLower.includes(k));
    const isHuman = ['human', 'face', 'portrait', 'person', 'figure', 'body', 'anatomy'].some(k => promptLower.includes(k));

    const createSvgDataUrl = (stage: number, title: string) => {
      // Choose SVG background based on target mode
      const bgFill = targetMode === 'sketch' ? '#faf8f5' : targetMode === 'pixel' ? 'none' : '#1c1917';
      const gridStroke = targetMode === 'sketch' ? '#e2e8f0' : targetMode === 'pixel' ? '#334155' : '#292524';
      const strokePrimary = targetMode === 'sketch' ? '#1e293b' : '#38bdf8';
      const strokeAccent = targetMode === 'sketch' ? '#0284c7' : '#c084fc';

      let stageContent = '';

      if (filePreview) {
        // Progressive Beginner Decomposition of Uploaded Reference Image
        stageContent = `
          <!-- Base Reference Image with Progressive Opacity and Contrast -->
          <image href="${filePreview}" x="32" y="32" width="448" height="448" preserveAspectRatio="xMidYMid slice" 
                 opacity="${stage === 1 ? 0.15 : stage === 2 ? 0.35 : stage === 3 ? 0.60 : stage === 4 ? 0.80 : 0.95}" 
                 filter="${stage === 1 ? 'grayscale(1) contrast(2.0)' : stage === 2 ? 'grayscale(1) contrast(1.5)' : 'none'}"/>

          <!-- STAGE 1: Proportional Scaffolding (Grid & Axis Guidelines) -->
          ${stage >= 1 ? `
            <rect x="32" y="32" width="448" height="448" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="6,6"/>
            <line x1="32" y1="256" x2="480" y2="256" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4"/>
            <line x1="256" y1="32" x2="256" y2="480" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4"/>
            <line x1="181" y1="32" x2="181" y2="480" stroke="#06b6d4" stroke-width="1" stroke-dasharray="2,4" opacity="0.6"/>
            <line x1="331" y1="32" x2="331" y2="480" stroke="#06b6d4" stroke-width="1" stroke-dasharray="2,4" opacity="0.6"/>
            <line x1="32" y1="181" x2="480" y2="181" stroke="#06b6d4" stroke-width="1" stroke-dasharray="2,4" opacity="0.6"/>
            <line x1="32" y1="331" x2="480" y2="331" stroke="#06b6d4" stroke-width="1" stroke-dasharray="2,4" opacity="0.6"/>
            <ellipse cx="256" cy="256" rx="160" ry="160" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="6,6"/>
          ` : ''}

          <!-- STAGE 2: Primary Outer Silhouette Block-In -->
          ${stage >= 2 ? `
            <rect x="36" y="36" width="440" height="440" fill="none" stroke="${strokePrimary}" stroke-width="3.5" rx="12"/>
            <path d="M 40 120 C 140 40, 370 40, 472 120 C 472 370, 370 472, 40 472 Z" fill="none" stroke="${strokePrimary}" stroke-width="3" stroke-dasharray="8,4"/>
          ` : ''}

          <!-- STAGE 3: Secondary Internal Seams & Feature Landmarks -->
          ${stage >= 3 ? `
            <line x1="60" y1="160" x2="452" y2="160" stroke="#3b82f6" stroke-width="2" stroke-dasharray="6,3"/>
            <line x1="60" y1="320" x2="452" y2="320" stroke="#3b82f6" stroke-width="2" stroke-dasharray="6,3"/>
            <path d="M 160 160 Q 256 220 352 160" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
            <path d="M 160 320 Q 256 370 352 320" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
          ` : ''}

          <!-- STAGE 4: Form Shading & 45-Degree Pencil Cross-Hatching -->
          ${stage >= 4 ? `
            <g stroke="${strokePrimary}" stroke-width="1.5" opacity="0.7">
              <line x1="60" y1="340" x2="120" y2="400"/><line x1="80" y1="340" x2="140" y2="400"/>
              <line x1="100" y1="340" x2="160" y2="400"/><line x1="350" y1="340" x2="410" y2="400"/>
              <line x1="370" y1="340" x2="430" y2="400"/><line x1="390" y1="340" x2="450" y2="400"/>
            </g>
          ` : ''}

          <!-- STAGE 5: Line Weight Accents & Fine Details -->
          ${stage >= 5 ? `
            <rect x="32" y="32" width="448" height="448" fill="none" stroke="${strokeAccent}" stroke-width="4.5" rx="8"/>
            <circle cx="256" cy="256" r="8" fill="${strokeAccent}"/>
          ` : ''}
        `;
      } else if (targetMode === 'pixel') {
        // Crisp Pixel Art Vectors
        stageContent = `
          ${stage >= 1 ? '<rect x="96" y="96" width="320" height="320" fill="none" stroke="#475569" stroke-width="4" stroke-dasharray="8,8"/>' : ''}
          ${stage >= 2 ? (isVehicle ? '<rect x="128" y="200" width="256" height="128" fill="#0284c7" rx="4"/>' : '<rect x="160" y="140" width="192" height="240" fill="#38bdf8" rx="4"/>') : ''}
          ${stage >= 3 ? (isVehicle ? '<rect x="176" y="160" width="160" height="64" fill="#38bdf8"/><circle cx="176" cy="328" r="32" fill="#0f172a"/><circle cx="336" cy="328" r="32" fill="#0f172a"/>' : '<rect x="192" y="180" width="48" height="48" fill="#f8fafc"/><rect x="272" y="180" width="48" height="48" fill="#f8fafc"/>') : ''}
          ${stage >= 4 ? '<path d="M 140 210 H 370 M 140 230 H 370" stroke="#bae6fd" stroke-width="3" stroke-dasharray="6,6"/>' : ''}
          ${stage >= 5 ? '<rect x="128" y="200" width="256" height="128" fill="none" stroke="#f0abfc" stroke-width="6"/>' : ''}
        `;
      } else if (isVehicle) {
        // Vehicle / Sci-Fi / Helmet Vector Scaffolding
        stageContent = `
          ${stage >= 1 ? '<polygon points="80,320 160,160 352,160 432,320" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/><ellipse cx="256" cy="340" rx="180" ry="40" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4"/>' : ''}
          ${stage >= 2 ? '<path d="M 90 310 Q 160 150 256 150 Q 352 150 422 310 Z" fill="none" stroke="' + strokePrimary + '" stroke-width="3.5"/>' : ''}
          ${stage >= 3 ? '<path d="M 140 220 Q 256 190 372 220" fill="none" stroke="#60a5fa" stroke-width="2.5"/><ellipse cx="160" cy="320" rx="30" ry="30" fill="none" stroke="#60a5fa" stroke-width="2.5"/><ellipse cx="352" cy="320" rx="30" ry="30" fill="none" stroke="#60a5fa" stroke-width="2.5"/>' : ''}
          ${stage >= 4 ? '<path d="M 160 230 L 220 280 M 180 230 L 240 280 M 200 230 L 260 280" stroke="#818cf8" stroke-width="2"/>' : ''}
          ${stage >= 5 ? '<circle cx="410" cy="290" r="12" fill="#f8fafc"/><path d="M 90 310 Q 256 130 422 310" fill="none" stroke="' + strokeAccent + '" stroke-width="4"/>' : ''}
        `;
      } else if (isCreature) {
        // Creature / Animal Vector Scaffolding
        stageContent = `
          ${stage >= 1 ? '<circle cx="180" cy="200" r="70" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/><circle cx="340" cy="260" r="90" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/><line x1="180" y1="200" x2="340" y2="260" stroke="#06b6d4" stroke-width="2" stroke-dasharray="4,4"/>' : ''}
          ${stage >= 2 ? '<path d="M 130 170 Q 220 120 340 170 Q 430 240 400 340 Q 280 370 160 310 Q 110 240 130 170 Z" fill="none" stroke="' + strokePrimary + '" stroke-width="3.5"/>' : ''}
          ${stage >= 3 ? '<polygon points="140,140 170,90 190,140" fill="none" stroke="#60a5fa" stroke-width="2.5"/><polygon points="200,140 230,90 250,140" fill="none" stroke="#60a5fa" stroke-width="2.5"/>' : ''}
          ${stage >= 4 ? '<path d="M 220 280 Q 280 320 340 280" fill="none" stroke="#818cf8" stroke-width="2.5"/>' : ''}
          ${stage >= 5 ? '<circle cx="170" cy="180" r="6" fill="#1e293b"/><circle cx="220" cy="180" r="6" fill="#1e293b"/><path d="M 130 170 Q 256 100 400 340" fill="none" stroke="' + strokeAccent + '" stroke-width="4"/>' : ''}
        `;
      } else if (isLandscape) {
        // Landscape / Architecture Scaffolding
        stageContent = `
          ${stage >= 1 ? '<line x1="0" y1="300" x2="512" y2="300" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/><polygon points="60,300 180,120 300,300" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/><polygon points="220,300 360,160 480,300" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/>' : ''}
          ${stage >= 2 ? '<path d="M 40 300 L 180 120 L 300 300 L 460 300 Z" fill="none" stroke="' + strokePrimary + '" stroke-width="3.5"/>' : ''}
          ${stage >= 3 ? '<circle cx="380" cy="110" r="40" fill="none" stroke="#60a5fa" stroke-width="2.5"/><path d="M 80 340 Q 256 380 432 340" fill="none" stroke="#60a5fa" stroke-width="2.5"/>' : ''}
          ${stage >= 4 ? '<path d="M 180 120 L 220 220 M 200 140 L 240 240 M 220 160 L 260 260" stroke="#818cf8" stroke-width="2"/>' : ''}
          ${stage >= 5 ? '<path d="M 40 300 L 180 120 L 300 300 L 460 300 Z" fill="none" stroke="' + strokeAccent + '" stroke-width="4"/>' : ''}
        `;
      } else {
        // Dynamic Human / Generic Anatomy Scaffolding
        stageContent = `
          ${stage >= 1 ? '<ellipse cx="256" cy="180" rx="80" ry="100" fill="none" stroke="#06b6d4" stroke-width="2" stroke-dasharray="6,6"/><line x1="256" y1="50" x2="256" y2="450" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4"/><line x1="100" y1="180" x2="412" y2="180" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4"/>' : ''}
          ${stage >= 2 ? '<path d="M 256 80 C 200 80, 160 130, 160 200 C 160 270, 190 340, 256 400 C 322 340, 352 270, 352 200 C 352 130, 312 80, 256 80 Z" fill="none" stroke="' + strokePrimary + '" stroke-width="3.5"/>' : ''}
          ${stage >= 3 ? '<path d="M 200 180 Q 256 150 312 180" fill="none" stroke="#60a5fa" stroke-width="2.5"/><path d="M 210 230 Q 256 270 302 230" fill="none" stroke="#60a5fa" stroke-width="2.5"/><path d="M 230 310 Q 256 335 282 310" fill="none" stroke="#60a5fa" stroke-width="2.5"/>' : ''}
          ${stage >= 4 ? '<path d="M 180 210 L 220 250 M 190 230 L 230 270 M 200 250 L 240 290" stroke="#818cf8" stroke-width="2"/>' : ''}
          ${stage >= 5 ? '<circle cx="225" cy="185" r="6" fill="' + strokePrimary + '"/><circle cx="287" cy="185" r="6" fill="' + strokePrimary + '"/><path d="M 256 75 C 190 75, 155 125, 155 200 C 155 275, 185 345, 256 405" fill="none" stroke="' + strokeAccent + '" stroke-width="4.5"/>' : ''}
        `;
      }

      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  ${bgFill !== 'none' ? `<rect width="512" height="512" fill="${bgFill}" rx="16"/>` : ''}
  <path d="M 64 0 V 512 M 128 0 V 512 M 192 0 V 512 M 256 0 V 512 M 320 0 V 512 M 384 0 V 512 M 448 0 V 512" stroke="${gridStroke}" stroke-width="0.75" opacity="0.6"/>
  <path d="M 0 64 H 512 M 0 128 H 512 M 0 192 H 512 M 0 256 H 512 M 0 320 H 512 M 0 384 H 512 M 0 448 H 512" stroke="${gridStroke}" stroke-width="0.75" opacity="0.6"/>
  ${stageContent}
  <rect x="20" y="456" width="220" height="36" rx="8" fill="#0f172a" stroke="#334155" opacity="0.9"/>
  <text x="32" y="479" fill="#38bdf8" font-family="sans-serif" font-size="13" font-weight="bold">Stage ${stage}: ${title}</text>
</svg>`;
      return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
    };

    const defaultDescriptions = [
      { name: 'Stage 1: Gesture & Scaffolding', technique: 'Scaffolding', desc: `Loose bounding boxes and grid lines for "${targetPrompt}".` },
      { name: 'Stage 2: Primary Contour', technique: 'Block-in', desc: 'Outer silhouette and primary volume block-in.' },
      { name: 'Stage 3: Plane Breaks & Seams', technique: 'Seams', desc: 'Secondary features and light/shadow plane break lines.' },
      { name: 'Stage 4: Value & Hatching', technique: 'Cross-hatch', desc: 'Planar shading and directional cross-hatching.' },
      { name: 'Stage 5: Line Weight Accents', technique: 'Fine Details', desc: 'Final line weight accents, specular highlights, and textures.' }
    ];

    const fallbackSteps: StepLayer[] = defaultDescriptions.map((d, i) => ({
      stage: i + 1,
      name: d.name,
      technique: d.technique,
      description: d.desc,
      image_url: createSvgDataUrl(i + 1, d.technique),
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
