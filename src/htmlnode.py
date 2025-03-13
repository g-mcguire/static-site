from textnode import TextNode, TextType

class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        strings = []
        if not self.props:
            return '' 
        for k in self.props.keys():
            strings.append(f"{k}=\"{self.props[k]}\"")
        return " " + (" ").join(strings)

    def __eq__(self):
        pass

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"
    

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag, value, None, props)
        self.tag = tag
        self.value = value
        self.props = props

    def to_html(self):
        if self.value is None:
            raise ValueError("Leaf node must have value")
        if not self.tag:
            return self.value
        html_tag = f"<{self.tag}{super().props_to_html()}>{self.value}</{self.tag}>"
        return html_tag

    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
        self.tag = tag
        self.children = children
        self.props = props

    def to_html(self):
        if not self.tag:
            raise ValueError("Tag is required for any object node")
        if not self.children:
            raise ValueError(f"ParentNode with tag '{self.tag}' has no children")
        else:
            subtree_html = ''
            for child in self.children:
                subtree_html += child.to_html()
            return f"<{self.tag}>{subtree_html}</{self.tag}>"
        

def text_node_to_html_node(text_node):
    match (text_node.text_type):
        case (TextType.NORMAL_TEXT):
            return LeafNode(None, text_node.text)
        case (TextType.BOLD_TEXT):
            return LeafNode("b", text_node.text)
        case (TextType.ITALIC_TEXT):
            return LeafNode("i", text_node.text)
        case (TextType.CODE_TEXT):
            return LeafNode("code", text_node.text)
        case (TextType.LINK):
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case (TextType.IMAGE):
            return LeafNode("img", '', {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("Invalid text type")
        