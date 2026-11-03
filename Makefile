# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nkerstin <nkerstin@student.42heilbronn.    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/15 15:20:46 by nkerstin          #+#    #+#              #
#    Updated: 2026/11/03 15:17:37 by nkerstin         ###   ########.fr        #
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

GREEN      = \033[0;32m
RED        = \033[0;31m
YELLOW     = \033[0;33m
RESET      = \033[0m

define BAR
printf "$(1)$(2)$(RESET)\n"; printf "$(1)["; \
for i in $$(seq 1 20); do printf "■"; sleep 0.03; done; \
printf "] 100%%$(RESET)\n"
endef

.PHONY: install run debug clean fclean lint lint-strict test

run:
	@$(call BAR,$(YELLOW),Compiling fly-in...)
	@$(VPY) $(MAIN) $(MAP)

install:
	@$(PYTHON) -m venv $(VENV)
	@$(VPY) -m pip install --upgrade pip
	@$(VPY) -m pip install -r requirements.txt

debug:
	@$(call BAR,$(RED),Debugging...)
	$(VPY) -m pdb $(MAIN) $(MAP)

lint:
	$(FLAKE8)
	$(MYPY) $(MYPYFLAGS)

lint-strict:
	$(FLAKE8)
	$(MYPY) --strict

test:
	@$(call BAR,$(GREEN),Compiling tests...)
	@$(VPY) -m pytest -q

clean:
	@$(call BAR,$(RED),Deleting...)
	@find . -path ./$(VENV) -prune -o -name "__pycache__" -type d -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache

fclean: clean
	@rm -rf $(VENV)
