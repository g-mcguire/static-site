from textnode import TextNode, TextType
from htmlnode import *
import re

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.NORMAL_TEXT:
            new_nodes.append(node)
        elif node.text_type == TextType.NORMAL_TEXT:
            segments = node.text.split(delimiter)
            if not validate_syntax(segments):
                raise Exception("Markdown syntax invalid")
            for i, segment in enumerate(segments):
                if segment:
                    if i % 2 == 0:
                        new_nodes.append(TextNode(segment, TextType.NORMAL_TEXT))
                    else:
                        new_nodes.append(TextNode(segment, text_type))
    old_nodes = new_nodes    
    return old_nodes 

def validate_syntax(nodes):
    return len(nodes) % 2 == 1

def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    final_nodes = []
    for node in old_nodes:
        images = extract_markdown_images(node.text)
        if len(images) == 0:
            final_nodes.append(node)
        else:
            current_nodes = [node]
            for image in images:
                img_alt, img_url = image[0], image[1]
                result_nodes = []
                for node in current_nodes:
                    if node.text_type == TextType.NORMAL_TEXT:
                        split_nodes = node.text.split(f"![{img_alt}]({img_url})", 1)
                        if len(split_nodes) == 1:
                            result_nodes.append(node)
                            continue    
                        if split_nodes[0] != '':
                            result_nodes.append(TextNode(split_nodes[0], TextType.NORMAL_TEXT))
                        result_nodes.append(TextNode(img_alt, TextType.IMAGE, img_url))
                        if split_nodes[1] != '':
                            result_nodes.append(TextNode(split_nodes[1], TextType.NORMAL_TEXT))
                    else:
                        result_nodes.append(node)
                current_nodes = result_nodes
            final_nodes.extend(current_nodes)
    return final_nodes

def split_nodes_link(old_nodes):
    final_nodes = []
    for node in old_nodes:
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            final_nodes.append(node)
        else:
            current_nodes = [node]
            for link in links:
                link_txt, link_url = link[0], link[1]
                result_nodes = []
                for node in current_nodes:
                    if node.text_type == TextType.NORMAL_TEXT:
                        split_nodes = node.text.split(f"[{link_txt}]({link_url})", 1)
                        if len(split_nodes) == 1:
                            result_nodes.append(node)
                            continue    
                        if split_nodes[0] != '':
                            result_nodes.append(TextNode(split_nodes[0], TextType.NORMAL_TEXT))
                        result_nodes.append(TextNode(link_txt, TextType.LINK, link_url))
                        if split_nodes[1] != '':
                            result_nodes.append(TextNode(split_nodes[1], TextType.NORMAL_TEXT))
                    else:
                        result_nodes.append(node)
                current_nodes = result_nodes
            final_nodes.extend(current_nodes)
    return final_nodes

def text_to_textnodes(text):
    delim_matcher = {
        "**": TextType.BOLD_TEXT,
        "*": TextType.ITALIC_TEXT,
        "_": TextType.ITALIC_TEXT,
        "`": TextType.CODE_TEXT
    }
    nodes = [TextNode(text, TextType.NORMAL_TEXT)]
    for delim in delim_matcher.keys():
        delimited_nodes = split_nodes_delimiter(nodes, delim, delim_matcher[delim])
        nodes = delimited_nodes
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_image(nodes)

    return nodes

def markdown_to_blocks(markdown):
    print(f"DEBUG - Original markdown: {repr(markdown)}")
    pattern = r"\n\s*\n"
    blocks = re.split(pattern, markdown)
    processed_blocks = [block.strip() for block in blocks if block.strip() != ""]
    print(f"DEBUG - Blocks after splitting: {processed_blocks}")
    return processed_blocks

