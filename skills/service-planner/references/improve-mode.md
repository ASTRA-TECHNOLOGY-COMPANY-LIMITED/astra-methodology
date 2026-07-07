# Improve-existing-service mode

Read this when the user picks **🔄 Improve an existing service** at Step 0.B. It defines the extra data to collect and how that data (`{EXISTING_SERVICE_DATA}`) is woven through each downstream step. New-service planning ignores this file.

## Additional-info collection prompt (Step 0.B)

After the user chooses improve mode, ask:

```
## Improve an existing service — additional info

Please share existing data about the current service.
(If none, enter "none")

You can provide:
- user feedback / review data (file path or text)
- usage analytics (DAU, churn rate, conversion, etc.)
- top 10 CS inquiry types
- existing service URL or screen-capture path
- previous improvement history

Input:
```


Save the collected info as `{EXISTING_SERVICE_DATA}` and reflect it in the steps below.

## Per-step adaptations

- **Step 1 (market analysis)**: also analyze the current service's positioning and market position.
- **Step 3 (personas)**: reflect real user feedback / CS data in the personas' frustrations and interview answers.
- **Step 4 (idea derivation)**: author JTBD / HMW from real usage data (churn points, CS-inquiry types, use frequency) and back idea priority with empirical evidence.
- **Step 6 (IA)**: start from the current service's IA and mark only changed / added menu items (`[NEW]`, `[CHANGED]`); write wireframes only for the parts that change.
- **Step 7 (feature definition)**: distinguish existing vs. new/changed features (`[NEW]`, `[CHANGED]`, `[AS-IS]`); in the User Story Map place only the current-release changes in the MVP slice.
