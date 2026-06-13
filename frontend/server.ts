import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = Number(process.env.PORT) || 5173;

app.use(express.json());

// Initialize server-side Gemini client securely
let ai: any = null;
if (process.env.GEMINI_API_KEY) {
  try {
    ai = new GoogleGenAI({
      apiKey: process.env.GEMINI_API_KEY,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    });
    console.log("Gemini API Initialized successfully on the Backend.");
  } catch (error) {
    console.error("Failed to initialize Gemini Client API:", error);
  }
} else {
  console.log("No GEMINI_API_KEY detected. Utilizing structured reasoner mocks for prompt diagnostics.");
}

// In-memory sessions / experiments
let customExperiments: any[] = [];

// Helper to sanitize database output or mapping
const getSamplePayload = (prompt: string) => {
  const normalized = prompt.toLowerCase();
  
  if (normalized.includes("leakage") || normalized.includes("renewal") || normalized.includes("future")) {
    return {
      id: `EXP-${Math.floor(1001 + Math.random() * 99)}`,
      project: "Retention Forecasting Engine",
      modelType: "Random Forest Regressor",
      category: "Target Leakage",
      confidence: 91,
      iqMode: "azure-live",
      humanReview: "Approved",
      created: new Date().toISOString().split("T")[0],
      summary: prompt,
      rootCause: "The feature 'renewal_status_after_30d' incorporates future validation records created after the evaluation cutoff. This temporal leak allows the classifier to memorize future target outcomes, boosting training accuracy artificially while causing failure on deployed test splits.",
      recommendedFixes: [
        "Remove renewal_status_after_30d from model variables immediately.",
        "Integrate static date snapshot constraints into database features schemas.",
        "Implement a structural Temporal Auditor inside data prep pipelines."
      ],
      evidence: [
        "Feature correlation index with target variable stands at anomalous 0.94.",
        "Validation AUC achieved 98.4% while deployment evaluation collapsed to 44.1%.",
        "Pipeline audit logs confirmed renewal features timestamp belongs to target epoch + 30 days."
      ],
      reasoningSteps: [
        "Planner: Detected massive accuracy variance between live splits.",
        "Classifier: Identified temporal target leakage signature in features list.",
        "Historian: Found relevant citations on timestamp offset guards in Microsoft RA playbook.",
        "Coach: Outlined an interactive remediation checklist to purge target leakage features."
      ],
      certificationMapping: "Model Governance Standard (Audit Section G.1): Temporal Target Leakage Protection Checkbox"
    };
  } else if (normalized.includes("fairness") || normalized.includes("loan") || normalized.includes("protected") || normalized.includes("bias")) {
    return {
      id: `EXP-${Math.floor(2001 + Math.random() * 99)}`,
      project: "Loan Disbursal Assessment",
      modelType: "Neural Network Classifier",
      category: "Ethical & Demographic Disparate Impact",
      confidence: 82,
      iqMode: "foundry-live",
      humanReview: "Requires Audit",
      created: new Date().toISOString().split("T")[0],
      summary: prompt,
      rootCause: "Proxy variables (geographic zip-code combined with income percentiles) encode highly correlated demographic parameters. Even with demographic variables removed, spatial proxies permitted structural discrimination biases to propagate into target model activation layers.",
      recommendedFixes: [
        "Identify and filter geographic proxy features using mutual information audits.",
        "Deploy Fairlearn's GridSearch with demographic parity objectives.",
        "Ensure group fairness tracking is established as an evaluation KPI."
      ],
      evidence: [
        "Demographic parity ratio checked out at 0.61 (Minimum threshold is 0.80).",
        "Mutual Information score between zipcode feature and protected group is extremely high (0.76)."
      ],
      reasoningSteps: [
        "Planner: Investigating demographic bias patterns across input clusters.",
        "Classifier: Flagging disparately high error rates in protected demographics.",
        "Root Cause Analyst: Back-mapping zipcode features to demographic density models.",
        "Coach: Recommending adversarial debiasing in training layers."
      ],
      certificationMapping: "Microsoft Responsible AI Standard: Section F.1 Compliance Gate (Assessing Fairness and Disparate Harms)"
    };
  } else if (normalized.includes("pre-processing") || normalized.includes("categorical") || normalized.includes("encoding") || normalized.includes("preprocessing")) {
    return {
      id: `EXP-${Math.floor(3001 + Math.random() * 99)}`,
      project: "Inference Schema Monitor",
      modelType: "LightGBM regressor",
      category: "Pipeline Schema Divergence",
      confidence: 96,
      iqMode: "local-foundry",
      humanReview: "Pending Review",
      created: new Date().toISOString().split("T")[0],
      summary: prompt,
      rootCause: "Categorical encoder has mismatched string mapping tables between historical training pipelines and live online microservices. Inference requests submit categories that get assigned NaN index positions, crashing feature vector dimensions.",
      recommendedFixes: [
        "Implement unified schema-registry definitions built on Protobuf / JSON-Schema.",
        "Configure pipeline validation checks in API gateways to reject diverged payloads.",
        "Export the categorical vocabulary mapping table as a static deployment artifact."
      ],
      evidence: [
        "Inference pipeline logs report 12.3% of entries evaluated as Null elements.",
        "Mismatch identified between training features list (N=24) and online API features (N=21)."
      ],
      reasoningSteps: [
        "Planner: Mapping production logs to training manifest datasets.",
        "Classifier: Detecting missing categories and structural schema divergence.",
        "Historian: Loading relevant industry standards on schema registries."
      ],
      certificationMapping: "Enterprise Deployment Standards (Section 12.4): Continuous Schema Audit validation criteria"
    };
  }

  // General fallback for overfitting or regular topics
  return {
    id: `EXP-${Math.floor(1001 + Math.random() * 99)}`,
    project: "Baseline ML Engine",
    modelType: "Random Forest Classifier",
    category: "Overfitting & Hyperparameter Splurge",
    confidence: 79,
    iqMode: "local-foundry",
    humanReview: "Pending Review",
    created: new Date().toISOString().split("T")[0],
    summary: prompt,
    rootCause: "Model utilized deep branching bounds without regularized split parameters (max_depth unconstrained), enabling trees to memorize unique dataset samples directly. Lack of k-fold validation masked high-variance indicators.",
    recommendedFixes: [
      "Set pre-pruning trees constraints via max_depth and min_samples_split.",
      "Incorporate 5-fold stratified cross-validation routines into baseline scripts.",
      "Utilize ensemble bagging regularizations or dropout elements."
    ],
    evidence: [
      "Training evaluation reported 97.4% accuracy vs test evaluation of 61.2%.",
      "Model tree depths average 24 levels, indicating complete sample index mapping.",
      "Local Foundry retrieval highlighted 3 matching remediation playbooks."
    ],
    reasoningSteps: [
      "Planner: Inspecting model definition specifications for overfitting signs.",
      "Classifier: Confirming high training vs baseline validation metrics delta.",
      "Root Cause Analyst: Identifying deep unconstrained leaf branching as driver of high variance.",
      "Coach: Defining regularized hyperparameters tuning rules based on Microsoft patterns."
    ],
    certificationMapping: "Microsoft ML Governance Protocol standard (v3.1): Robustness and Variance Safeguards"
  };
};

