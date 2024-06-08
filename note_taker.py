import logging
import ollama
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def count_tokens(text):
    """Counts the number of tokens in a text string."""
    return len(text.split())

def split_text(text, max_tokens=512):
    """Splits the text into chunks based on a specified maximum number of tokens."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    current_length = 0

    logging.info("Starting to split the transcript into chunks.")

    for paragraph in paragraphs:
        paragraph_length = count_tokens(paragraph)

        if current_length + paragraph_length > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                current_length = 0
                logging.info(f"Created a chunk with {count_tokens(current_chunk)} tokens.")

        while paragraph_length > max_tokens:
            sub_chunk = paragraph[:max_tokens]
            chunks.append(sub_chunk)
            logging.info(f"Split a paragraph into a chunk with {count_tokens(sub_chunk)} tokens.")
            paragraph = paragraph[max_tokens:]
            paragraph_length = count_tokens(paragraph)

        current_chunk += paragraph + "\n\n"
        current_length += paragraph_length

    if current_chunk:
        chunks.append(current_chunk)
        logging.info(f"Created a final chunk with {count_tokens(current_chunk)} tokens.")

    logging.info(f"Total chunks created: {len(chunks)}")
    return chunks

def query_gpt(prompt, model):
    """Generates notes for a given prompt using LLaMA3."""
    template = """You are NotesGPT, an AI language model skilled at taking detailed, concise, and easy-to-understand notes on 
                various subjects in bullet-point format. When provided with a passage or a topic, your task is to:
                Create advanced bullet-point notes summarizing the important parts of the reading or topic.
                Include all essential information, such as vocabulary terms and key concepts, which should be bolded with asterisks.
                Remove any extraneous language, focusing only on the critical aspects of the passage or topic.
                Strictly base your notes on the provided information, without adding any external information.
                Provide response in markdown code for easy documentation. 
                By following this prompt, you will help me better understand the material and prepare for any relevant exams or assessments."""
    
    logging.info(f"Sending a chunk to the model: {model} chunk: {prompt[:100]}")
    start_time = time.time()
    response = ollama.generate(model=model, prompt=prompt, system=template)
    end_time = time.time()
    logging.info(f"Received response from the model in {end_time - start_time:.2f} seconds.")
    return response['response']

def process_transcript(file_path, model, max_tokens, output_path):
    """Reads a transcript file, splits it, and generates notes."""
    logging.info(f"Reading transcript from {file_path}.")
    with open(file_path, 'r') as file:
        transcript = file.read()
    start_time = time.time()
    chunks = split_text(transcript, max_tokens)
    notes = []

    with open(output_path, 'w') as output_file:
        for i, chunk in enumerate(chunks):
            logging.info(f"Processing chunk {i+1}/{len(chunks)}.")
            note = query_gpt(chunk, model)
            output_file.write(note + '\n\n')
            output_file.flush()  # Ensure the note is written to disk immediately

    end_time = time.time()
    logging.info(f"Finished processing all chunks in {end_time - start_time:.2f} seconds.")
    return notes

def save_notes(notes, output_path):
    """Saves the generated notes to a markdown file."""
    logging.info(f"Saving notes to {output_path}.")
    with open(output_path, 'w') as file:
        for note in notes:
            file.write(note + '\n\n')
    logging.info(f"Notes successfully saved to {output_path}.")

if __name__ == "__main__":
    input_file = "./transcript.txt"  # Replace with your transcript file path
    output_file = "./notes.md"       # Replace with desired output file path

    logging.info("Starting the transcript processing script.")
    notes = process_transcript(input_file, "phi3:14b", 512, output_file)
    logging.info("Transcript processing script finished.")
