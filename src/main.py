from textnode import TextNode, TextType

def main():
    test = TextNode("What's good?", TextType.BOLD_TEXT, "https://www.boot.dev")
    print(test)

main()