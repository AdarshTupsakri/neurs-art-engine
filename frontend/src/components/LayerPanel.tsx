import React from 'react';
import { StepLayer } from '../types/art';
import { Layers, Eye, EyeOff, Sliders, CheckCircle2 } from 'lucide-react';

interface LayerPanelProps {
  steps: StepLayer[];
  currentStepIndex: number;
  onSelectStep: (index: number) => void;
  onToggleLayerVisibility?: (index: number) => void;
  onChangeLayerOpacity?: (index: number, opacity: number) => void;
}

export const LayerPanel: React.FC<LayerPanelProps> = ({
  steps,
  currentStepIndex,
  onSelectStep,
  onToggleLayerVisibility,
  onChangeLayerOpacity
}) => {
  return (
    <div className="flex flex-col w-full h-full p-4 rounded-2xl glass-panel border border-slate-800">
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800">
        <div className="flex items-center gap-2 text-slate-200">
          <Layers className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold tracking-wide uppercase">Layer Breakdown</h3>
        </div>
        <span className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded-md">
          {steps.length} Stages
        </span>
      </div>

      <div className="flex flex-col gap-2 overflow-y-auto max-h-[460px] pr-1">
        {steps.map((step, idx) => {
          const isActive = idx === currentStepIndex;
          const isVisible = step.visible !== undefined ? step.visible : true;
          const opacity = step.opacity !== undefined ? step.opacity : 1.0;

          return (
            <div
              key={idx}
              onClick={() => onSelectStep(idx)}
              className={`flex flex-col p-3 rounded-xl border transition-all cursor-pointer ${
                isActive
                  ? 'bg-slate-800/90 border-cyan-500/60 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-900/40 border-slate-800/60 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  {/* Layer thumbnail preview */}
                  <div className="w-10 h-10 rounded-lg canvas-checkerboard border border-slate-700/80 overflow-hidden flex items-center justify-center shrink-0">
                    {step.image_url ? (
                      <img src={step.image_url} alt={step.name} className="w-full h-full object-contain" />
                    ) : (
                      <span className="text-[10px] text-slate-500">{idx + 1}</span>
                    )}
                  </div>

                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-bold text-slate-200">Stage {idx + 1}</span>
                      {isActive && (
                        <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400/20" />
                      )}
                    </div>
                    <p className="text-[11px] text-slate-400 truncate max-w-[140px]">{step.name}</p>
                  </div>
                </div>

                {/* Layer visibility & controls */}
                <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => onToggleLayerVisibility && onToggleLayerVisibility(idx)}
                    className={`p-1.5 rounded-lg transition-colors ${
                      isVisible ? 'text-slate-300 hover:bg-slate-800' : 'text-slate-600 hover:bg-slate-800'
                    }`}
                    title={isVisible ? 'Hide Layer' : 'Show Layer'}
                  >
                    {isVisible ? <Eye className="w-4 h-4 text-cyan-400" /> : <EyeOff className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Opacity slider for active step */}
              {isActive && onChangeLayerOpacity && (
                <div className="flex items-center gap-2 mt-2 pt-2 border-t border-slate-800/80" onClick={(e) => e.stopPropagation()}>
                  <Sliders className="w-3 h-3 text-slate-400" />
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={opacity}
                    onChange={(e) => onChangeLayerOpacity(idx, parseFloat(e.target.value))}
                    className="w-full accent-cyan-400 h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="text-[10px] font-mono text-slate-400 min-w-[28px]">
                    {Math.round(opacity * 100)}%
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
