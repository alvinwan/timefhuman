coverage:
	py.test --cov
	coverage html
	open htmlcov/index.html
