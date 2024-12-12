#!/usr/bin/env python

import os
import shlex
import shutil
import subprocess
import sys
import tempfile

NO_PROMPT = False
REQUIRED_BINARIES = ["git", "gittuf-git", "ssh-keygen"]


def check_binaries():
    for p in REQUIRED_BINARIES:
        if not shutil.which(p):
            raise Exception(f"required command {p} not found")


def prompt_key(prompt):
    if NO_PROMPT:
        print("\n" + prompt)
        return
    inp = False
    while inp != "":
        try:
            inp = input(f"\n{prompt} -- press any key to continue")
        except Exception:
            pass


def display_command(cmd):
    print(f"[{os.getcwd()}] $ {cmd}")


def run_demo():
    current_dir = os.getcwd()
    keys_dir = "keys"

    tmp_dir = tempfile.TemporaryDirectory()
    tmp_keys_dir = os.path.join(tmp_dir.name, keys_dir)
    tmp_repo_dir = os.path.join(tmp_dir.name, "repo")

    shutil.copytree(os.path.join(current_dir, keys_dir), tmp_keys_dir)
    os.mkdir(tmp_repo_dir)

    for key in os.listdir(tmp_keys_dir):
        os.chmod(os.path.join(tmp_keys_dir, key), 0o600)

    # Clone a repository with gittuf-git
    prompt_key("Clone repository with gittuf metadata")
    os.chdir(tmp_dir.name)
    cmd = "gittuf-git clone git@github.com:example/gittuf-demo.git repo"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))
    os.chdir(tmp_repo_dir)

    # Fetch hooks and metadata
    prompt_key("Fetch RSL and policy metadata after clone")
    cmd = "gittuf-git pull"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    # Initialize repository and hooks
    prompt_key("Initialize gittuf hooks")
    cmd = "gittuf-git hooks init"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    # Add pre-commit hook
    prompt_key("Add pre-commit hook")
    with open("pre-commit", "w") as hook:
        hook.write("#!/bin/sh\necho \"Pre-commit hook triggered!\"\nexit 0")
    os.chmod("pre-commit", 0o755)

    cmd = "gittuf-git hooks add pre-commit --stage pre-commit"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    # Apply hooks metadata
    prompt_key("Apply hooks metadata")
    cmd = "gittuf-git hooks apply"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    # Verify hooks load and commit
    prompt_key("Make a commit to trigger pre-commit hook and gittuf verification")
    display_command("echo 'Hello, gittuf-git!' > README.md")
    with open("README.md", "w") as fp:
        fp.write("Hello, gittuf-git!\n")

    cmd = "gittuf-git add README.md"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    cmd = "gittuf-git commit -m 'Test commit with pre-commit hook'"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    prompt_key("Verification results printed above. Commit proceeds regardless.")

    # Record changes to RSL and push
    prompt_key("Push changes and record RSL entries")
    cmd = "gittuf-git push origin main"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    # Load and verify hooks
    prompt_key("Fetch RSL and hooks on pull")
    cmd = "gittuf-git pull"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    prompt_key("Verify pre-commit hook integrity")
    cmd = "gittuf-git hooks load"
    display_command(cmd)
    subprocess.call(shlex.split(cmd))

    print("\nDemo complete: gittuf-git hooks and metadata successfully distributed, applied, and verified!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-prompt":
            NO_PROMPT = True
    check_binaries()
    run_demo()
