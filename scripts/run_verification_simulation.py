"""Reproduce or resume the separately specified additional simulation validation."""
import json
import logging
from pathlib import Path
from compas_fairness.simulation import run_simulation
logging.basicConfig(level=logging.INFO)
out=Path('results/verification_simulation');out.mkdir(exist_ok=True)
run_simulation(json.loads(Path('configs/verification_simulation.json').read_text()),out)
