import os
def init(repo):
    os.mkdir(repo)
    os.mkdir(os.path.join(repo, '.git'))
    for name in ['objects', 'refs', 'refs/head']:
        os.mkdir(os.path.join(repo, '.git', name))
    # write_file(os.path.join(repo, '.git', 'HEAD'),b'ref: refs/heads/master')
    print('Initilaized empty repository: {}'. format(repo))

