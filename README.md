Start off by installing the requirements (preferrably in a virtual environment). This will vary by OS, python path, etc, but will look something like this:

python -m venv /path/to/new/virtual/environment
./env/Scripts/activate
pip install -r requirements.txt

From there the script should run with a simple command (python format_builder.py)

The csv is the basis for all the data. Each final stage evolution is given one line, unless it has multiple forms that have different base stats. When forms have the same base stats but different typings that will be reflected in the 'Typing' column.
