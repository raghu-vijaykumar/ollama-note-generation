import logging
import ollama
import time
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def count_tokens(text):
    """Counts the number of tokens in a text string."""
    return len(text.split())


def split_text(text, max_tokens=512):
    """Splits the text into chunks based on a specified maximum number of tokens."""
    paragraphs = text.split("\n\n")
    chunks = []

    logging.info("Starting to split the transcript into chunks.")

    for paragraph in paragraphs:
        words = paragraph.split()
        while words:
            if len(words) <= max_tokens:
                # Add the entire paragraph as a chunk
                chunks.append(" ".join(words).strip())
                logging.info(
                    f"Created a chunk with {count_tokens(' '.join(words))} tokens."
                )
                words = []
            else:
                # Split the paragraph into a chunk and update remaining words
                split_point = max_tokens
                sub_chunk = words[:split_point]
                chunks.append(" ".join(sub_chunk).strip())
                logging.info(
                    f"Split a paragraph into a chunk with {count_tokens(' '.join(sub_chunk))} tokens."
                )
                words = words[split_point:]

    logging.info(f"Total chunks created: {len(chunks)}")
    return chunks


def query_gpt(messages, model):
    """Generates notes for a given prompt using LLaMA3."""
    system = """You are NotesGPT, an AI language model skilled at taking detailed, precise, and easy-to-understand notes on 
                various subjects in bullet-point format. When provided with a passage or a topic, your task is to:
                Create advanced bullet-point notes summarizing the important parts of the reading or topic.
                Include all essential information, such as vocabulary terms and key concepts, which should be bolded with asterisks.
                Remove any extraneous language, focusing only on the critical aspects of the passage or topic.
                Strictly base your notes on the provided information, without adding any external information.
                Tabulate any comparisions. Numerical values in the context are important dont leave them out.
                lease ensure that the summary includes relevant details and examples that support the main ideas, 
                while avoiding any unnecessary information or repetition. The length of the summary should be 
                appropriate for the length and complexity of the original text. Provide response in markdown for easy documentation. 
                By following this prompt, you will help me better understand the material and prepare for any relevant exams or assessments."""

    logging.info(
        f"Sending a chunk to the model: {model} chunk: {messages[-1]['content'][:50]}"
    )
    messages.append({"role": "system", "content": f"{system}"})
    start_time = time.time()
    response = ollama.chat(model=model, messages=messages)
    end_time = time.time()
    logging.info(
        f"Received response of {len(response['message']['content'])} tokens for input {len(messages[-2]['content'])} tokens from the model in {end_time - start_time:.2f} seconds."
    )
    return response["message"]


def process_transcript(file_path, model, max_tokens, output_path):
    """Reads a transcript file, splits it, and generates notes."""
    logging.info(f"Reading transcript from {file_path}.")
    with open(file_path, "r") as file:
        transcript = file.read()
    start_time = time.time()
    chunks = split_text(transcript, max_tokens)

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    messages = []
    with open(output_path, "w") as output_file:
        for i, chunk in enumerate(chunks):
            logging.info(f"Processing chunk {i+1}/{len(chunks)}.")
            messages.append({"role": "user", "content": f"{chunk}"})
            message = query_gpt(messages, model)
            messages.append(message)
            output_file.write(message["content"] + "\n\n")
            output_file.flush()  # Ensure the note is written to disk immediately

    end_time = time.time()
    logging.info(
        f"Finished processing all chunks in {end_time - start_time:.2f} seconds."
    )


def save_notes(notes, output_path):
    """Saves the generated notes to a markdown file."""
    logging.info(f"Saving notes to {output_path}.")
    with open(output_path, "w") as file:
        for note in notes:
            file.write(note + "\n\n")
    logging.info(f"Notes successfully saved to {output_path}.")


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
    avg_words_per_paragraph = total_words / num_paragraphs if num_paragraphs > 0 else 0

    return num_paragraphs, avg_words_per_paragraph


if __name__ == "__main__":
    input_file = "./transcript.txt"  # Replace with your transcript file path
    output_file = "./notes.md"  # Replace with desired output file path
    num_paragraphs, avg_words_per_paragraph = count_paragraphs_and_average_words(
        input_file
    )
    logging.info(f"Number of paragraphs: {num_paragraphs}")
    logging.info(f"Average words per paragraph: {avg_words_per_paragraph:.2f}")
    logging.info("Starting the transcript processing script.")
    process_transcript(
        input_file, "phi3:14b", int(avg_words_per_paragraph), output_file
    )
    logging.info("Transcript processing script finished.")
