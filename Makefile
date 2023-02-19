poetry.lock:
	poetry install --without=dev
dev: poetry.lock
	poetry install
run: poetry.lock
	poetry run python -m czeditor

build: dev
	poetry build --format wheel
install: build
	python -m pip install dist/*.whl
bundle: dev
	poetry run python -m nuitka --standalone --enable-plugin=pyside6 czeditor

clean:
	rm -rf build dist *.build *.dist *.onefile-build
dist-clean: | clean
	rm -rf .venv poetry.lock
	git clean -ixd

.PHONY: run build install bundle clean dist-clean