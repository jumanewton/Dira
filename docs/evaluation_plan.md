# Evaluation Plan

This document outlines the metrics and methods used to evaluate the performance and effectiveness of the Dira platform.

## 1. Technical Performance Metrics

### 1.1 Classification Accuracy (NLP Service)
*   **Metric:** Accuracy (%) of assigning the correct category (Infrastructure, Safety, Utility, etc.) compared to ground truth labels.
*   **Method:** Run a test set of 50 pre-labeled reports through the `ClassifierAgent`.
*   **Target:** > 85% accuracy.

### 1.2 Duplicate Detection Precision
*   **Metric:** Precision (%) - The percentage of flagged duplicates that are actual semantic duplicates.
*   **Method:** Inject 10 known duplicate reports (rephrased versions of existing ones) and measure how many are correctly identified by `DuplicateDetectorAgent`.
*   **Target:** > 90% precision (minimizing false positives is critical to avoid ignoring real issues).

### 1.3 Routing Latency
*   **Metric:** End-to-end time (seconds) from submission to "routed" status.
*   **Method:** Measure timestamp difference between `submitted_at` and `assigned_at` on the `HandledBy` edge.
*   **Target:** < 10 seconds per report.

## 2. Qualitative Evaluation

### 2.1 Message Quality (NLP Service)
*   **Metric:** Human rating (1-5 scale) of the drafted notification emails.
*   **Criteria:** Professionalism, conciseness, and inclusion of key details (Title, Urgency).
*   **Method:** Review 10 randomly generated drafts.

### 2.2 Graph Reasoning Effectiveness
*   **Metric:** Success rate of the `RouterAgent` in finding the *correct* organization type based on the report category.
*   **Example:** An "Infrastructure" report should route to a "Utility" or "Government" node, not a "Health" node.

## 3. User Experience (UX) Metrics

*   **Submission Ease:** Time taken to complete the report form.
*   **Transparency:** Availability of the public tracking link immediately after submission.

## 4. Evaluation Dataset

We use a seed dataset (`reports.json`) containing:
*   **20 Unique Reports:** Covering diverse categories (Potholes, outages, noise complaints).
*   **5 Duplicate Reports:** Rephrased versions of the above to test the vector search.
*   **5 Edge Cases:** Ambiguous descriptions to test `byLLM` reasoning capabilities.
