# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: nkerstin <nkerstin@student.42heilbronn.    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/10/15 15:20:46 by nkerstin          #+#    #+#              #
#    Updated: 2026/10/23 18:45:57 by nkerstin         ###   ########.fr        #
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

.PHONY: install run debug clean fclean lint lint-strict test

run:
	@echo "$(Y)Compiling fly-in...$(RESET)"
	@printf "$(G)["
	@for i in $$(seq 1 20); do \
		printf "■"; \
		sleep 0.03; \
	done
	@printf "] 100%%$(RESET)\n"
	@$(VPY) $(MAIN) $(MAP)

install:
	@$(PYTHON) -m venv $(VENV)
	@$(VPY) -m pip install --upgrade pip
	@$(VPY) -m pip install -r requirements.txt

debug:
	@echo "$(RED)Debugging...$(RESET)"
	@printf "$(G)["
	@for i in $$(seq 1 20); do \
		printf "■"; \
		sleep 0.03; \
	done
	@printf "] 100%%$(RESET)\n"
	$(VPY) -m pdb $(MAIN) $(MAP)

lint:
	$(FLAKE8)
	$(MYPY) $(MYPYFLAGS)

lint-strict:
	$(FLAKE8)
	$(MYPY) --strict

test:
	@echo "$(GREEN)Compiling tests...$(RESET)"
	@printf "$(G)["
	@for i in $$(seq 1 20); do \
		printf "■"; \
		sleep 0.03; \
	done
	@printf "] 100%%$(RESET)\n"
	@$(VPY) -m pytest -q

clean:
	@echo "$(RED)Deleting...$(RESET)"
	@printf "$(G)["
	@for i in $$(seq 1 20); do \
		printf "■"; \
		sleep 0.03; \
	done
	@printf "] 100%%$(RESET)\n"
	@find . -path ./$(VENV) -prune -o -name "__pycache__" -type d -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache

fclean: clean
	@rm -rf $(VENV)
