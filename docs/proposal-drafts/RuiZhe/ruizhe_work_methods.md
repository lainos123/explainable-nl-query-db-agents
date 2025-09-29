# 05 METHODS

## 001 Preliminary interrogation of the data

-   **Profiling:** For each table/column compute row counts, null/distinct rates, min/max, example values (hashed for sensitive fields)

-   **Unified schema catalog:** Normalize table/column names, comments, and constraints into a single catalog; derive synonyms via simple morphology (singular/plural).

-   **Intent Agent →** extracts **metrics**, **dimensions**, **filters**, **time window**, and **aggregation** from the question; emits an **intent frame** and ambiguity flags.

## 002 Choice of techniques to test

-    **Static checks:** reject queries with unbounded text operations on big tables, functions outside an allowlist, or predicted row counts above a configurable ceiling.

-   **Deterministic templates:** generate SELECT-FROM-JOIN-WHERE-GROUP BY with explicit aliases; always parameterise filter values.

## 003 Making the process understandable and outputs usable

-   **Explainability:** Human-readable “why this” rationales, lineage diagrams, and clearly stated assumptions:

    ***Why-this (positive evidence):*** list tables/columns used, the matched phrases, and the selected join path; show a minimal, readable SQL view.

    ***Why-not (counterfactuals):*** if a user expected a value/row, show which filter/join excluded it (e.g., inner join null elimination).

-   **Uncertainty communication:** Confidence indicators and alternative interpretations offered as options before execution.

## 004 Visualisation to communicate processes/results

-   **Result view:** Highlighted records, compact aggregates, and a simple lineage graph. Exports to CSV and to a reproducible analysis artifact: table with **highlighted fields** that justified inclusion; quick charts (bar/line) for common aggregates; one-click export to CSV and to a reproducible **analysis artifact** (notebook + SQL).

## 005 Collaborative tools for data/code version control

-   **Versioning:** Source control with pull-request review; data and experiment versioning.
-   **Project tracking:** Task board with owner & due date aligned to W1–W12 milestones; acceptance criteria per deliverable.