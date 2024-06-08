import glob
import logging
import os

import ollama


class BlogGenerator:
    def __init__(self, model):
        self.model = model

    def read_markdown_files(self, notes_dir):
        """Reads all markdown files from the notes directory."""
        markdown_files = glob.glob(os.path.join(notes_dir, "*.md"))
        return markdown_files

    def generate_blog(self, content):
        """Generates a blog from the given content using the model."""
        response = ollama.chat(
            model=self.model, messages=[{"role": "user", "content": content}]
        )
        return response["message"]["content"]

    def process_notes(self, notes_file, blog_file):
        """Processes a markdown file and generates a blog."""
        logging.info(f"Reading notes from {notes_file}.")
        with open(notes_file, "r") as file:
            content = file.read()

        logging.info(f"Generating blog for {notes_file}.")
        blog_content = self.generate_blog(content)

        logging.info(f"Saving generated blog to {blog_file}.")
        with open(blog_file, "w") as blog_file_obj:
            blog_file_obj.write(blog_content)
        logging.info(f"Blog successfully saved to {blog_file}.")
