# Source: https://github.com/readthedocs/readthedocs.org/issues/1846#issuecomment-477184259

# Workaround to install and execute git-lfs on Read the Docs
import os
import subprocess

LFS_VERSION = "v3.6.1"
LFS_DIR = "git-lfs-extracted"
LFS_TARBALL = f"git-lfs-linux-amd64-{LFS_VERSION}.tar.gz"
LFS_URL = f"https://github.com/git-lfs/git-lfs/releases/download/{LFS_VERSION}/{LFS_TARBALL}"

if not os.path.exists(os.path.join(LFS_DIR, 'git-lfs')):
    print("Downloading Git LFS...")
    os.system(f"wget {LFS_URL}")
    os.makedirs(LFS_DIR, exist_ok=True)
    os.system(f"tar -xvf {LFS_TARBALL} -C {LFS_DIR}")
    os.remove(LFS_TARBALL)

    # Add git-lfs to PATH for subprocesses
    extracted_path = os.path.join(LFS_DIR, "git-lfs-3.6.1")
    git_lfs_binary = os.path.join(extracted_path, "git-lfs")
    os.environ["PATH"] = extracted_path + ":" + os.environ["PATH"]

    print("Installing Git LFS...")
    subprocess.run(["git-lfs", "install"], check=True)

    print("Fetching LFS content...")
    subprocess.run(["git-lfs", "fetch"], check=True)

    print("Checking out LFS objects...")
    subprocess.run(["git-lfs", "checkout"], check=True)
