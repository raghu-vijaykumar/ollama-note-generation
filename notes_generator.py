import logging
import os
import time
import ollama


class NotesGenerator:
    def __init__(self, model, max_tokens=512):
        self.model = model
        self.max_tokens = max_tokens
        self.system = """You are NotesGPT, When provided with a topic your task is 
        - Taking detailed, precise, and easy-to-understand notes
        - Create advanced bullet-point notes summarizing the important parts of the reading or topic. 
        - Include all essential information, use text highlighting with bold fonts for important key words. 
        - Remove any extraneous language or the source of the content like courses, labs. 
        - Strictly base your notes on the provided information.
        - Tabulate any comparisions in markdown syntax.
        - Numerical values in the context are important dont leave them out. 
        - Includes code.
        - Use latex for any mathematical equations.  
        - Avoid repetition.
        - The length of the summary should be appropriate for the length and complexity of the original text.
        - Dont include tasks or insructions or homework in the text. 
        - Provide response in markdown for easy documentation.
        
        Content:
        """

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

    def process_transcript(self, file_path):
        """Reads a transcript file, splits it, and generates notes."""
        logging.info(f"Reading transcript from {file_path}.")
        with open(file_path, "r") as file:
            transcript = file.read()
        start_time = time.time()
        chunks = self.split_text(transcript)

        # Determine output path for notes
        model_name = self.model.replace(":", "_")
        output_path = os.path.splitext(file_path)[0] + f".{model_name}" + ".notes.md"

        messages = []
        with open(output_path, "w") as output_file:
            for i, chunk in enumerate(chunks):
                logging.info(f"Processing chunk {i+1}/{len(chunks)}.")
                messages.append({"role": "user", "content": f"{self.system + chunk}"})
                message = self.query_gpt(messages)
                messages.append(message)
                output_file.write(message["content"] + "\n\n")
                output_file.flush()  # Ensure the note is written to disk immediately

        end_time = time.time()
        logging.info(
            f"Finished processing all chunks in {end_time - start_time:.2f} seconds."
        )
