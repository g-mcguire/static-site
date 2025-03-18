from textnode import TextNode, TextType
from inline_markdown import *
from pathlib import Path
import os, shutil, sys

def main():
    basepath = "/"
    if sys.argv:
        basepath = sys.argv[0]
    
    current = Path(__file__).parent
    source_dir = current.parent / "static"
    target_dir = current.parent  / "docs"
    #target_dir = current.parent  / "public"
    copy_contents(source_dir, target_dir)

    from_path = current.parent / "content/"
    dest_path = current.parent / "public/"
    template_path = current.parent / "template.html"

    generate_pages_recursive(from_path, template_path, dest_path, basepath)
    #generate_page(from_path, template_path, dest_path)
    

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

def generate_page(from_path, template_path, dest_path, basepath):
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
    #print(content)

    filled_template = template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    pathed_template = filled_template.replace("href=\"/", f"href=\"{basepath}").replace("src=\"/", f"src=\"{basepath}")

    directory = os.path.dirname(dest_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(dest_path, "w") as f:
        f.write(pathed_template)

    return

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    if not os.path.exists(dir_path_content):
        raise Exception("Source directory does not exist")
    
    for item in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item)

        if os.path.isdir(source_path):
            os.makedirs(dest_path, exist_ok=True)
            generate_pages_recursive(source_path, template_path, dest_path, basepath)

        elif os.path.isfile(source_path) and source_path.endswith(".md"):
            html = populate_template(source_path, template_path, basepath)
            filename, ext = os.path.splitext(item)
            new_filename = filename + ".html"
            new_path = os.path.join(dest_dir_path, new_filename)

            with open(new_path, 'w') as f:
                f.write(html) 
    return

def populate_template(markdown_path, template_path, basepath):
    markdown = open(markdown_path).read()
    title = extract_title(markdown)

    template = open(template_path).read()
    content = markdown_to_html_node(markdown).to_html()
    filled_template = template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    pathed_template = filled_template.replace("href=\"/", f"href=\"{basepath}").replace("src=\"/", f"src=\"{basepath}")
    return pathed_template





if __name__ == "__main__":
    main()