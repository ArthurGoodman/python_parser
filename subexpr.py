import readline


class BinaryNode:

    def __init__(self, left, oper, right):
        self.oper = oper
        self.left = left
        self.right = right

    def equals(self, node):
        return (isinstance(node, BinaryNode) and
                ((self.left.equals(node.left) and
                  self.right.equals(node.right)) or
                 (self.right.equals(node.left) and
                  self.left.equals(node.right))))

    def includes(self, node):
        return (self.equals(node) or
                self.left.includes(node) or
                self.right.includes(node))


class ValueNode:

    def __init__(self, value):
        self.value = value

    def equals(self, node):
        return isinstance(node, ValueNode) and self.value == node.value

    def includes(self, node):
        return self.equals(node)


class VariableNode:

    def __init__(self, name):
        self.name = name

    def equals(self, node):
        return isinstance(node, VariableNode) and self.name == node.name

    def includes(self, node):
        return self.equals(node)


class Parser:

    def __init__(self):
        self.recorded_expr = None

    def check(self, id):
        return self.t_id == id

    def accept(self, id):
        if self.check(id):
            self.get_token()
            return True

        return False

    def get_token(self):
        self.t_id = "e"
        self.t_text = ""

        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1

        if self.pos == len(self.expr):
            return
        elif self.expr[self.pos].isalpha():
            while self.pos < len(self.expr) and self.expr[self.pos].isalpha():
                self.t_text += self.expr[self.pos]
                self.pos += 1

            if len(self.t_text) == 1 and self.t_text.islower():
                self.t_id = "v"
            elif self.t_text == "true":
                self.t_id = "t"
            elif self.t_text == "false":
                self.t_id = "f"
            elif self.t_text == "or":
                self.t_id = "|"
            elif self.t_text == "and":
                self.t_id = "&"
            else:
                self.t_id = "u"
        else:
            self.t_text += self.expr[self.pos]
            self.pos += 1

            if self.t_text in "()=":
                self.t_id = self.t_text
            else:
                self.t_id = "u"

    def binary(self):
        if (self.accept('(')):
            node = self.binary()

            if self.accept("|"):
                node = BinaryNode(node, "|", self.binary())
            elif self.accept("&"):
                node = BinaryNode(node, "&", self.binary())
            else:
                raise RuntimeError(
                    "binary operator expected inside parentheses")

            if not self.accept(')'):
                raise RuntimeError("unmatched parentheses")
        else:
            node = self.term()

        return node

    def term(self):
        node = None

        if self.check("v"):
            node = VariableNode(self.t_text)
            self.get_token()
        elif self.accept("t"):
            node = ValueNode(True)
        elif self.accept("f"):
            node = ValueNode(False)
        elif self.check("u"):
            raise RuntimeError("unknown token '" + self.t_text + "'")
        elif self.check("e"):
            raise RuntimeError("unexpected end of expression")
        else:
            raise RuntimeError("unexpected token '" + self.t_text + "'")

        return node

    def parse(self, expr):
        self.expr = expr
        self.pos = 0

        try:
            self.get_token()

            record = False
            if self.t_text == "#":
                record = True
                self.get_token()

            node = self.binary()

            if not self.check("e"):
                raise RuntimeError("there's an excess part of expression")

            if self.recorded_expr is None or record:
                self.recorded_expr = node
                print("[expression recorded]")
            else:
                if self.recorded_expr.includes(node):
                    print("true")
                else:
                    print("false")

        except RuntimeError as e:
            print("error: " + str(e))


def main():
    parser = Parser()

    while True:
        line = raw_input("$ ")

        if line == "exit":
            return
        else:
            parser.parse(line)

        print("")

main()
