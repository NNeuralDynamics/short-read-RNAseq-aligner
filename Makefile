# Makefile

# Define the default target
all: install_python_packages install_star

# Target for installing Python packages
install_python_packages:
	python -m venv .venv
	source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && deactivate

# Target for installing STAR Aligner
install_star:
	mkdir -p bin
	cd STAR && git checkout -b 2.7.11a 2.7.11a && cd source && make -j && cp STAR ../../bin/.

# Clean up downloaded files
clean:
	cd STAR/source && make clean && git checkout master && git branch -D 2.7.11a &>/dev/null || true
	cd rmats-turbo && rm -f rmats_setup.patch && git checkout setup_environment.sh && git checkout master && git branch -D v4.2.0 &>/dev/null || true

.PHONY: all install_python_packages install_star clean
