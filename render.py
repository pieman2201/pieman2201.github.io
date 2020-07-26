from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
        loader      = FileSystemLoader('templates'),
        autoescape  = select_autoescape(['html','xml'])
        )

def color_tech_term(term):
    lt = term.lower()
    color = ''
    if 'python' in lt:
        color = 'blue'
    elif 'c' == lt:
        color = 'magenta'
    elif 'java' == lt:
        color = 'red'
    elif 'html' in lt or 'css' in lt or 'js' in lt or 'jquery' in lt:
        color = 'yellow'
    elif 'dart' in lt:
        color = 'green'
    elif 'flutter' in lt:
        color = 'cyan'
    elif 'vue' in lt:
        color = 'green'
    elif 'wordpress' in lt or 'php' in lt:
        color = 'magenta'

    return '<span class="%s">%s</span>' % (color, term)

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

env.get_template('home.html').stream().dump('index.html')
env.get_template('about.html').stream().dump('about/index.html')
env.get_template('portfolio.html').stream(
        portfolio = load_portfolio()
       ).dump('portfolio/index.html')
env.get_template('fun.html').stream().dump('fun/index.html')

