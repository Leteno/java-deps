
from . import Grammar, Tokenizer

def do(content):
    tokens = Tokenizer.tokenize(content)
    ast = Grammar.buildAST(tokens)
    return ast

def test():
    f = open('Student.test.java', 'r')
    content = f.read()
    f.close()
    expectObj = {}
    assert(do(content) == expectObj)

if __name__ == '__main__':
    test()