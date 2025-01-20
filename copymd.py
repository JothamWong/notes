"""
This python3 script copies over a Obsidian markdown file and its dependent images, converting the Obsidian image links into standard markdown image links.

Intended usage:
python3 copymd.py [input_file] [output_dst]

This deals with the issue where just copying the raw markdown file by itself
means that image links are broken. It is assumed that the file is passed the input_file's path and all path namings are relative to the input_file. It also
assumes that all image files exist in an attachment_dir.

At the moment, that's all this script does, it finds the dependent image files
and adds them to the output_dir in addition to the original markdown file. It
does not deal with other internal obsidian links (such as referenced markdown files) because they don't really break the rendering.
"""
import argparse
import os
import re
import shutil

# Changed whenever appropriate
ROOT_DIR = "/Users/jotham/Personal/jotham"

def transform_image_filename(filename: str) -> str:
    """
    Common name processing to obey standard markdown image formatting rules.
    1. Images with spaces in them do not display in standard markdown
    2. Images with brackets in them do not display
    """
    return filename.replace(" ", "").replace("(", "").replace(")", "")

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input_file", type=str)
    argparser.add_argument("--attachment_dir", type=str, default=os.path.join(ROOT_DIR, "attachments"))
    argparser.add_argument("--output_dir", type=str)
    args = argparser.parse_args()
    
    input_filename = args.input_file.split("/")[-1]
    attachment_dir = args.attachment_dir
    
    output_dir = args.output_dir
    if output_dir == ".":
        output_dir = os.getcwd()
    
    # We process line by line and scan for text of the form ![[]]
    pattern = r'!\[\[(.*?)\]\]'
    input_buffer = []
    additional_files = []
    with open(args.input_file, "r") as inf:
        for line in inf.readlines():
            matches = re.findall(pattern, line)
            modified_line = line
            for match in matches:
                attachment_file_path = os.path.join(attachment_dir, match)
                additional_files.append(attachment_file_path)
                original_pattern = f"![[{match}]]"
                new_pattern = f"![title]({transform_image_filename(match)})"
                modified_line = modified_line.replace(original_pattern, new_pattern)
            input_buffer.append(modified_line)

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, input_filename), "w") as outf:
        outf.writelines(input_buffer)
    for additional_file in additional_files:
        additional_filename = additional_file.split("/")[-1]
        shutil.copy2(additional_file, os.path.join(output_dir, transform_image_filename(additional_filename)))
    