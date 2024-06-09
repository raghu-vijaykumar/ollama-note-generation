from concurrent.futures import ThreadPoolExecutor
import glob
import os
import logging
import shutil

from blog_generator import BlogGenerator
from notes_generator import NotesGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def main(input_dir, notes_dir, blog_dir, archive_dir, max_tokens, max_threads):
    notes_generator = NotesGenerator(model="notes-phi3:14b", max_tokens=max_tokens)
    blog_generator = BlogGenerator(model="blog-phi3:14b")

    # Ensure the output directories exist
    os.makedirs(notes_dir, exist_ok=True)
    os.makedirs(blog_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Get all transcript files from input directory
    transcript_files = glob.glob(os.path.join(input_dir, "*.txt"))

    def process_file(file_path):
        try:
            # Generate notes
            filename = os.path.basename(file_path)
            notes_file = os.path.join(notes_dir, os.path.splitext(filename)[0] + ".md")
            # notes_generator.process_transcript(file_path, notes_file)

            # Generate blog
            blog_file = os.path.join(
                blog_dir, os.path.splitext(filename)[0] + "_blog.md"
            )
            blog_generator.process_notes(notes_file, blog_file)

            # Move file to archive directory
            archive_file = os.path.join(archive_dir, filename)
            shutil.move(file_path, archive_file)
            logging.info(f"Moved {filename} to archive directory.")
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {e}")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(process_file, file) for file in transcript_files]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in thread: {e}")


if __name__ == "__main__":
    input_dir = "./input"  # Replace with your input directory path
    notes_dir = "./notes"  # Directory to save generated notes
    blog_dir = "./blogs"  # Directory to save generated blogs
    archive_dir = "./archive"
    max_tokens = 4096  # Maximum number of tokens per chunk
    max_threads = 4  # Number of threads to use

    logging.info("Starting the transcript to notes and blog generation process.")
    main(input_dir, notes_dir, blog_dir, archive_dir, max_tokens, max_threads)
    logging.info("Completed the transcript to notes and blog generation process.")
