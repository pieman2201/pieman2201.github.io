from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
        loader      = FileSystemLoader('templates'),
        autoescape  = select_autoescape(['html','xml'])
        )

env.get_template('index.html').stream().dump('index.html')
env.get_template('about.html').stream().dump('about/index.html')
env.get_template('portfolio.html').stream().dump('portfolio/index.html')
env.get_template('fun.html').stream().dump('fun/index.html')

