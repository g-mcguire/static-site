from textnode import TextNode, TextType
from inline_markdown import *
from pathlib import Path
import os, shutil

def main():
    current = Path(__file__).parent
    source_dir = current.parent / "static"
    target_dir = current.parent  / "public"
    result = copy_contents(source_dir, target_dir)

    from_path = current.parent / "content/index.md"
    dest_path = current.parent / "public/index.html"
    template_path = current.parent / "template.html"

    generate_page(from_path, template_path, dest_path)
    

def copy_contents(source_dir, target_dir):
    if not os.path.exists(source_dir):
        raise Exception("invalid source path")
    
    if os.path.isdir(source_dir):
        prep_target_dir(target_dir)

        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            target_path = os.path.join(target_dir, item)
            
            if os.path.isdir(source_path):
                copy_contents(source_path, target_path)

            elif os.path.isfile(source_path):
                shutil.copy2(source_path, target_path)

    elif os.path.isfile(source_dir):
        raise Exception("Source path points to a file, not a directory.")

def prep_target_dir(target):
    if not os.path.exists(target):
        os.makedirs(target, exist_ok=True)
        print(f"The directory at {target} was created.")
    else:
        for item in os.listdir(target):
            item_path = os.path.join(target, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print(f"The directory at {target} has been cleared.")

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using the template at {template_path}...")

    # read md and save to var
    markdown = open(from_path).read()
    title = extract_title(markdown)


    # read template and save to var
    template = open(template_path).read()

    #print(markdown)
    #print(template)


    # convert md to html w. core fxns
    content = markdown_to_html_node(markdown).to_html()
    print(content)

    filled_template = template.replace("{{ Title }}", title).replace("{{ Content }}", content)

    directory = os.path.dirname(dest_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(filled_template)

    return


if __name__ == "__main__":
    main()