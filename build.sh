set -e
python -m venv .venv_tmp
. .venv_tmp/bin/activate
pip install -r requirements.txt
lektor --project sps20 build -f scss --output-path build
rm -r .venv_tmp
