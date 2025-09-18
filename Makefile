setup:
	test -d .venv || python -m venv .venv
	./.venv/bin/pip install -r requirements.txt -e . --config-settings editable_mode=strict

test_all:
	pytest