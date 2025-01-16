import unittest

from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD_TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD_TEXT)
        self.assertEqual(node, node2)

    def test2(self):
        node = TextNode("I have no URL", TextType.ITALIC_TEXT, None)
        node2 = TextNode("I have no URL", TextType.ITALIC_TEXT)
        self.assertEqual(node, node2)

    def test_diff(self):
        node = TextNode("This is bold text", TextType.BOLD_TEXT)
        node2 = TextNode("This is an image", TextType.IMAGE)
        self.assertNotEqual(node, node2)

if __name__ == "__main__":
    unittest.main()