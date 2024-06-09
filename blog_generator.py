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
        and engaging articles. Your article should provide a comprehensive analysis 
        of the key factors that impact, including keywords. To make your article 
        informative and engaging, be sure to discuss the tradeoffs involved 
        in balancing different factors, and explore the challenges associated 
        with different approaches. Include code, examples exceptions wherever 
        necessary. Your article should also highlight the 
        importance of considering the impact on when making decisions. 
        Finally, your article should be written in an informative and 
        objective tone that is accessible to a general audience. Make sure 
        to include the relevant keywords provided by the user, and tailor 
        the article to their interests and needs
        """

    def read_markdown_files(self, notes_dir):
        """Reads all markdown files from the notes directory."""
        markdown_files = glob.glob(os.path.join(notes_dir, "*.md"))
        return markdown_files

    def extract_concepts(self, content):
        """Extracts the top 5 important concepts from the given content."""
        prompt = (
            """List the top 5 most important concepts with numerical bullet 
            points 1,2,3 ... with no sub points from the following content:\n\n"""
            + content
        )
        messages = []
        # messages.append({"role": "system", "content": self.system})
        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(model=self.model, messages=messages)
        concepts = response["message"]["content"]
        # logging.info(f"Extracted concepts:\n{concepts}")
        return concepts.strip().split("\n")

    def filter_numbered_concepts(self, concepts):
        """Filters and keeps only concepts that start with a number."""
        numbered_concepts = [
            concept
            for concept in concepts
            if concept.strip() and concept.strip()[0].isdigit()
        ]
        logging.info(f"Filtered numbered concepts:\n{numbered_concepts}")
        return numbered_concepts

    def generate_blog_from_concepts(self, concepts):
        """Generates a blog from the given concepts using the model."""
        prompt = (
            "Generate a detailed blog strictly in the range of 4000-5000 words in markdown on the following important concepts, each concept should be elaborated with relevant information:\n\n"
            f"{concepts}"
        )
        messages = []
        messages.append({"role": "system", "content": self.system})
        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(model=self.model, messages=messages)
        return response["message"]["content"]

    def extract_first_heading(self, section):
        """Extracts the first heading from the section."""
        # Use a regex to find the first markdown heading
        match = re.search(r"^(\s*#+\s+.*)$", section, re.MULTILINE)
        if match:
            heading = match.group(1).strip()
            # Convert heading to a suitable filename by removing special characters
            filename = re.sub(r"[^a-zA-Z0-9_\-]+", "_", heading.lower())
            return str(filename + ".md")
        # Return a random UUID if no heading is found
        return str(uuid.uuid4()) + ".md"

    def generate_main_blog(self, content, blog_dir, base_filename):
        """Generates the main blog content and saves it to a file."""
        # Generate main blog content based on the top concepts
        main_blog_content = self.generate_blog_from_concepts(content)

        # Write main blog content to file
        mainblog_filepath = os.path.join(blog_dir, base_filename + ".md")
        with open(mainblog_filepath, "w") as bf:
            bf.write(main_blog_content)

        # Log the path where main blog is saved
        logging.info(f"Saved detailed main blog to {mainblog_filepath}")

    def generate_blog(self, content, blog_dir, base_filename):
        """Generates a detailed blog from the given content using the model."""

        # Create directory for the blog if it doesn't exist
        base_dir = os.path.join(blog_dir, base_filename)
        os.makedirs(base_dir, exist_ok=True)

        numbered_concepts = self.filter_concepts(content)

        if not numbered_concepts:
            logging.error("Failed to extract numbered concepts after maximum attempts.")
            return  # Or handle this case as needed

        # Generate main blog
        self.generate_main_blog("\n".join(numbered_concepts), base_dir, base_filename)

        # Generate a detailed section for each concept
        for concept in numbered_concepts:
            if concept.strip():
                section = self.generate_blog_from_concepts(concept.strip())
                logging.info(f"Generated section for concept: {concept.strip()}")

                # Save each section to a separate file
                # Extract the first heading from the section for the filename
                filename = self.extract_first_heading(section)
                concept_filepath = os.path.join(base_dir, filename)
                with open(concept_filepath, "w") as bf:
                    bf.write(section)
                logging.info(f"Saved detailed sub blog section to {concept_filepath}")

    def filter_concepts(self, content):
        max_attempts = 5  # Maximum number of attempts to extract numbered concepts

        attempt = 0
        numbered_concepts = []
        while not numbered_concepts and attempt < max_attempts:
            # Extract top 5 important concepts
            concepts = self.extract_concepts(content)
            # Filter out numbered concepts
            numbered_concepts = self.filter_numbered_concepts(concepts)
            attempt += 1
            logging.info(
                f"Attempt {attempt}: Extracted {len(numbered_concepts)} numbered concepts."
            )

            if not numbered_concepts:
                logging.warning(
                    f"No numbered concepts found on attempt {attempt}. Retrying..."
                )

        return numbered_concepts

    def process_notes(self, notes_file, blog_dir, base_filename):
        """Processes a markdown file and generates a blog."""
        logging.info(f"Reading notes from {notes_file}.")
        with open(notes_file, "r") as file:
            content = file.read()

        logging.info(f"Generating blog for {notes_file}.")
        self.generate_blog(content, blog_dir, base_filename=base_filename)
