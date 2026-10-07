import React, { useEffect, useState } from 'react';
import { StepLayer } from '../types/art';
import { Play, Pause, SkipBack, SkipForward, Eye, Sliders, Sparkles } from 'lucide-react';

interface StepReplayProps {
  steps: StepLayer[];
  currentStepIndex: number;
  onSelectStep: (index: number) => void;
  onionSkinning: boolean;
  onToggleOnion: () => void;
  onionOpacity: number;
  onChangeOnionOpacity: (opacity: number) => void;
}

export const StepReplay: React.FC<StepReplayProps> = ({
  steps,
  currentStepIndex,
  onSelectStep,
  onionSkinning,
  onToggleOnion,
  onionOpacity,
  onChangeOnionOpacity
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const currentStep = steps[currentStepIndex];

  // Auto-replay interval timer
  useEffect(() => {
    let timer: any;
    if (isPlaying) {
      timer = setInterval(() => {
        onSelectStep((currentStepIndex + 1) % (steps.length || 5));
      }, 2000);
    }
    return () => clearInterval(timer);
  }, [isPlaying, steps.length, currentStepIndex, onSelectStep]);

  return (
    <div className="w-full flex flex-col gap-4 p-5 rounded-2xl glass-panel border border-slate-800">
      {/* Header controls & step technique display */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-100">
                Step {currentStepIndex + 1}: {currentStep?.name || `Stage ${currentStepIndex + 1}`}
              </h3>
              {currentStep?.technique && (
                <span className="text-[11px] font-semibold uppercase tracking-wider text-cyan-400 bg-cyan-950/80 border border-cyan-800/60 px-2 py-0.5 rounded-full">
                  {currentStep.technique}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5 max-w-2xl">
              {currentStep?.description || 'Scrub through the construction steps to study the visual build order.'}
            </p>
          </div>
        </div>

        {/* Onion skinning toggles */}
        <div className="flex items-center gap-3 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800">
          <button
            onClick={onToggleOnion}
            className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-lg transition-all ${
              onionSkinning
                ? 'bg-cyan-500 text-white shadow-sm shadow-cyan-500/20'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>Ghost Prev Step</span>
          </button>

          {onionSkinning && (
            <div className="flex items-center gap-2">
              <Sliders className="w-3 h-3 text-slate-400" />
              <input
                type="range"
                min="0.1"
                max="0.8"
                step="0.05"
                value={onionOpacity}
                onChange={(e) => onChangeOnionOpacity(parseFloat(e.target.value))}
                className="w-20 accent-cyan-400 h-1 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                title="Ghost Opacity"
              />
              <span className="text-[10px] font-mono text-slate-400">{Math.round(onionOpacity * 100)}%</span>
            </div>
          )}
        </div>
      </div>

      {/* Interactive Timeline Scrub Bar */}
      <div className="flex items-center gap-4">
        {/* Playback action buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => {
              setIsPlaying(false);
              onSelectStep(Math.max(0, currentStepIndex - 1));
            }}
            disabled={currentStepIndex === 0}
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Previous Step"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-white shadow-md shadow-cyan-500/20 transition-all scale-[1.02]"
            title={isPlaying ? 'Pause Auto Replay' : 'Play Step Replay'}
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-white" />}
          </button>

          <button
            onClick={() => {
              setIsPlaying(false);
              onSelectStep(Math.min((steps.length || 5) - 1, currentStepIndex + 1));
            }}
            disabled={currentStepIndex === (steps.length || 5) - 1}
            className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            title="Next Step"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {/* Step dots & scrub track */}
        <div className="flex-1 flex items-center gap-2">
          {steps.map((step, idx) => {
            const isActive = idx === currentStepIndex;
            const isCompleted = idx < currentStepIndex;
            return (
              <button
                key={idx}
                onClick={() => {
                  setIsPlaying(false);
                  onSelectStep(idx);
                }}
                className={`relative flex-1 group flex flex-col items-center gap-1.5 py-2 px-1 rounded-xl transition-all ${
                  isActive
                    ? 'bg-slate-800/90 border border-cyan-500/50 shadow-lg shadow-cyan-500/10'
                    : 'hover:bg-slate-900/60'
                }`}
              >
                {/* Step indicator bar */}
                <div
                  className={`w-full h-2 rounded-full transition-all duration-300 ${
                    isActive
                      ? 'bg-gradient-to-r from-cyan-400 to-blue-500 scale-y-125'
                      : isCompleted
                      ? 'bg-cyan-900/80'
                      : 'bg-slate-800'
                  }`}
                />

                <span className={`text-[11px] font-semibold ${isActive ? 'text-cyan-300' : 'text-slate-400'}`}>
                  Stage {idx + 1}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};
