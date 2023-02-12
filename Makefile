poetry.lock:
	poetry install --without=dev
dev:
	poetry install
run: | poetry.lock
	poetry run python -m czeditor

build: | poetry.lock
	poetry build
install: build
	python -m pip install dist/*.whl

clean:
	rm -rf build dist *.build *.dist
dist-clean: | clean
	rm -rf .venv poetry.lock
	git clean -ixd

.PHONY: run build clean dist-clean