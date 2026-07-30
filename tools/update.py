#!/usr/bin/env python3
from glob import glob
import json
from packaging import version
from lastversion import latest
from urllib.request import urlretrieve
from filehash import FileHash

dirs = glob("./*/version.json")
for path in dirs:
    with open(path) as file:
        data = json.load(file)

        repo = data["repo"]
        v = data["version"]
        
        print(f"Checking {repo} {v}")
        latest_version = latest(repo=repo, output_format="dict")
        
        if latest_version["version"] > version.parse(v):
            print(f'{repo} has newer version: {latest_version["version"]} (from: {v})')
            url = f'https://github.com/{repo}/archive/refs/tags/{latest_version["tag_name"]}.tar.gz'
            tmp_path, headers = urlretrieve(url)
            hs = FileHash("sha256")
            hash = hs.hash_file(tmp_path)
            data["url"] = url
            data["sha256"] = hash
            data["version"] = latest_version["version"]
            print(f'Updated: "{url}" "{hash}"')
            with open(path, "w") as ofile:
                json.dump(data, ofile, indent=2)
        else:
            print(f"{repo} has no update available")