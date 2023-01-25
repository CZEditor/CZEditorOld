poetry.lock:
	poetry install --without=dev
dev: poetry.lock
	poetry install
run: | poetry.lock
	poetry run python czeditor.py

install:
	poetry build
	pip install dist/*.whl

clean:
	rm -rf build dist *.build *.dist
dist-clean: | clean
	rm -rf .venv poetry.lock
	git clean -ixd

.PHONY: run clean dist-clean