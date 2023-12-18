import json
import os
import re
import shutil
import tum_esm_utils

root_src_path = "packages/docs/docs/api-reference-raw"
root_dst_path = "packages/docs/docs/api-reference"
repo_url = "https://github.com/tum-esm/pyra"

stdout = tum_esm_utils.shell.run_shell_command(
    f"lazydocs --output-path ./{root_src_path} --src-base-url {repo_url}/tree/main --no-watermark packages"
)

for p in ["core", "cli"]:
    if os.path.isdir(f"{root_dst_path}/{p}"):
        shutil.rmtree(f"{root_dst_path}/{p}")

dst_file_paths = [(f[:-3].replace(".", "/")) for f in os.listdir(root_src_path)]
print(dst_file_paths)

for src_path in sorted(os.listdir(root_src_path), key=len):
    dst_path = src_path[:-3].replace(".", "/") + ".mdx"

    module_dir_prefix = src_path[:-3].replace(".", "/") + "/"
    if any([f.startswith(module_dir_prefix) for f in dst_file_paths]):
        continue

    abs_src_path = os.path.join(f"{root_src_path}/{src_path}")
    abs_dst_path = os.path.join(f"{root_dst_path}/{dst_path}")
    print(f"generating: {dst_path}")

    # create parent dir
    os.makedirs(os.path.dirname(abs_dst_path), exist_ok=True)

    # transfer content
    with open(abs_src_path) as f:
        original_content = f.read()
    with open(abs_dst_path, "w") as f:
        f.write("---\nhide_table_of_contents: true\n")
        if abs_dst_path.endswith("main.mdx"):
            f.write("sidebar_position: 1\n")
        f.write("---\n\n")
        for match in re.findall(
            r'\n<a href="' + repo_url + r'/tree[^>]*>.*</a>\n',
            original_content,
            flags=re.MULTILINE,
        ):
            assert isinstance(match, str)
            original_content = original_content.replace(match, "")
        f.write(original_content)

shutil.rmtree(root_src_path)

with open(f"{root_dst_path}/_category_.json", "w") as f:
    json.dump({"label": "API Reference", "position": 6}, f)

with open(f"{root_dst_path}/core/_category_.json", "w") as f:
    json.dump({"label": "CORE", "position": 1}, f)

with open(f"{root_dst_path}/cli/_category_.json", "w") as f:
    json.dump({"label": "CLI", "position": 2}, f)
