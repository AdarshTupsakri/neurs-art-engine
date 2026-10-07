import React from 'react';
import { ArtMode } from '../types/art';
import { Grid, PenTool, Palette } from 'lucide-react';

interface ModeSelectorProps {
  currentMode: ArtMode;
  onSelectMode: (mode: ArtMode) => void;
  disabled?: boolean;
}

export const ModeSelector: React.FC<ModeSelectorProps> = ({
  currentMode,
  onSelectMode,
  disabled = false
}) => {
  const modes: { id: ArtMode; label: string; icon: React.ReactNode; badge: string; color: string }[] = [
    {
      id: 'pixel',
      label: 'Pixel Art',
      icon: <Grid className="w-4 h-4" />,
      badge: 'Sprite Slicing',
      color: 'from-emerald-500 to-teal-600'
    },
    {
      id: 'sketch',
      label: 'Sketching',
      icon: <PenTool className="w-4 h-4" />,
      badge: 'Cumulative Scaffolding',
      color: 'from-cyan-500 to-blue-600'
    },
    {
      id: 'paint',
      label: 'Painting',
      icon: <Palette className="w-4 h-4" />,
      badge: 'Value & Atelier Layers',
      color: 'from-amber-500 to-rose-600'
    }
  ];

  return (
    <div className="flex items-center gap-2 p-1.5 rounded-xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
      {modes.map((m) => {
        const isActive = currentMode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => onSelectMode(m.id)}
            disabled={disabled}
            className={`flex items-center gap-2.5 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
              isActive
                ? `bg-gradient-to-r ${m.color} text-white shadow-lg shadow-cyan-500/20 scale-[1.02]`
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {m.icon}
            <span>{m.label}</span>
            <span
              className={`text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded-full ${
                isActive ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'
              }`}
            >
              {m.badge}
            </span>
          </button>
        );
      })}
    </div>
  );
};
