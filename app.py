from concurrent.futures import ThreadPoolExecutor
import glob
import os
import logging
import shutil
import sys

from blog_generator import BlogGenerator
from notes_generator import NotesGenerator
from post_generator import PostGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(threadName)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def process_transcript_to_notes(file_path, notes_generator, notes_dir):
    try:
        filename = os.path.basename(file_path)
        notes_file = os.path.join(notes_dir, os.path.splitext(filename)[0] + ".md")
        notes_generator.process_transcript(file_path, notes_file)
        return file_path, notes_file
    except Exception as e:
        logging.error(f"Error processing transcript to notes for file {file_path}: {e}")
        return file_path, None


def process_notes_to_blog(notes_file, blog_generator, blog_dir, archive_dir):
    try:
        filename = os.path.basename(notes_file)
        base_filename = os.path.splitext(filename)[0]
        blog_generator.process_notes(notes_file, blog_dir, base_filename)
        archive_file = os.path.join(archive_dir, filename)
        shutil.move(notes_file, archive_file)
        logging.info(f"Moved {filename} to archive directory.")
    except Exception as e:
        logging.error(f"Error processing notes to blog for file {notes_file}: {e}")


def process_blog_to_post(blog_file, post_generator):
    try:
        post_generator.process_blog(blog_file)
    except Exception as e:
        logging.error(f"Error processing blog to post for file {blog_file}: {e}")


def run_transcript_to_notes(max_threads, notes_dir):
    text_dir = "./text"  # Replace with your input directory path
    notes_generator = NotesGenerator(model="notes-phi3:14b", max_tokens=4096)

    # Ensure the notes directory exists
    os.makedirs(notes_dir, exist_ok=True)

    # Get all transcript files from input directory
    transcript_files = glob.glob(os.path.join(text_dir, "**", "*.txt"), recursive=True)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(
                process_transcript_to_notes, file, notes_generator, notes_dir
            )
            for file in transcript_files
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in transcript to notes thread: {e}")


def run_notes_to_blog(max_threads, notes_dir, blog_dir, archive_dir):
    blog_generator = BlogGenerator(model="phi3:14b")

    # Ensure the output directories exist
    os.makedirs(blog_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)

    # Get all notes files from notes directory
    notes_files = glob.glob(os.path.join(notes_dir, "**", "*.md"), recursive=True)
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(
                process_notes_to_blog, file, blog_generator, blog_dir, archive_dir
            )
            for file in notes_files
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in notes to blog thread: {e}")


def run_blog_to_post(max_threads, blog_dir):
    post_generator = PostGenerator(model="phi3:14b")

    # Get all blog files from blog directory, excluding files with .post.md
    blog_files = [
        file
        for file in glob.glob(os.path.join(blog_dir, "**", "*.md"), recursive=True)
        if not file.endswith(".post.md")
    ]
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [
            executor.submit(process_blog_to_post, file, post_generator)
            for file in blog_files
        ]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logging.error(f"Error in blog to post thread: {e}")


def run_pipeline_sequentially(max_threads):
    notes_dir = "./notes"  # Directory to save generated notes
    blog_dir = "./blogs"  # Directory to save generated blogs
    archive_dir = "./archive"

    run_transcript_to_notes(max_threads, notes_dir)
    run_notes_to_blog(max_threads, notes_dir, blog_dir, archive_dir)
    run_blog_to_post(max_threads, blog_dir)


def main(pipeline, max_threads):
    notes_dir = "./notes"  # Directory to save generated notes
    blog_dir = "./blogs"  # Directory to save generated blogs
    archive_dir = "./archive"

    if pipeline == "sequential":
        run_pipeline_sequentially(max_threads)
    elif pipeline == "transcript_to_notes":
        run_transcript_to_notes(max_threads, notes_dir)
    elif pipeline == "notes_to_blog":
        run_notes_to_blog(max_threads, notes_dir, blog_dir, archive_dir)
    elif pipeline == "blog_to_post":
        run_blog_to_post(max_threads, blog_dir)
    else:
        logging.error(f"Unknown pipeline: {pipeline}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <pipeline> <max_threads>")
        print(
            "pipeline: 'sequential', 'transcript_to_notes', 'notes_to_blog', or 'blog_to_post'"
        )
        sys.exit(1)

    pipeline = sys.argv[1]
    max_threads = int(sys.argv[2])

    logging.info("Starting blog generation process.")
    main(pipeline, max_threads)
    logging.info("Completed blog generation process.")
