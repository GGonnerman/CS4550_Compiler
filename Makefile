setup:
	test -d .venv || python3 -m venv .venv
	./.venv/bin/pip install -r ./src/compiler/requirements.txt -e . --config-settings editable_mode=strict

test_all:
	pytest