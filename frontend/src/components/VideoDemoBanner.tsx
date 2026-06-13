import { CheckCircle2 } from "lucide-react";

export function VideoDemoBanner() {
  return (
    <section className="video-demo-banner" role="status">
      <CheckCircle2 size={18} />
      <strong>FailureLens IQ · Microsoft Agents League · Reasoning Agents Track</strong>
      <span>Video demo mode: EXP-1001, deterministic fallback-safe flow</span>
    </section>
  );
}
