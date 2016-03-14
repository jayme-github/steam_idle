clean:
		rm -rf dist build *.egg-info
		find . -type d -name "__pycache__"  -exec rm -rf {} \;
		find . -type f -name "*.pyc" -exec rm -rf {} \;

dist: clean
		python setup.py sdist

upload: dist
		twine upload -r pypi dist/*
