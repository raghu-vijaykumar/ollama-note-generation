import glob
import logging
import os
import re
import uuid

import ollama


class BlogGenerator:
    def __init__(self, model):
        self.model = model
        self.system = """You are a BlogGPT, you know how to write informative 
        and engaging tech articles.
        """

    def read_markdown_files(self, notes_dir):
        """Reads all markdown files from the notes directory."""
        markdown_files = glob.glob(os.path.join(notes_dir, "*.md"))
        return markdown_files

    def ollama_gen(self, content):
        """Generates a blog from the given concepts using the model."""
        prompt = "Rewrite this as a blog article 5000-10000 words:\n\n" f"{content}"
        messages = [
            # {"role": "system", "content": system_prompt},
            {"role": "user", "content": self.system + "\n" + prompt},
        ]
        response = ollama.chat(model=self.model, messages=messages)
        return response["message"]["content"]

    def generate_blog(self, content, blog_dir, base_filename):
        """Generates a detailed blog from the given content using the model."""
        base_dir = os.path.join(blog_dir, base_filename)
        os.makedirs(base_dir, exist_ok=True)
        logging.info(f"Blog generation input length: {len(content)}")
        main_blog_content = self.ollama_gen(content)
        mainblog_filepath = os.path.join(base_dir, base_filename + ".md")
        with open(mainblog_filepath, "w", encoding="utf-8") as bf:
            bf.write(main_blog_content)

    def process_notes(self, notes_file, blog_dir, base_filename):
        """Processes a markdown file and generates a blog."""
        logging.info(f"Reading notes from {notes_file}.")
        with open(notes_file, "r", encoding="utf-8") as file:
            content = file.read()

        logging.info(f"Generating blog for {notes_file}.")
        self.generate_blog(content, blog_dir, base_filename=base_filename)
        logging.info(f"Blog successfully saved.")
