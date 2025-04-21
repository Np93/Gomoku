FROM python:3.10-slim

# Installer outils système
RUN apt-get update && apt-get install -y \
  build-essential \
  cmake \
  git \
  && rm -rf /var/lib/apt/lists/*

# Cloner et installer pybind11 en tant que package CMake
RUN git clone https://github.com/pybind/pybind11.git /tmp/pybind11 \
 && cd /tmp/pybind11 \
 && cmake -DPYBIND11_TEST=OFF -DCMAKE_INSTALL_PREFIX=/usr/local . \
 && make install \
 && rm -rf /tmp/pybind11

# Définir le dossier de travail
WORKDIR /app

# Copier ton projet
COPY . .

# Installer les dépendances Python
RUN pip install -e .

# Compilation du module C++
RUN mkdir -p build \
 && cd build \
 && cmake .. \
 && make \
 && cp /app/build/cpp_gomoku.so /app/ || true \
 && ls -lh /app && ls -lh /app/build

# Lancer un shell par défaut
CMD ["bash"]