"""Full v3 narration, single Fish generation. Key from env only; new filename fish-gradient-v3-full.mp3."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('nf',ROOT/'scripts/narration-fish.py');nf=importlib.util.module_from_spec(spec);spec.loader.exec_module(nf)
TEXT=(ROOT/'scripts/v3-full-narration.txt').read_text(encoding='utf-8').strip()
nf.synthesize('v3-full',TEXT)
