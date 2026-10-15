# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nkerstin <nkerstin@student.42heilbronn.    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/15 15:20:46 by nkerstin          #+#    #+#              #
#    Updated: 2026/10/15 18:06:56 by nkerstin         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

PYTHON      := $(or $(strip $(PYTHON)),python3)
VENV        := .venv
VPY         := $(VENV)/bin/python
PIP         := $(VPY) -m pip
 
MAIN        := fly-in.py
MAP         ?= maps/easy/01_linear_path.txt
ARGS        ?=
 
MYPY_FLAGS  := --warn-return-any --warn-unused-ignores \
               --ignore-missing-imports --disallow-untyped-defs \
               --check-untyped-defs
 
.DEFAULT_GOAL := help
.PHONY: help install run debug clean fclean lint lint-strict test
 
help:
	@echo "Usage: make <target> [MAP=path/to/map.txt] [ARGS='...']"
	@echo ""
	@echo "  install      create venv and install dependencies"
	@echo "  run          run the simulation on MAP"
	@echo "  debug        run the simulation under pdb"
	@echo "  lint         flake8 + mypy (mandatory flags)"
	@echo "  lint-strict  flake8 + mypy --strict"
	@echo "  test         run pytest"
	@echo "  clean        remove caches"
	@echo "  fclean       clean + remove venv"
 
$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
 
install: $(VENV)/bin/activate
	$(PIP) install --upgrade pip
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		$(PIP) install flake8 mypy pytest; \
	fi
 
run:
	$(VPY) $(MAIN) $(MAP) $(ARGS)
 
debug:
	$(VPY) -m pdb $(MAIN) $(MAP) $(ARGS)
 
lint:
	$(VPY) -m flake8 . --exclude $(VENV)
	$(VPY) -m mypy . $(MYPY_FLAGS) --exclude $(VENV)
 
lint-strict:
	$(VPY) -m flake8 . --exclude $(VENV)
	$(VPY) -m mypy . --strict --exclude $(VENV)
 
test:
	$(VPY) -m pytest -q
 
clean:
	find . -path ./$(VENV) -prune -o -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache
	find . -path ./$(VENV) -prune -o -type f -name "*.pyc" -delete
 
fclean: clean
	rm -rf $(VENV)
 