def determine_block_type(block):
    lines = block.strip().split('\n')
    if len(lines) >= 2 and lines[0].strip() == '```' and lines[-1].strip() == '```':
        return "code"
    header_pattern = r"^(#{1,6})\s(.+)$"
    if re.match(header_pattern, block):
        return "heading"
    quote_pattern = r"^>\s*.*"
    if re.match(quote_pattern, block):
        return "quote"
    if block and block[0] in {"-", "*", "+"}:
        if len(block) > 1 and block[1] == " ":
            return "unordered_list"
    if block and re.match(r"^\d+\.\s", block.strip().split("\n")[0]):
        return "ordered_list"
    #ordered_list_pattern = r"^((\d+)\.\s.*\n?)+$"
    #if re.match(ordered_list_pattern, block):
    #    
    #        return "ordered_list" 
    return "paragraph"
    

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    block_nodes = []

    for block in blocks:
        if not block.strip():
            continue
        block_type = determine_block_type(block)

        match block_type:
            case "paragraph":
                block_node = create_paragraph_node(block)
            case "heading":
                block_node = create_heading_node(block)
            case "code":
                block_node = create_code_block(block)
            case "unordered_list":
                block_node = create_unordered_list_node(block)
            case "ordered_list":
                block_node = create_ordered_list_node(block)
            case "quote":
                block_node = create_quote_node(block)
            case _:
                continue

        block_nodes.append(block_node)

    if not block_nodes:
        print("Warning: No block nodes created")
    parent_node = ParentNode("div", block_nodes)
    return parent_node

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for t_node in text_nodes:
        html_node = text_node_to_html_node(t_node)
        html_nodes.append(html_node)

    return html_nodes

def create_code_block(block):
    block_lines = block.strip().split("\n")
    code_content = "\n".join([line.lstrip() for line in block_lines[1:-1]]) + "\n"
    text_node = TextNode(code_content, TextType.CODE_TEXT)
    code_html_node = text_node_to_html_node(text_node)
    pre_node = ParentNode("pre", [code_html_node])

    return pre_node

def create_paragraph_node(block):
    content = re.sub(r'\s+', ' ', block.strip())
    children = text_to_children(content)
    if not children:
        children = [LeafNode("text", content)]
    print(f"Paragraph children: {children}")
    return ParentNode("p", children)

def create_heading_node(block):
    match = re.match(r"^(#+)\s+(.*)", block)
    if not match:
        return None
    level = len(match.group(1))
    content = match.group(2).strip()

    children = text_to_children(content)
    return ParentNode(f"h{level}", children)

def create_unordered_list_node(block):
    list_items = []
    for line in block.strip().split("\n"):
        if not line.strip():
            continue
        match = re.match(r"^\s*[-*+]\s+(.*)", line)
        if match: 
            item_content = match.group(1)
            if item_content:
                item_children = text_to_children(item_content)
                list_items.append(ParentNode("li", item_children))

    return ParentNode("ul", list_items)

def create_ordered_list_node(block):
    list_items = []
    for line in block.strip().split("\n"):
        if not line.strip():
            continue
        match = re.match(r"^\s*\d+\.\s+(.*)", line)
        if match: 
            item_content = match.group(1)
            if item_content:
                item_children = text_to_children(item_content)
                list_items.append(ParentNode("li", item_children))

    return ParentNode("ol", list_items)

def create_quote_node(block):
    print(f"DEBUG - Quote block received: {repr(block)}")

    lines = []
    for line in block.strip().split("\n"):
        print(f"DEBUG - Processing line: {repr(line)}") 
        line = line.strip()
        if line.startswith(">"):
            line = line[1:].strip()
            print(f"DEBUG - Line after removing '>': {repr(line)}")
        lines.append(line)
        

    content = " ".join(lines)
    print(f"DEBUG - Final content for quote: {repr(content)}")

    content = re.sub(r"\s+", " ", content).strip()
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def extract_title(markdown):
    first_line = markdown.split("\n")[0]
    if not first_line.startswith("# "):
        raise Exception("No h1 header detected.")
    title = first_line.lstrip("# ").rstrip()
    return title

"""
if __name__ == "__main__":
    # Test text_to_children
    test_text = "This is **bold** and *italic* text with `code`"
    children = text_to_children(test_text)
    print(f"Children count: {len(children)}")
    for i, child in enumerate(children):
        print(f"Child {i}: {type(child).__name__}, content: {getattr(child, 'value', 'No value')}")
"""
