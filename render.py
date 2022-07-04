from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown2 import Markdown
from pathlib import Path
from datetime import datetime
import re
import os
import shutil


env = Environment(
        loader      = FileSystemLoader('templates'),
        autoescape  = select_autoescape(['html','xml']),
        )
mkd = Markdown(extras=['fenced-code-blocks', 'tables'])

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
            'go',
            ],
        'blue':     [
            'python',
            'css',
            'wordpress',
            'typescript',
            ],
        'magenta':  [
            'c',
            'php',
            'sass',
            ]
        }

act_cm = {k: v for d in [{val: key for val in vals} for key, vals in COLOR_MAP.items()] for k, v in d.items()}
punct  = '!"#$%&\'()*+-,./:;<=>?@[\\]^`{|}~ _\n'

def color_about(text):
    terms = ['']
    for char in text:
        if char not in punct:
            terms[-1] += char
        else:
            terms.append(char)
            if char == "/":
                terms.append('<wbr>')
            terms.append('')
    return ''.join([color_tech_term(term) for term in terms])

def color_tech_term(term):
    color = act_cm.get(term.lower(), '')
    return ('<span class="%s">%s</span>' % (color, term)) if len(color) else term

def extract_first_image(html_str):
    try:
        return html_str.split('<img')[1].split("src=\"")[1].split('"')[0]
    except:
        return None

env.globals.update({
    "color_function": color_about,
    "extract_first_image": extract_first_image,
    })

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
        shutil.copytree(folder.path, 'docs/other/' + folder.name)


        markdown_files = list(Path('docs/other/' + folder.name).rglob('*.md'))
        for file in markdown_files:
            with file.open() as f:
                post = {}
                rendered = mkd.convert(f.read())
                post['title'] = strip_html_tags([line for line in rendered.split('\n') if '<h1>' in line][0]).strip()

                rendered = process_raw_html(rendered)
                post['link'] = '/other/' + folder.name
                post['time'] = datetime.fromtimestamp(os.path.getmtime(folder.path)).strftime(
                    'Updated at %H:%M on <span style="display: inline-block">%b %-d %Y</span>')

                if str(file) == 'docs/other/' + folder.name + '/index.md':
                    posts.append(post)

                html_name = '.'.join(file.name.split('.')[:-1] + ['html'])

                env.from_string('{% extends "base.html" %}' + rendered).stream(
                        use_header_as_title = True
                        ).dump(str(file.parent) + '/' + html_name)

    return posts



shutil.rmtree('docs')
os.mkdir('docs')
os.mkdir('docs/experience')
os.mkdir('docs/portfolio')
os.mkdir('docs/trivia')
os.mkdir('docs/contact')
os.mkdir('docs/other')
shutil.copy('sources/style.css', 'docs')
shutil.copy('sources/style.css.map', 'docs')
shutil.copy('sources/resume.pdf', 'docs')
shutil.copy('sources/CNAME', 'docs')
shutil.copy('sources/sitemap.txt', 'docs')
shutil.copy('sources/.nojekyll', 'docs')
shutil.copytree('sources/icons', 'docs/icons')


def load(template):
    template = env.get_template(template)
    return template

load('home.html').stream().dump('docs/index.html')
load('trivia.html').stream().dump('docs/trivia/index.html')
load('portfolio.html').stream().dump('docs/portfolio/index.html')
load('experience.html').stream().dump('docs/experience/index.html')
load('contact.html').stream().dump('docs/contact/index.html')
load('other.html').stream(
        posts = process_blog()
        ).dump('docs/other/index.html')
