"""Create a review-only fix branch for one allowlisted deterministic patch.

Explicit workflow_dispatch only; never commit to main or automatically merge.
"""
import os
import subprocess
from pathlib import Path
from dropship.v83_repair_proposals import ALLOWED_WORKFLOW
from dropship.v84_patch_validation import validate_and_diff

def run():
    target=Path(ALLOWED_WORKFLOW)
    diagnosis={"findings":[{"category":"python_import"}]}
    original=target.read_text(encoding="utf-8")
    proposal=validate_and_diff(diagnosis,{ALLOWED_WORKFLOW:original})
    if proposal["status"]!="patch_validated":
        print("No safe known patch needed; leaving repository unchanged.")
        return
    from dropship.v83_repair_proposals import OLD_COMMAND,NEW_COMMAND
    assert original.count(OLD_COMMAND)==1
    name="autofix/shadow-import-"+os.environ["GITHUB_RUN_ID"]
    def git(*args):
        return subprocess.run(["git",*args],check=True)
    git("switch","-c",name)
    target.write_text(original.replace(OLD_COMMAND,NEW_COMMAND,1),encoding="utf-8")
    git("add","--",ALLOWED_WORKFLOW)
    git("-c","user.name=github-actions[bot]","-c","user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit","-m","fix: restore Shadow Collect import path (review only)")
    git("push","origin","HEAD:refs/heads/"+name)
    print("Created review-only branch:",name)
if __name__=="__main__":
    run()
