default: check-source check

check-source: check-flake8 check-mypy

check-flake8:
	flake8 | cat

check-mypy:
	mypy .

check:
	pytest
