
TYPECHECK_TARGETS = chess/*.py

typecheck:
	python3.7 -m mypy --config-file mypy.ini $(TYPECHECK_TARGETS)
