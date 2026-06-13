import React, { useState } from "react";
import { Sparkles, Loader2, AlertCircle } from "lucide-react";

interface PromptAnalysisPanelProps {
  onGenerate: (prompt: string) => void;
  isGenerating: boolean;
  error: string | null;
}

const SAMPLE_PROMPTS = [
  { label: "High accuracy but low minority F1", text: "Analyze a churn model that reached 93% accuracy but minority F1 dropped to 0.14. Find the root cause, retrieve evidence, recommend remediation, and map it to Microsoft certification skills." },
  { label: "Data leakage in customer churn model", text: "Customer churn XGBoost model has 98% accuracy on training, but validation drops to 60%. A column called post_churn_activity was included. Find root cause and remediation." },
  { label: "Overfitting random forest", text: "Overfitting random forest model on loan risk assessment. Training accuracy is 99% but test validation is 55% due to deep max_depth of 30. Suggest regularization fixes." },
  { label: "Data drift after deployment", text: "Data drift detected after deploying loan risk model. Feature distribution for average income changed by 35% in production validation logs. Root cause and playbooks needed." },
  { label: "Fairness risk in loan model", text: "Fairness risk in loan risk model: subgroup accuracy disparity. Model has 94% accuracy overall, but accuracy for minority demographic subgroups is 42%. Analyze bias pattern." }
];

export const PromptAnalysisPanel: React.FC<PromptAnalysisPanelProps> = ({
  onGenerate,
  isGenerating,
  error
}) => {
  const [promptText, setPromptText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (promptText.trim() && !isGenerating) {
      onGenerate(promptText.trim());
    }
  };

  const selectSample = (text: string) => {
    setPromptText(text);
  };

  return (
    <section className="panel prompt-analysis-panel max-w-4xl mx-auto w-full p-6 bg-[#071226]/60 border border-[#1e2d42] rounded-xl backdrop-blur-md" aria-labelledby="prompt-title">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-cyan-400" size={20} />
        <h2 id="prompt-title" className="text-lg font-semibold text-white">Describe a failed ML experiment</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          className="w-full h-32 p-3 bg-[#0b1724] border border-[#1e2d42] rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500 transition resize-none text-sm"
          placeholder="Example: Analyze a churn model that reached 93% accuracy but minority F1 dropped to 0.14. Find the root cause, retrieve evidence, recommend remediation, and map it to Microsoft certification skills."
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          disabled={isGenerating}
        />

        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-950/40 border border-red-500/50 rounded-lg text-red-200 text-sm">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <div className="flex flex-wrap gap-2 py-2">
          {SAMPLE_PROMPTS.map((sample) => (
            <button
              key={sample.label}
              type="button"
              className="px-3 py-1.5 bg-[#0b1724] border border-[#1e2d42] hover:border-cyan-500/50 hover:bg-[#071226] text-xs text-cyan-200 rounded-full transition cursor-pointer"
              onClick={() => selectSample(sample.text)}
              disabled={isGenerating}
            >
              {sample.label}
            </button>
          ))}
        </div>

        <button
          type="submit"
          className="w-full flex items-center justify-center gap-2 py-3 bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 disabled:text-cyan-400 text-white font-semibold rounded-lg shadow-lg shadow-cyan-500/10 hover:shadow-cyan-500/20 transition cursor-pointer"
          disabled={!promptText.trim() || isGenerating}
        >
          {isGenerating ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              <span>Generating FailureLens Analysis...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Generate FailureLens Analysis</span>
            </>
          )}
        </button>
      </form>
    </section>
  );
};

export default PromptAnalysisPanel;
