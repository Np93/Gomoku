# Variables
DC = docker-compose

# Nom de l'environnement conda
CONDA_ENV_NAME = gomoku
PYTHON_VERSION = 3.11
SO_FILE = cpp_gomoku.so

# Commandes
.PHONY: all build build_so run exec clean fclean re ps help setup_conda setup_conda_force clean_env clean_so

all: build_so ## Build la lib C++ (.so) dans Docker

build: ## Build complet Docker
	@if [ -f $(SO_FILE) ]; then \
		echo "✅ $(SO_FILE) déjà présent, image Docker non rebuildée."; \
	else \
		$(DC) build && echo "✅ Image Docker construite."; \
	fi

build_so: build ## Compile dans Docker et récupère le .so
	@if [ -f $(SO_FILE) ]; then \
		echo "✅ $(SO_FILE) déjà présent, compilation ignorée."; \
	else \
		echo "🚀 Compilation dans Docker..."; \
		cid=$$(docker create gomoku) && \
		docker cp $$cid:/app/cpp_gomoku.so ./cpp_gomoku.so && \
		docker rm $$cid && \
		echo "✅ $(SO_FILE) compilé et exporté."; \
	fi

run: ## Lance le jeu localement (avec GUI Pygame)
	poetry run python3 main.py

exec: ## Shell interactif dans le conteneur Docker
	$(DC) exec gomoku bash

test: ## Lance tout les tests
	poetry run pytest tests

setup_conda: ## ⚙️ Tout configurer avec conda : env + poetry + build .so
	@if [ ! -f $(SO_FILE) ]; then \
		echo "📦 Création de l'environnement conda + installation de poetry + compilation..."; \
		conda info --envs | grep -q "^$(CONDA_ENV_NAME)\s" || conda create -y -n $(CONDA_ENV_NAME) python=$(PYTHON_VERSION); \
		echo "✅ Environnement conda '$(CONDA_ENV_NAME)' prêt."; \
		source $$(conda info --base)/etc/profile.d/conda.sh && \
		conda activate $(CONDA_ENV_NAME) && \
		pip install poetry && \
		poetry install && \
		cmake -S . -B build \
			-DPython3_EXECUTABLE=$$(which python3) \
			-DPython3_ROOT_DIR=$$(python3 -c 'import sys; print(sys.prefix)') && \
		cmake --build build --config Release && \
		echo "✅ Compilation terminée."; \
	else \
		echo "✅ $(SO_FILE) déjà présent, rien à faire."; \
	fi

setup_conda_force: ## Force tout le setup pour env conda
	rm -rf build $(SO_FILE) .env_*
	$(MAKE) setup_conda

clean_so: ## Nettoyage pour env conda
	rm -f $(SO_FILE)
	rm -rf build

clean_env: ## Nettoyage de l'env conda
	@conda remove -y -n $(CONDA_ENV_NAME) --all || true
	rm -f .env_conda_created .env_poetry_installed

clean: ## Stoppe les conteneurs (garde les images)
	$(DC) down --volumes

fclean: clean_so clean_env ## Supprime conteneurs, images, volumes et orphans ainsi que l'env conda les fichier .so ...
	$(DC) down --rmi all --volumes --remove-orphans
	docker system prune -f

ps: ## Liste les conteneurs
	docker ps

re: fclean all ## Rebuild total du projet

help: ## Affiche l’aide
	@echo "Utilisation : make [commande]"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'