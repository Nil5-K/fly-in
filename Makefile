# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nkerstin <nkerstin@student.42heilbronn.    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/15 15:20:46 by nkerstin          #+#    #+#              #
#    Updated: 2026/10/23 09:53:54 by nkerstin         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #


PYTHON     = python3
VENV       = .venv
VPY        = $(VENV)/bin/python

MAIN       = fly-in.py
MAP        = maps/easy/01_linear_path.txt

FLAKE8     = $(VPY) -m flake8 . --extend-exclude=$(VENV),tests
MYPY       = $(VPY) -m mypy . --exclude $(VENV) --exclude tests
MYPYFLAGS  = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
             --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean fclean lint lint-strict test

run:
	$(VPY) $(MAIN) $(MAP)

install:
	$(PYTHON) -m venv $(VENV)
	$(VPY) -m pip install --upgrade pip
	$(VPY) -m pip install -r requirements.txt

debug:
	$(VPY) -m pdb $(MAIN) $(MAP)

lint:
	$(FLAKE8)
	$(MYPY) $(MYPYFLAGS)

lint-strict:
	$(FLAKE8)
	$(MYPY) --strict

test:
	$(VPY) -m pytest -q

clean:
	find . -path ./$(VENV) -prune -o -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

fclean: clean
	rm -rf $(VENV)