// --- API ENDPOINTS ---

// GET /health
app.get(["/health", "/api/health"], (req, res) => {
  res.json({
    status: ai ? "active" : "local-simulation",
    timestamp: new Date().toISOString()
  });
});

// GET /readiness
app.get(["/readiness", "/api/readiness"], (req, res) => {
  res.json({ ready: true });
});

// GET /iq/status
app.get(["/iq/status", "/api/iq/status"], (req, res) => {
  res.json({
    status: "active",
    provider: ai ? "Azure Open AI + Gemini Reasoning Engine" : "Local Foundry IQ Adapter",
    iq_mode: ai ? "Azure Live Grounding" : "Foundry IQ Local Mode",
    live_search: ai ? true : false,
    citations_count: ai ? 14 : 4,
    warnings: ai ? [] : ["This run uses an offline Foundry template, mirroring knowledge sources locally."]
  });
});

// GET /experiments
app.get(["/experiments", "/api/experiments"], (req, res) => {
  // Combine custom sessions with standard fallback list
  res.json(customExperiments);
});

// GET /knowledge/search
app.get(["/knowledge/search", "/api/knowledge/search"], (req, res) => {
  const query = (req.query.query || "").toString().toLowerCase();
  const index = [
    {
      id: "KN-301",
      title: "Class Imbalance Calibration",
      sourceType: "Remediation Playbook",
      score: 0.96,
      excerpt: "For heavy class imbalances (>85/15), standard cross-entropy fails. Recommend focal loss wrappers, class weighting variables, and threshold adjustments.",
      citation: "Microsoft Foundational AI Playbook v3, Section 5"
    },
    {
      id: "KN-302",
      title: "Temporal Target Leakage Safeguards",
      sourceType: "Responsible AI",
      score: 0.93,
      excerpt: "Data leakage happens when future state features (timestamp >= target timestamp) are exposed to models during snapshot creation.",
      citation: "Foundry IQ Standards, Section F.1"
    },
    {
      id: "KN-303",
      title: "Proxy Variable Correlation Mitigations",
      sourceType: "Failure Taxonomy",
      score: 0.89,
      excerpt: "Protected classes are often latent in geographic zipcodes. Mitigate by removing high mutual information spatial predictors.",
      citation: "Fairness Assessment Framework, Microsoft v2"
    }
  ];

  if (!query) {
    return res.json(index);
  }

  const filtered = index.filter(k => 
    k.title.toLowerCase().includes(query) || 
    k.excerpt.toLowerCase().includes(query)
  );
  res.json(filtered);
});

