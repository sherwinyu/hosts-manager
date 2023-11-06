import subprocess
import os
import openai



hosts = """
Wikipedia:
    wikipedia:
    wikipedia.org
    www.wikipedia.org
    en.wikipedia.org
    m.en.wikipedia.org

LearnedLeague:
    learnedleague.com
    www.learnedleague.com

Facebook:
    facebook.com
    www.facebook.com

Instagram:
    instagram.com
    www.instagram.com

Reddit:
    reddit.com
    www.reddit.com

Twitter:
    twitter.com
    www.twitter.com

Youtube:
    youtube.com
    www.youtube.com

Hacker News:
    news.ycombinator.com
    www.news.ycombinator.com

Tiktok:
    tiktok.com
    www.tiktok.com
"""


import openai
openai.api_key = api_key
openai.Model.list()
completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)


def parse_block_groups(block_groups_str):
    groups = [
        [l.strip() for l in g.split('\n') if l]
        for g in block_groups_str.split('\n\n')]
    # for g in groups:
    #     key = group[0]
    #     rest = group[1:]
    return {g[0]: g[1:] for g in groups}

def select_item(items):
    input = [bytes(i, 'utf-8') for i in items]
    result = subprocess.run('fzf', input=input)

x = parse_block_groups(hosts)
print(x)
