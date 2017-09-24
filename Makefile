distro: register clean build upload

init:
	pipenv install

init-dev:
	pipenv install --dev

doc:
	pandoc --from=markdown --to=rst --output="README.rst" "README.md"

clean:
	-rm -fr dist
	-rm -fr __pycache__
	-rm -fr build
	-find . -iname '*.pyc' -delete

build:
	python setup.py sdist
	python setup.py bdist_wheel

upload:
	twine upload dist/subst*

register:
	python setup.py register

