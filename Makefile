.venv:
	python -m virtualenv .venv
	bash -c "source .venv/bin/activate && pip install -e . || rm -rf .venv"
run: .venv
	bash -c "source .venv/bin/activate && czeditor"

dev: .venv
	bash -c "source .venv/bin/activate && pip install -e .[dev]"
build-deps: .venv
	bash -c "source .venv/bin/activate && pip install -e .[build]"
	
build: build-deps
	bash -c "source .venv/bin/activate && python -m build --wheel --no-isolation"
install: build
	python -m pip install dist/*.whl
bundle: build-deps
	bash -c " \
	source .venv/bin/activate && \
	python -m nuitka \
	--standalone --enable-plugin=pyside6 --include-data-dir=./czeditor/res=res \
	czeditor \
	"

clean:
	rm -rf build dist *.build *.dist *.onefile-build *.egg-info
dist-clean: | clean
	rm -rf .venv
	git clean -ixd

.PHONY: run build install bundle clean dist-clean