class BinaryNode:

    def __init__(self, left, oper, right):
        self.oper = oper
        self.left = left
        self.right = right

    def eval(self, context):
        return {
            "|": self.left.eval(context) or self.right.eval(context),
            "&": self.left.eval(context) and self.right.eval(context),
        }.get(self.oper, None)


class ValueNode:

    def __init__(self, value):
        self.value = value

    def eval(self, context):
        return self.value


class VariableNode:

    def __init__(self, name):
        self.name = name

    def eval(self, context):
        if self.name not in context:
            raise RuntimeError("undefined variable '" + self.name + "'")

        return context[self.name]


class AssignmentNode:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def eval(self, context):
        value = self.value.eval(context)
        context[self.name] = value
        return value


class Parser:

    def __init__(self):
        self.context = {}

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

            if len(self.t_text) == 1:
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

    def assign(self):
        node = self.logic_or()

        if self.accept("="):
            if not(isinstance(node, VariableNode)):
                raise RuntimeError("invalid assignment")

            node = AssignmentNode(node.name, self.logic_or())

        return node

    def logic_or(self):
        node = self.logic_and()

        while self.accept("|"):
            node = BinaryNode(node, "|", self.logic_and())

        return node

    def logic_and(self):
        node = self.term()

        while self.accept("&"):
            node = BinaryNode(node, "&", self.term())

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
        elif self.accept("("):
            node = self.logic_or()
            if not self.accept(")"):
                raise RuntimeError("unmatched parentheses")
        elif self.check("u"):
            raise RuntimeError("unknown token '" + self.t_text + "'")
        elif self.check("e"):
            raise RuntimeError("unexpected end of expression")
        else:
            raise RuntimeError("unexpected token '" + self.t_text + "'")

        return node

    def eval(self, expr):
        self.expr = expr
        self.pos = 0

        try:
            self.get_token()

            node = self.assign()

            if not self.check("e"):
                raise RuntimeError("there's an excess part of expression")

            return node.eval(self.context)
        except RuntimeError as e:
            print("error: " + str(e))


def main():
    parser = Parser()
    print(parser.eval("true or (false and true)"))

main()
