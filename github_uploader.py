import datetime

from git import Repo
from templater import generate_index

def update_website():
    repo = Repo('.')
    current_branch = repo.active_branch

    try:
        print('Generating index.html...')
        repo.heads['master'].checkout()
        generate_index()

        print('Adding to branch gh-pages...')
        repo.heads['gh-pages'].checkout()
        repo.index.add(['index.html', 'index.css', 'photos'], force=True)
        repo.index.commit(str.format('Updated at {}', str(datetime.datetime.now())))

        print('Pushing...')
        repo.remotes['origin'].push()
        print('Pushed.')
    except Exception as e:
        print(str.format('Could not update the website. Encountered error {}', e))
    finally:
        current_branch.checkout()

update_website()
