import logging
import os
import ollama


class PostGenerator:
    def __init__(self, model):
        self.model = model
        self.system = """You are a PostGPT, you know how to write concise 
        and engaging LinkedIn/Twitter/Instagram posts that summarize articles 
        and entice readers to read more. Your posts should highlight the main 
        points of the content provided. Ensure the tone 
        is professional yet approachable. Include emojis. The post should 
        consist of 200 words maximum. Also include relatable SEO hashtags."""

    def generate_post(self, blog_content):
        """Generates a LinkedIn post from the given blog content using the model."""
        prompt = (
            "Generate a concise LinkedIn post summarizing the following blog content:\n\n"
            + blog_content
        )
        messages = []
        messages.append({"role": "system", "content": self.system})
        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(model=self.model, messages=messages)
        return response["message"]["content"]

    def process_blog(self, blog_file):
        """Processes a blog file to generate a LinkedIn post and save it in the same directory."""
        try:
            with open(blog_file, "r", encoding="utf-8") as bf:
                blog_content = bf.read()

            post_content = self.generate_post(blog_content)

            post_filename = os.path.basename(blog_file).replace(".md", ".post.md")
            post_filepath = os.path.join(os.path.dirname(blog_file), post_filename)
            with open(post_filepath, "w", encoding="utf-8") as pf:
                pf.write(post_content)

            logging.info(f"Saved LinkedIn post to {post_filepath}")

        except Exception as e:
            logging.error(f"Error processing blog file {blog_file}: {e}")
