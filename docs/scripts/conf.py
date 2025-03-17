# Source: https://github.com/readthedocs/readthedocs.org/issues/1846#issuecomment-477184259

# Workaround to install and execute git-lfs on Read the Docs
import os
if not os.path.exists('./git-lfs'):
    os.system('wget https://github.com/git-lfs/git-lfs/releases/download/v3.6.1/git-lfs-linux-amd64-v3.6.1.tar.gz')
    os.system('tar xvfz git-lfs-linux-amd64-v3.6.1.tar.gz')
    os.system('./git-lfs install')  # make lfs available in current repository
    os.system('./git-lfs fetch')  # download content from remote
    os.system('./git-lfs checkout')  # make local files to have the real content on the
    os.system('./git-lfs untrack CHANGELOG.md')  # remove git lfs paths from git attributes
    os.system('./git-lfs track "*.svg"')  # track .svg files
    os.system('./git add .gitattributes')
    os.system('./git-lfs prune --force')  # delete old git lfs files from local storage
