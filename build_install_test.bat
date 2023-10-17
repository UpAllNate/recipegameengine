pipenv run py setup.py bdist_wheel sdist
pipenv run twine check dist/*
pipenv install . -d