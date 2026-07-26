.PHONY: install run clean debug lint lint-strict

# export HF_HOME=/tmp/hf_home
# export UV_CACHE_DIR=/tmp/uv_cache_dir
# export UV_PROJECT_ENVIRONMENT=/tmp/uv_venv

install:
	@python3 -m pip install .

run:
	@uv run python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calls.json

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".mypy_cache" -exec rm -rf {} +

debug:
	@uv run python -m pudb -m src

lint:
	@uv run flake8 src
	@uv run mypy src --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	@uv run flake8 src
	@uv run mypy src --strict
