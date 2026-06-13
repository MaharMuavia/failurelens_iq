import { useState, useEffect } from 'react';
import { listExperiments, runAnalysisWithOptions, Experiment } from '../api/client';

export function useAnalysis() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadExperiments = async () => {
    setLoading(true);
    try {
      const data = await listExperiments();
      setExperiments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load experiments');
    } finally {
      setLoading(false);
    }
  };

  const analyze = async (experimentId: string) => {
    setLoading(true);
    try {
      const res = await runAnalysisWithOptions(experimentId);
      return res;
    } catch (err: any) {
      setError(err.message || 'Analysis run failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExperiments();
  }, []);

  return {
    experiments,
    loading,
    error,
    refresh: loadExperiments,
    analyze
  };
}
