doc:
	pandoc --from=markdown --to=rst --output="README.rst" "README.md"

clean:
	rm dist/* || true
	rm -fr __pycache__ || true
	rm -fr build || true

build:
	python setup.py sdist
	python setup.py bdist_wheel

upload:
	twine upload dist/subst*

distro: clean build upload
