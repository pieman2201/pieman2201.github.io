from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown2 import Markdown
from glob import glob
from datetime import datetime
import string
import re
import os.path

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


def color_about(text):
    terms = ['']
    for char in text:
        if char not in string.punctuation + ' ':
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
    with open('raw_portfolio') as raw:
        content = raw.read()
        items = content.split('\n=\n')
        return [{
            'name': item.split('\n')[0],
            'tech': process_tech(item.split('\n')[1]),
            'summary': item.split('\n')[2]
            } for item in items]

def strip_html_tags(line):
    return re.sub(re.compile('<.*?>'), '', line)

def process_blog():
    posts = []
    for fn in sorted(glob('mkd_fun/*.md'), key = os.path.getmtime, reverse = True):
        with open(fn) as f:
            post = {}
            rendered = mkd.convert(f.read())
            post['title'] = strip_html_tags([line for line in rendered.split('\n') if '<h1>' in line][0]).strip()
            rendered = rendered.replace('<h1>', '{% block c_header %}<h1>', 1)
            rendered = rendered.replace('</h1>', '</h1>{% endblock %}{% block c_main %}', 1)
            rendered += '{% endblock %}'
            nfn = 'fun/' + ('.'.join(fn.split('.')[:-1] + ['html'])).split('/')[-1]
            post['link'] = '/' + nfn
            post['time'] = datetime.fromtimestamp(os.path.getmtime(fn)).strftime(
                    'Updated at %H:%M on <span style="display: inline-block">%b %-d %Y</span>')
            env.from_string('{% extends "base.html" %}' + rendered).stream(
                    use_header_as_title = True
                    ).dump(nfn)
            posts.append(post)
    return posts


env.get_template('home.html').stream().dump('index.html')
env.get_template('about.html').stream(
        color_function = color_about
        ).dump('about/index.html')
env.get_template('portfolio.html').stream(
        portfolio = load_portfolio()
        ).dump('portfolio/index.html')
env.get_template('fun.html').stream(
        posts = process_blog()
        ).dump('fun/index.html')
