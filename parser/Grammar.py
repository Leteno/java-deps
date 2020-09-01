
import json, sys

def buildAST(tokens):
    pass

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