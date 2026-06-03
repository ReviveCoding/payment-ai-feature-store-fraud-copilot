# Transformer / NLP Routing Smoke Report

This report addresses the JD signal around NLP, LLMs, Transformers, and fine-tuning while keeping the core project centered on payment fraud-risk feature stores.

```json
{
  "status": "SKIPPED",
  "reason": "no multi-class routing label found",
  "transformers_available": false
}
```

## Interpretation

The default run is offline-safe. If the `transformers` package and local model weights are available, this module can be extended to DistilBERT/MiniLM-style fine-tuning for complaint issue or risk routing. Without local model weights, the project runs a TF-IDF logistic fallback and explicitly avoids claiming real Transformer fine-tuning.