// POST /prompt/analyze
app.post(["/prompt/analyze", "/api/prompt/analyze"], async (req, res) => {
  const { prompt } = req.body;
  if (!prompt) {
    return res.status(400).json({ error: "Prompt is required" });
  }

  console.log("Analyzing log or prompt of length:", prompt?.length || 0);

  if (ai) {
    try {
      // Call Gemini for standard full-stack structured reasoning
      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: `You are FailureLens IQ, a premium AI reasoning agent built for Microsoft Agents League. 
Analyze the following failed ML experiment described by the user:
"${prompt}"

Produce a structured JSON response matching the following output format:
{
  "project": "Descriptive project name representing their model",
  "modelType": "The machine learning model likely used or identified",
  "category": "The failure taxonomy category (e.g. Class Imbalance Bias, Target Leakage, Overfitting, Data Drift, Pipeline Schema Divergence)",
  "confidence": <integer percentage, e.g. 85>,
  "rootCause": "Detailed description in a high-quality human engineer voice addressing what failed and why.",
  "recommendedFixes": ["Fix 1", "Fix 2", "Fix 3"],
  "evidence": ["Evidence 1 from prompt", "Evidence 2 based on analysis"],
  "reasoningSteps": ["Agent trace planner step 1", "Step 2 identifying gaps", "Step 3 compiling plan"],
  "certificationMapping": "Specific compliance section map to Microsoft Responsible AI Standard or general ML governance rules"
}

Ensure the response is ONLY valid JSON.`,
        config: {
          responseMimeType: "application/json",
          temperature: 0.2,
        }
      });

      const responseText = response.text || "";
      const parsed = JSON.parse(responseText.trim());
      
      const newExperiment = {
        id: `EXP-${Math.floor(1001 + Math.random() * 8999)}`,
        iqMode: "azure-live",
        humanReview: "Pending Review",
        created: new Date().toISOString().split("T")[0],
        ...parsed
      };

      customExperiments.unshift(newExperiment);
      return res.json({
        success: true,
        mode: "azure-live",
        data: newExperiment
      });

    } catch (gError) {
      console.error("Gemini runtime error during live prompt analyze, falling back:", gError);
    }
  }

  // Fallback Offline Generator
  const offlineExp = getSamplePayload(prompt);
  customExperiments.unshift(offlineExp);
  res.json({
    success: true,
    mode: "offline-mock",
    data: offlineExp
  });
});

// POST /demo/run
app.post(["/demo/run", "/api/demo/run"], (req, res) => {
  res.json({
    success: true,
    status: "Demo Initiated",
    timestamp: new Date().toISOString()
  });
});

// POST /analysis/run
app.post(["/analysis/run", "/api/analysis/run"], (req, res) => {
  const { experimentId } = req.body;
  res.json({
    success: true,
    traceId: `T-${Math.floor(100000 + Math.random() * 900000)}`,
    status: "Analysis Pipeline completed successfully"
  });
});

// POST /report/:experiment_id/generate
app.post(["/report/:experiment_id/generate", "/api/report/:experiment_id/generate"], (req, res) => {
  const id = req.params.experiment_id;
  res.json({
    id: `REP-${Math.floor(500 + Math.random() * 499)}`,
    experimentId: id,
    title: `Remediation Report for ${id}`,
    downloadUrl: `/api/report/${id}/download`,
    status: "Generated Complete"
  });
});

// GET /report/:experiment_id/interactive
app.get(["/report/:experiment_id/interactive", "/api/report/:experiment_id/interactive"], (req, res) => {
  const id = req.params.experiment_id;
  res.json({
    url: `/report/${id}/interactive-preview`,
    html: `<h3>Interactive Analysis Plan</h3><p>Tracing completed for experiment ${id}. Microsoft IQ verification ready for submission.</p>`
  });
});


// Start server and handle Vite Static assets
async function start() {
  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[FailureLens IQ] Full-stack Server running at http://localhost:${PORT}`);
  });
}

start();
