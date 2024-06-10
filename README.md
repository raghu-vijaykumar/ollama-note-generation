# Notes Generation Pipeline

This project processes `.raw.txt` files to generate detailed notes using the `ollama` library. The project supports processing multiple files in parallel.

## Requirements

- Install ollama: https://www.ollama.com/download/linux
- Install phi3:14b model: https://www.ollama.com/library/phi3:14b (You can try out any llm, its all about prompting)

## Setup

```sh
# Set Up Virtual Environment
python -m venv venv
source venv/bin/activate

# Install python packages
pip install -r requirements.txt

# Run the pipeline
python app.py raw_to_notes 2 phi3:14b ./transcript
```
