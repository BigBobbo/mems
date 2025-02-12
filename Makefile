.PHONY: test coverage e2e lint

test:
	PYTHONPATH=. pytest tests/test_*.py -v

coverage:
	PYTHONPATH=. pytest --cov=app tests/ --cov-report=html

e2e:
	PYTHONPATH=. pytest tests/test_e2e.py -v

lint:
	flake8 app tests
	black app tests --check

format:
	black app tests 