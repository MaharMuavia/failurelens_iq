import { useEffect, useState } from "react";
import { reasoningSteps } from "../data/mockData";
import { streamAnalysis } from "../api/client";

type VisibleStep = Record<string, any>;

export function useSSEStream(enabled: boolean, experimentId: string, fallbackMode: boolean) {
  const [visibleSteps, setVisibleSteps] = useState<VisibleStep[]>(reasoningSteps);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    if (fallbackMode) {
      setVisibleSteps(reasoningSteps);
      return;
    }

    setVisibleSteps([]);
    const source = streamAnalysis(experimentId);
    source.onmessage = (message) => {
      const event = JSON.parse(message.data);
      if (event.event === "agent_reasoning") {
        const step = event.data;
        setVisibleSteps((current) => [
          ...current,
          {
            agent: event.agent || "Agent",
            status: "completed",
            confidence: step.confidence ?? 0,
            finding: step.finding,
            evidence: (step.evidence || step.evidence_fields || []).map((item: any) =>
              typeof item === "string" ? item : item.field_path
            )
          }
        ]);
      }
      if (event.event === "pipeline_completed" || event.event === "pipeline_failed") {
        source.close();
      }
    };
    source.onerror = () => {
      source.close();
      setVisibleSteps(reasoningSteps);
    };

    return () => source.close();
  }, [enabled, experimentId, fallbackMode]);

  return visibleSteps;
}
