.PHONY: install run check clean

install:
	pip install -r gateway/requirements.txt

run:
	@bash scripts/start-gateway.sh

check:
	@bash scripts/check-connection.sh

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
