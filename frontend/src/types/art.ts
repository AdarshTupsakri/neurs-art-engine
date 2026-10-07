export type ArtMode = 'pixel' | 'sketch' | 'paint';

export interface StepLayer {
  stage: number;
  name: string;
  technique?: string;
  description: string;
  image_url: string;
  width: number;
  height: number;
  opacity?: number;
  visible?: boolean;
}

export interface TutorialSession {
  status: string;
  mode: string;
  total_steps: number;
  steps: StepLayer[];
}

export interface CanvasEditorProps {
  steps: StepLayer[];
  currentStepIndex: number;
  onionSkinning: boolean;
  onionOpacity: number;
  mode: ArtMode;
}
