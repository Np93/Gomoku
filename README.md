conda create -n gomoku python=3.11
conda activate gomoku

pip install uv
uv pip install -e .    OU uv sync 

# Create a build/ dir, go into it and type >
cmake .. && make && cp cpp_gomoku.so ../ && cp cpp_gomoku.so ../tests