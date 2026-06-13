export const VITE_VIDEO_DEMO_MODE = import.meta.env.VITE_VIDEO_DEMO_MODE;
export const VITE_DEMO_API_KEY = import.meta.env.VITE_DEMO_API_KEY;

export const videoDemoMode = VITE_VIDEO_DEMO_MODE === "true";
export const demoModeEnabled = videoDemoMode || import.meta.env.MODE === "development";
