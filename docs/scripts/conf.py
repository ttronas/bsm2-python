# Source: https://github.com/readthedocs/readthedocs.org/issues/1846#issuecomment-477184259

# Workaround to install and execute git-lfs on Read the Docs
import os
if not os.path.exists('./git-lfs'):
    os.system('wget https://github.com/git-lfs/git-lfs/releases/download/v2.7.1/git-lfs-linux-amd64-v2.7.1.tar.gz')
    os.system('mkdir -p git-lfs-extracted')  # create new directory
    os.system('tar xvfz git-lfs-linux-amd64-v2.7.1.tar.gz -C git-lfs-extracted')  # extract into new directory
    os.system('./git-lfs-extracted/git-lfs install')  # make lfs available in current repository
    os.system('./git-lfs-extracted/git-lfs fetch')  # download content from remote
    os.system('./git-lfs-extracted/git-lfs checkout')  # make local files to have the real content on them
