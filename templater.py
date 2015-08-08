from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('resources'))
template = env.get_template('index_template.html')
rendered = template.render(test='hello')

with open('resources/index.html', 'w+') as f:
    f.write(rendered)
