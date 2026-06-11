export const VIDEO_DEMO_MODE = import.meta.env.VITE_VIDEO_DEMO_MODE === "true";

export function demoErrorMessage(message: string) {
  if (VIDEO_DEMO_MODE) {
    return "Demo-safe error hidden. Check the backend logs for details.";
  }
  return message;
}
