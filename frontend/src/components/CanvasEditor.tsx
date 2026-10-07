import React, { useRef, useEffect, useState } from 'react';
import { StepLayer, ArtMode } from '../types/art';
import { Eye, EyeOff, ZoomIn, ZoomOut, RefreshCw, Layers } from 'lucide-react';

interface CanvasEditorProps {
  steps: StepLayer[];
  currentStepIndex: number;
  onionSkinning: boolean;
  onionOpacity: number;
  mode: ArtMode;
}

export const CanvasEditor: React.FC<CanvasEditorProps> = ({
  steps,
  currentStepIndex,
  onionSkinning,
  onionOpacity,
  mode
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [zoom, setZoom] = useState<number>(1.0);
  const [imagesLoaded, setImagesLoaded] = useState<Record<number, HTMLImageElement>>({});

  // Preload step layer images into HTMLImageElement instances
  useEffect(() => {
    const loaded: Record<number, HTMLImageElement> = {};
    let isMounted = true;

    steps.forEach((step, index) => {
      if (step.image_url) {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.src = step.image_url;
        img.onload = () => {
          if (isMounted) {
            loaded[index] = img;
            setImagesLoaded((prev) => ({ ...prev, [index]: img }));
          }
        };
      }
    });

    return () => {
      isMounted = false;
    };
  }, [steps]);

  // Main Canvas Compositing Engine
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas internal resolution based on current step or default 512x512
    const currentStep = steps[currentStepIndex];
    const width = currentStep?.width || 512;
    const height = currentStep?.height || 512;

    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }

    // Set rendering smoothing (Nearest neighbor for Pixel Art, Bilinear for Sketch/Paint)
    ctx.imageSmoothingEnabled = mode !== 'pixel';
    if (mode === 'pixel') {
      ctx.imageSmoothingQuality = 'low';
    }

    // Clear main canvas frame
    ctx.clearRect(0, 0, width, height);

    // 1. Draw Onion Skin (Ghosting previous step if enabled)
    if (onionSkinning && currentStepIndex > 0) {
      const prevImg = imagesLoaded[currentStepIndex - 1];
      if (prevImg) {
        ctx.save();
        ctx.globalAlpha = onionOpacity;
        ctx.drawImage(prevImg, 0, 0, width, height);
        ctx.restore();
      }
    }

    // 2. Draw Active Cumulative Stage Layer (Step 0 up to currentStepIndex)
    // Note: For cumulative modes (sketch & paint), rendering the current step image directly 
    // composites all previous stages cleanly.
    const activeImg = imagesLoaded[currentStepIndex];
    if (activeImg) {
      ctx.save();
      const layerOpacity = currentStep?.opacity !== undefined ? currentStep.opacity : 1.0;
      const isVisible = currentStep?.visible !== undefined ? currentStep.visible : true;

      if (isVisible) {
        ctx.globalAlpha = layerOpacity;
        ctx.drawImage(activeImg, 0, 0, width, height);
      }
      ctx.restore();
    } else {
      // Fallback placeholder during image load
      ctx.fillStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillRect(0, 0, width, height);
    }

  }, [steps, currentStepIndex, onionSkinning, onionOpacity, mode, imagesLoaded, zoom]);

  return (
    <div className="relative flex flex-col items-center justify-center w-full h-full min-h-[480px] p-6 rounded-2xl glass-panel border border-slate-800/80 overflow-hidden">
      {/* Top Toolbar overlay */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between z-10">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 backdrop-blur-md text-xs font-semibold text-slate-300">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>Stage {currentStepIndex + 1} of {steps.length || 5}</span>
          <span className="text-slate-500">|</span>
          <span className="capitalize text-cyan-400">{mode} Mode</span>
        </div>

        {/* Zoom controls */}
        <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-900/90 border border-slate-800 backdrop-blur-md">
          <button
            onClick={() => setZoom((z) => Math.max(0.5, z - 0.25))}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-slate-400 min-w-[40px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom((z) => Math.min(3.0, z + 0.25))}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom(1.0)}
            className="p-1.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors ml-1"
            title="Reset Zoom"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* HTML5 Canvas Viewport */}
      <div className="relative flex items-center justify-center w-full h-full overflow-auto canvas-checkerboard rounded-xl border border-slate-800 shadow-2xl p-4">
        <div
          style={{
            transform: `scale(${zoom})`,
            transformOrigin: 'center center',
            transition: 'transform 0.15s ease-out'
          }}
          className="relative shadow-2xl rounded-lg overflow-hidden"
        >
          <canvas
            ref={canvasRef}
            className="block max-w-full max-h-[500px] object-contain rounded-lg"
          />
        </div>
      </div>
    </div>
  );
};
