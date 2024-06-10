from concurrent.futures import ThreadPoolExecutor
import glob
import os
import logging
import shutil
import sys

from notes_generator import NotesGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def process_raw_to_notes(file_path, notes_generator):
    try:
        notes_generator.process_transcript(file_path)
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")


def run_raw_to_notes(model, max_threads, folder):
    notes_generator = NotesGenerator(model=model, max_tokens=4096)

    # Get all transcript files from input directory
    raw_files = glob.glob(os.path.join(folder, "**/*.raw.txt"), recursive=True)
    # Initialize a list to store raw files without corresponding notes files
    filtered_raw_files = []

    # Iterate over the raw files
    for raw_file in raw_files:
        # Get the name of the raw file without the extension
        raw_file_name = os.path.splitext(os.path.basename(raw_file))[0]
        # Check if a corresponding notes file exists
        model_name = model.replace(":", "_")
        notes_file = os.path.join(
            os.path.dirname(raw_file), raw_file_name + f".{model_name}" + ".notes.md"
        )
        if not os.path.exists(notes_file):
            # If notes file does not exist, add the raw file to the filtered list
            filtered_raw_files.append(raw_file)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(process_raw_to_notes, file, notes_generator)
            for file in filtered_raw_files
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in transcript to notes thread: {e}")


def main(pipeline, model, max_threads, folder):
    if pipeline == "raw_to_notes":
        run_raw_to_notes(model, max_threads, folder)
    else:
        logging.error(f"Unknown pipeline: {pipeline}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python main.py <pipeline> <max_threads> <model> <folder>")
        print("pipeline: 'raw_to_notes'")
        sys.exit(1)

    pipeline = sys.argv[1]
    max_threads = int(sys.argv[2])
    model = sys.argv[3]
    folder = sys.argv[4]

    logging.info("Starting note generation process.")
    main(pipeline, model, max_threads, folder)
    logging.info("Completed note generation process.")
