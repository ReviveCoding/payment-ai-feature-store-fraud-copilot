from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"
REPORTS = ROOT / "reports"
MODELS = ROOT / "models"
CONFIGS = ROOT / "configs"

for path in [DATA, OUTPUTS, REPORTS, MODELS, CONFIGS]:
    path.mkdir(parents=True, exist_ok=True)
