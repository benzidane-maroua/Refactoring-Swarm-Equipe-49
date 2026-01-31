CHANGELOG = """
# Prompts Changelog – Refactoring Swarm

## Version history

### v1.0 – 2026-01-29 (initial version)
- Created baseline prompts for Auditor, Fixer, Judge
- Auditor: strict severity levels + pylint focus
- Fixer: minimal changes + preserve behavior
- Judge: conservative ACCEPT only if all tests pass

### v1.1 – 2026-02-01
- Auditor: added "Global Recommendations" section
- Fixer: improved instruction to use type hints & Google docstrings
- Reduced token usage in Auditor by ~15% (removed redundant rules)

### v1.2 – upcoming
- Plan: add few-shot example in Auditor prompt
- Reason: reduce hallucinations on complex code smells
"""