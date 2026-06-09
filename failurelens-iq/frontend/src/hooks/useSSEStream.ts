import { useEffect, useState } from "react";
import { reasoningSteps } from "../data/mockData";

export function useSSEStream(enabled: boolean) {
  const [visibleSteps, setVisibleSteps] = useState<typeof reasoningSteps>(reasoningSteps);

  useEffect(() => {
    if (!enabled) {
      setVisibleSteps(reasoningSteps);
      return;
    }

    setVisibleSteps([]);
    reasoningSteps.forEach((step, index) => {
      window.setTimeout(() => {
        setVisibleSteps((current) => [...current, step]);
      }, 220 * (index + 1));
    });
  }, [enabled]);

  return visibleSteps;
}
