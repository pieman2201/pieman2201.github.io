from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown2 import Markdown
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from wordcloud import WordCloud
from colour import Color
from nltk.corpus import stopwords
import re
import os
import shutil

env = Environment(
        loader      = FileSystemLoader('templates'),
        autoescape  = select_autoescape(['html','xml'])
        )
mkd = Markdown()

COLOR_MAP = {
        'red':      [
            'java',
            'materialize',
            ],
        'orange':   [
            'html',
            ],
        'yellow':   [
            'js',
            ],
        'green':    [
            'vue',
            'android',
            ],
        'cyan':     [
            'flutter',
            'jquery',
            ],
        'blue':     [
            'python',
            'css',
            'wordpress',
            ],
        'magenta':  [
            'c',
            'php',
            'sass',
            ]
        }

act_cm = {k: v for d in [{val: key for val in vals} for key, vals in COLOR_MAP.items()] for k, v in d.items()}
punct  = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '

def color_about(text):
    terms = ['']
    for char in text:
        if char not in punct:
            terms[-1] += char
        else:
            terms.append(char)
            terms.append('')
    return ''.join([color_tech_term(term) for term in terms])

def color_tech_term(term):
    color = act_cm.get(term.lower(), '')
    return ('<span class="%s">%s</span>' % (color, term)) if len(color) else term

def process_tech(tech):
    tech_terms = tech.split('/')
    return '/<wbr>'.join([color_tech_term(term) for term in tech_terms])

def load_portfolio():
    with open('sources/raw_portfolio') as raw:
        content = raw.read()
        items = content.split('\n=\n')
        return [{
            'name': item.split('\n')[0],
            'tech': process_tech(item.split('\n')[1]),
            'summary': item.split('\n')[2]
            } for item in items]

def strip_html_tags(line):
    return re.sub(re.compile('<.*?>'), '', line)

def process_raw_html(rendered):
    rendered = rendered.replace('<h1>', '{% block c_header %}<h1>', 1)
    rendered = rendered.replace('</h1>', '</h1>{% endblock %}{% block c_main %}', 1)
    rendered += '{% endblock %}'
    return rendered


def process_blog():
    posts = []
    for folder in sorted(
            [f for f in os.scandir('markdown') if f.is_dir()],
            key = os.path.getmtime, reverse = True
            ):
        shutil.copytree(folder.path, 'docs/fun/' + folder.name)


        markdown_files = list(Path('docs/fun/' + folder.name).rglob('*.md'))
        for file in markdown_files:
            with file.open() as f:
                post = {}
                rendered = mkd.convert(f.read())
                post['title'] = strip_html_tags([line for line in rendered.split('\n') if '<h1>' in line][0]).strip()

                rendered = process_raw_html(rendered)
                post['link'] = '/fun/' + folder.name
                post['time'] = datetime.fromtimestamp(os.path.getmtime(folder.path)).strftime(
                    'Updated at %H:%M on <span style="display: inline-block">%b %-d %Y</span>')

                if str(file) == 'docs/fun/' + folder.name + '/index.md':
                    posts.append(post)

                html_name = '.'.join(file.name.split('.')[:-1] + ['html'])

                env.from_string('{% extends "base.html" %}' + rendered).stream(
                        use_header_as_title = True
                        ).dump(str(file.parent) + '/' + html_name)

    return posts



shutil.rmtree('docs')
os.mkdir('docs')
os.mkdir('docs/about')
os.mkdir('docs/portfolio')
os.mkdir('docs/fun')
os.mkdir('docs/clouds')
shutil.copy('sources/style.css', 'docs')
shutil.copy('sources/pfp.jpeg', 'docs')
shutil.copy('sources/CNAME', 'docs')


def load(template):
    template = env.get_template(template)
    return template

load('home.html').stream().dump('docs/index.html')
load('about.html').stream(
        color_function = color_about
        ).dump('docs/about/index.html')
load('portfolio.html').stream(
        portfolio = load_portfolio()
        ).dump('docs/portfolio/index.html')
load('fun.html').stream(
        posts = process_blog()
        ).dump('docs/fun/index.html')


def get_word_tallies():
    tallies = {}
    html_files = list(Path('docs/').rglob('*.html'))
    for file in html_files:
        with file.open() as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            content = soup.find(id = 'content-main')
            text = ''.join([c if c not in punct + '\n' else ' ' for c in str(content.text)])
            for term in text.split(' '):
                if len(term) > 2 and term not in stopwords.words('english'):
                    tallies[term.lower()] = tallies.get(term.lower(), 0) + 1
    return tallies

def get_color_gradient(start, stop, steps):
    colors = []
    for x in range(steps):
        start_part = [(steps - x - 1) * v for v in start.rgb]
        stop_part  = [x * v for v in stop.rgb]
        combined = [sum(p) / (steps - 1) for p in zip(start_part, stop_part)]
        colors.append(combined)
    return colors

def create_svg_from_tallies(tallies):
    max_tally = max(tallies.values())
    text = ''.join([(word + ' ') * tallies[word] for word in sorted(tallies.keys(), key = lambda x: tallies[x])])
    start_color = Color("#7cafc2")
    stop_color  = Color("#d8d8d8")
    gradient = get_color_gradient(start_color, stop_color, max_tally)
    height = 512
    for r in range(1, 50):
        ratio = r / 10
        width = int(height * ratio)
        wordcloud = WordCloud(
                width = width, height = height,
                color_func = lambda word, *args, **kwargs: Color(rgb=gradient[tallies[word] - 1]),
                normalize_plurals = False,
                collocations = False,
                background_color = "#181818"
                ).generate(text)
        with open('docs/clouds/cloud-%.1f.svg' % ratio, 'w') as f:
            f.write(wordcloud.to_svg())


create_svg_from_tallies(get_word_tallies())


