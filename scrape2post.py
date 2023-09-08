# Scrape > NLP paraphrase > summarize > Post on wp blog or other medium.
import nltk
import torch
from newspaper import Article
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from sentence_splitter import SentenceSplitter, split_text_into_sentences
import warnings
import requests
import base64
import json
import click
import os
import configparser

# Comment out this code to output warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sentence_splitter")

@click.group()
def cli():
    pass

def init_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

@cli.command()
@click.option('--url', help='Target article URL to scrape')
def scrape_and_post(url):
    config = init_config()

    if 'WordPress' not in config:
        click.echo('Wordpress credentials are not set. Use the "set-credentials" command to save them.')
        return
    
    wp_username = config['WordPress']['Username']
    wp_password = config['WordPress']['Password']
    wp_url = config['WordPress']['URL']

    # Scrape article using newspaper
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    #  Extract content
    title = article.title
    body = article.text
    summary = article.summary
    keywords = article.keywords

    # Initialize Pegasus model and tokenizer
    model_name = "tuner007/pegasus_paraphrase"
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch_device)

    # Define paraphraser() 
    def get_paraphrase(input_text: str, num_return_sequences: int) -> list[str]:
        inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True, max_length=60)
        translated = model.generate(**inputs, max_length=60,num_beams=10, num_return_sequences=num_return_sequences)
        tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
        return tgt_text

    # Paraphrase title
    paraphrased_title = get_paraphrase(title, 1)

    # Split body into batched sentences and vice versa
    sentence_splitter = SentenceSplitter(language='en')
    sentences = sentence_splitter.split(body)

    # Initialize a list to store paraphrased sentences
    paraphrased_sentences = []

    # Paraphrase each sentence
    for sentence in sentences:
        paraphrased_sentence = get_paraphrase(sentence, 1)
        # Check if paraphrased_sentence is a list and join it into a single string
        if isinstance(paraphrased_sentence, list):
            paraphrased_sentence = ' '.join(paraphrased_sentence)
        paraphrased_sentences.append(paraphrased_sentence)

    # Join the paraphrased sentences into a single string
    paraphrased_text = ' '.join(paraphrased_sentences)
    paraphrased_title = ' '.join(paraphrased_title)

    ##print('Para-Title: %s' % paraphrased_title)
    ##print('Para-Body: %s' % paraphrased_text)
    ##print('Summary: %s' % summary)
    ##print('Keywords: %s' % keywords)

    # Initialize wp client
    creds = f"{wp_username}:{wp_password}"
    cred_token = base64.b64encode(creds.encode())
    header = {'Authorization': 'Basic ' + cred_token.decode('utf-8')}
    destination_url = f"{wp_url}"

    post = {
     'title' : paraphrased_title,
     'content' : paraphrased_text,
     'status' : 'draft', 
     }

    blog = requests.post(destination_url + '/posts' , headers=header , json=post)


    status_code = blog.status_code
    if status_code == 201:
        print("Post created successfully.")
        print(summary)
    else:
        print(f"Error: {status_code}")
        print(blog.text)

@cli.command()
def set_credentials():
    config = init_config()

    wp_username = click.prompt('Enter WP Username:')
    wp_password = click.prompt('Enter WP App Password:', hide_input=True)
    wp_url = click.prompt('Enter WP json URL:')

    config['WordPress'] = {
        'Username': wp_username,
        'Password': wp_password,
        'URL':wp_url
    }

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

    click.echo('Credentials saved successfully.')

if __name__ == '__main__':
    cli()
