import unittest

from htmlnode import *
from textnode import TextType, TextNode

class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode("p", "Test", props={"style": "color:green"})
        self.assertEqual(node.tag, "p")
        self.assertEqual(node.value, "Test")
        self.assertEqual(node.children, None)
        self.assertDictEqual(node.props, {"style": "color:green"})
        self.assertEqual(node.props_to_html(), " style=\"color:green\"")

    def test_leaf(self):
        node = LeafNode("a", "leaf_test", props={"href": "https://www.google.com"})
        self.assertEqual(node.tag, "a")
        self.assertEqual(node.value, "leaf_test")
        self.assertEqual(node.children, None)
        self.assertEqual(node.to_html(), "<a href=\"https://www.google.com\">leaf_test</a>")

    def test_parent(self):
        node = ParentNode(
                "p",
                [
                    LeafNode("b", "Bold text"),
                    LeafNode(None, "Normal text"),
                    LeafNode("i", "italic text"),
                    LeafNode(None, "Normal text"),
                ],
            )

        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")
    
    def test_tagless_parent(self):
        with self.assertRaises(ValueError):
            node = ParentNode(None, [LeafNode("b", "Bold text")])
            node.to_html()

    def test_childless_parent(self):
        with self.assertRaises(ValueError):
            node = ParentNode("b", [])
            node.to_html()
        with self.assertRaises(ValueError):
            node = ParentNode("b", None)
            node.to_html()
        
    def test_nested_parents(self):
        nested_node = ParentNode(
            "div",
            [
                ParentNode(
                    "p",
                    [LeafNode("span", "Hello world!")]
                )
            ]
        )
        self.assertEqual(nested_node.to_html(), "<div><p><span>Hello world!</span></p></div>")

        complex_node = ParentNode(
            "section",
            [
                ParentNode(
                    "header",
                    [LeafNode("h1", "Title")]
                ),
                ParentNode(
                    "nav",
                    [
                        LeafNode("a", "Link 1"),
                        LeafNode("a", "Link 2")
                    ]
                ),
                ParentNode(
                    "footer",
                    [LeafNode("p", "Copyright")]
                )
            ]
        )
        html_string = "<section><header><h1>Title</h1></header><nav><a>Link 1</a><a>Link 2</a></nav><footer><p>Copyright</p></footer></section>"
        self.assertEqual(complex_node.to_html(), html_string)
    
    def test_node_conversions(self):
        node = TextNode("normal", TextType.NORMAL_TEXT)
        converted_normal = text_node_to_html_node(node)
        self.assertIsInstance(converted_normal, LeafNode)
        self.assertEqual(converted_normal.to_html(), "normal")

        bold_node = TextNode("bold", TextType.BOLD_TEXT)
        converted_bold = text_node_to_html_node(bold_node)
        self.assertIsInstance(converted_bold, LeafNode)
        self.assertEqual(converted_bold.to_html(), "<b>bold</b>")

        italic_node = TextNode("italic", TextType.ITALIC_TEXT)
        converted_italic = text_node_to_html_node(italic_node)
        self.assertIsInstance(converted_italic, LeafNode)
        self.assertEqual(converted_italic.to_html(), "<i>italic</i>")
        
        code_node = TextNode("code_block", TextType.CODE_TEXT)
        converted_code = text_node_to_html_node(code_node)
        self.assertIsInstance(converted_code, LeafNode)
        self.assertEqual(converted_code.to_html(), "<code>code_block</code>")

        link_node = TextNode("link_test", TextType.LINK, "https://www.google.com")
        converted_link = text_node_to_html_node(link_node)
        self.assertDictEqual(converted_link.props, {
            "href": "https://www.google.com"
        })
        self.assertIsInstance(converted_link, LeafNode)
        self.assertEqual(converted_link.to_html(), "<a href=\"https://www.google.com\">link_test</a>")

        image_node = TextNode("alt_text", TextType.IMAGE, "https://example.com")
        converted_image = text_node_to_html_node(image_node)
        self.assertDictEqual(converted_image.props, {
            "src": "https://example.com",
            "alt": "alt_text"
        })
        self.assertIsInstance(converted_image, LeafNode)
        self.assertEqual(converted_image.to_html(), "<img src=\"https://example.com\" alt=\"alt_text\"></img>")