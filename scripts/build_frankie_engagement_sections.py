"""Assemble first-message retention and exhaustive message-content sections."""
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs/frankie-project-assessment'
text=(OUT/'first-message-usage-section.md').read_text(encoding='utf-8')+(OUT/'all-message-response-section.md').read_text(encoding='utf-8')
(OUT/'weekly-usage-and-answer-quality.md').write_text(text,encoding='utf-8')
print('Created weekly-usage-and-answer-quality.md')
