# GATCGGenerator v1.0

## Description

GATCGGenerator allows to generate specific quasi-random nucleotide sequences.
These are sequences without homopolymer regions with a given dinucleotides amount.
It is available to specify the required number of sequences, their length, GC-composition, and the percentage of dinucleotides.
In addition, the software allows sequences generation without homopolymer regions.
The generator excludes the presence of repeating motifs from 2 to 5 nucleotides more than four times.
The GATCGGenerator allows to generate DNA and RNA sequences . The output is presented as a CSV file.
The output table contains the following information: sequence, GC-composition, and quantitative content of each nucleotide.

## Authors
- Olga Kiryanova <kiryanova@anrb.ru>
- Ilya Kiryanov <ilya.lsc@gmail.com>
- Alexey Chemeris <chemeris@anrb.ru>

## License
GPL

## Requirenments:
- Python (>= 3.1)
- python-telegram-bot
- numpy

## Installation

- Talk to the BotFather Telegram bot in order to register a new bot and obtain a new API key for it (https://t.me/botfather). Keep the API key safe and secure.
- Go to the project folder: <code>cd project_folder</code>
- Create a new Python environment: <code>python -m venv environment_name</code>
- Activate the environment <code>environment_name\Scripts\activate.bat</code>
- Run <code>pip install -r requirements.txt</code>
- Place the API key as a value of variable <code>API_KEY</code> in "dna_sng.py"
- Run script "dna_sng.py": <code>python dna_sng.py</code>
- Now newely created bot should be available for all Telegram users
