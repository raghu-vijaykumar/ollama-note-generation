import logging
import os
import time

import ollama


class NotesGenerator:
    def __init__(self, model, max_tokens=512):
        self.model = model
        self.max_tokens = max_tokens

    @staticmethod
    def count_tokens(text):
        """Counts the number of tokens in a text string."""
        return len(text.split())

    def split_text(self, text):
        """Splits the text into chunks based on a specified maximum number of tokens."""
        paragraphs = text.split("\n\n")
        chunks = []

        logging.info("Starting to split the transcript into chunks.")

        for paragraph in paragraphs:
            words = paragraph.split()
            while words:
                if len(words) <= self.max_tokens:
                    # Add the entire paragraph as a chunk
                    chunks.append(" ".join(words).strip())
                    logging.info(
                        f"Created a chunk with {self.count_tokens(' '.join(words))} tokens."
                    )
                    words = []
                else:
                    # Split the paragraph into a chunk and update remaining words
                    split_point = self.max_tokens
                    sub_chunk = words[:split_point]
                    chunks.append(" ".join(sub_chunk).strip())
                    logging.info(
                        f"Split a paragraph into a chunk with {self.count_tokens(' '.join(sub_chunk))} tokens."
                    )
                    words = words[split_point:]

        logging.info(f"Total chunks created: {len(chunks)}")
        return chunks

    def query_gpt(self, messages):
        """Generates notes for a given prompt using LLaMA3."""
        start_time = time.time()
        response = ollama.chat(model=self.model, messages=messages)
        end_time = time.time()
        logging.info(
            f"Received response of {len(response['message']['content'])} tokens for input {len(messages[-1]['content'])} tokens from the model in {end_time - start_time:.2f} seconds."
        )
        return response["message"]

    def process_transcript(self, file_path, output_path):
        """Reads a transcript file, splits it, and generates notes."""
        logging.info(f"Reading transcript from {file_path}.")
        with open(file_path, "r") as file:
            transcript = file.read()
        start_time = time.time()
        chunks = self.split_text(transcript)

        # Create the output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        messages = []
        with open(output_path, "w") as output_file:
            for i, chunk in enumerate(chunks):
                logging.info(f"Processing chunk {i+1}/{len(chunks)}.")
                messages.append({"role": "user", "content": f"{chunk}"})
                message = self.query_gpt(messages)
                messages.append(message)
                output_file.write(message["content"] + "\n\n")
                output_file.flush()  # Ensure the note is written to disk immediately

        end_time = time.time()
        logging.info(
            f"Finished processing all chunks in {end_time - start_time:.2f} seconds."
        )

    @staticmethod
    def max_words_in_paragraphs(file_path):
        """Calculates the maximum number of words in any paragraph from an input file."""
        with open(file_path, "r") as file:
            content = file.read()

        # Split content into paragraphs
        paragraphs = content.split("\n\n")

        max_words = 0
        for paragraph in paragraphs:
            word_count = NotesGenerator.count_tokens(paragraph)
            if word_count > max_words:
                max_words = word_count

        return max_words

    @staticmethod
    def count_paragraphs_and_average_words(file_path):
        """Counts the number of paragraphs and calculates the average number of words per paragraph."""
        with open(file_path, "r") as file:
            content = file.read()
        # Split content into paragraphs
        paragraphs = content.split("\n\n")
        # Count the number of paragraphs
        num_paragraphs = len(paragraphs)
        # Calculate the total number of words
        total_words = sum(
            len(paragraph.split()) for paragraph in paragraphs if paragraph.strip()
        )
        # Calculate the average number of words per paragraph
        avg_words_per_paragraph = (
            total_words / num_paragraphs if num_paragraphs > 0 else 0
        )
        return num_paragraphs, avg_words_per_paragraph
