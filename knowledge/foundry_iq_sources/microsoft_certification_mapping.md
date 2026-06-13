id: cert-mapping-001
title: Microsoft Certification Mapping
source_type: certification_mapping
permission_scope: demo
tags: certification, skill_mapping, training
agent_usage_notes: The CertificationEvaluatorAgent uses this mapping to suggest official Microsoft Azure certifications and learning paths to technical teams based on diagnosed failure domains.
content: |
  # Microsoft Certification Mapping
  
  This mapping connects each technical issue to a relevant Azure AI certification path:
  
  ## Basic AI/ML Concepts
  - *Recommended Certification:* **AI-900: Azure AI Fundamentals** [24†L139-L145].
  - *Why:* Covers fundamental AI workloads, ML principles on Azure, and introduces Microsoft Foundry usage (Foundry is part of AI-900 objectives) [24†L139-L145].
  - *Used for:* Teams encountering general ML workflow or fairness issues need these foundational skills.
  
  ## Azure AI Solutions & Search
  - *Recommended Certification:* **AI-102: Azure AI Engineer Associate** [22†L20-L23][22†L181-L184].
  - *Why:* Focuses on designing/implementing solutions with Azure AI services, including Azure AI Search (knowledge mining) and Azure OpenAI [22†L20-L23][22†L181-L184].
  - *Used for:* Teams building or debugging solutions that integrate LLMs, agents, or search-based grounding.
  
  ## Responsible AI & Governance
  - *Recommended Certification:* **AZ-400: Azure DevOps Engineer** (with emphasis on security/governance).
  - *Why:* Although not AI-specific, AZ-400 covers implementing secure DevOps and compliance pipelines in Azure, supporting responsible AI operations.
  - *Used for:* Understanding how to integrate monitoring, auditing, and governance controls in ML projects.
  
  ## Data and Cloud Infrastructure
  - *Recommended Certification:* **DP-900 / AZ-900: Azure Data/Azure Fundamentals** for beginners.
  - *Why:* Provide knowledge of cloud/data fundamentals (data management, security in Azure) relevant to data pipelines and compliance.
  
  Each suggested certification has **learning paths** on Microsoft Learn and ensures the team has the skills to implement the required fixes (e.g. connecting Azure Search, building secure pipelines). By aligning failures to training, we support remediation and upskilling.
