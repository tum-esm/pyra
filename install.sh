
python3.10 -m venv .venv
source .venv/bin/activate
poetry install

cp config/config.default.json config/config.json

# TODO: Download pyra-ui executable and put it in the project directory
