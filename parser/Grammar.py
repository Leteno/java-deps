
import json, sys

def buildAST(tokens):
    return ASTBuilder(tokens).buildAST()

class ASTBuilder:
    def __init__(self, tokens):
        self.tokens = tokens

    def buildAST(self):
        self.size = len(self.tokens)
        self.index = 0
        return self.parseInternal()

    def getToken(self, index):
        return self.tokens[index]

    def currentToken(self):
        return self.tokens[self.index]

def test():
    f = open('Student.tokenizer.json', 'r')
    tokens = json.load(f)
    f.close()
    f = open('Student.grammar.json', 'r')
    expect = json.load(f)
    f.close()
    ast = buildAST(tokens)
    assert expect == ast, "expect: %s, actual: %s" % (expect, ast)
    return 0

if __name__ == '__main__':
    sys.exit(test())