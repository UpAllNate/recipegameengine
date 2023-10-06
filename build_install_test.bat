pipenv run py setup.py bdist_wheel sdist
pipenv run twine check dist/*
pipenv install . -d
pipenv run pytest .\app\recipegameengine\test\test_recipegameengine.py