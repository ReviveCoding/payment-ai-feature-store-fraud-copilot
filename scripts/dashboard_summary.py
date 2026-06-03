from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def main():
    kpi_path = ROOT / "outputs" / "kpi_policy_scenarios.csv"
    if not kpi_path.exists():
        raise SystemExit("Run make run-demo first.")
    kpi = pd.read_csv(kpi_path)
    print("Payment Fraud-Risk Policy Dashboard Summary")
    print("=" * 48)
    print(kpi[["scenario", "pr_auc", "precision_at_capacity", "fraud_loss_capture_rate", "ece", "decision_score"]].to_string(index=False))
    print("\nSee reports/ for full validation artifacts.")

if __name__ == "__main__":
    main()
