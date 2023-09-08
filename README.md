# Scrape2Post
This very gray area Click tool scrapes web article content using newspaper3k, paraphrases the content using an NLP model (Hugging face - Pegasus) and posts said content to wordpress drafts using its API.
To use this tool you will need to;
a, install necessary dependencies (check import statements)
b, create a venv to work in/ avoid dependency conflicts
c, create a config.ini file to store WP credentials and URL (WP Admin Username & WP Application Key)
d, Run it with ''' python scrape2post.py set credentials ''' to set credentials
e, follow prompts and input creds, also provide destination url like so <https://your-website.com/wp-json/wp/v2>
f, Run with ''' python scrape2post.py scrape_and_post url <https://target-article-url.com>
g, Scrape2Post Click tool can also output summary, title, authors, etc of scraped article using Newspaper3k, tweak if necessary.

PS
NLP Model can be changed depending on the task, the pegasus model has its drawbaks, for instance the longer the article the more questionale the output. 

