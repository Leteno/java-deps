
import json, sys

def buildAST(tokens):
    return ASTBuilder(tokens).buildAST()

class ASTBuilder:
    def __init__(self, tokens):
        self.tokens = tokens

    def buildAST(self):
        self.size = len(self.tokens)
        self.index = 0
        return self.statements()

    def statements(self):
        stmts, oldIndex = [], self.index
        while self.index < self.size:
            stmt = self.statement()
            if not stmt:
                break
            assert oldIndex < self.index, "Stop Moving at: %s" % self.index
            oldIndex = self.index
            stmts.append(stmt)
        return {
            'type': 'statements',
            'list': stmts
        }

    def statement(self):
        currentType, currentValue = self.currentType(), self.currentValue()
        if currentValue == "package":
            return self.packageClause()
        elif currentValue == "import":
            return self.importClause()
        else:
            # TODO skip it by now
            self.index += 1

    def packageClause(self):
        self.index += 1 # package
        path = self.classPathExpr()
        assert self.currentValue() == ';'
        self.index += 1
        return {
            'type': 'package',
            'path': path
        }

    def importClause(self):
        self.index += 1 # import
        path = self.classPathExpr()
        assert self.currentValue() == ';'
        self.index += 1
        return {
            'type': 'import',
            'path': path
        }

    def classPathExpr(self, keepLastVarAsMethod=False):
        assert self.currentType() == 'variable'
        retClassPath = {
            'type': 'class-path',
            'value': self.currentToken(),
            'path': None
        }
        self.index += 1
        curClassPath, lastToken = retClassPath, None
        while self.index + 1 < self.size and \
             self.getType(self.index) == 'dot' and \
                 self.getType(self.index+1) == 'variable':
            if lastToken:
                curClassPath['path'] = {
                    'type': 'class-path',
                    'value': lastToken,
                    'path': None
                }
                curClassPath = curClassPath['path']
            lastToken = self.getToken(self.index + 1)
            self.index += 2
        if not keepLastVarAsMethod and lastToken:
            curClassPath['path'] = {
                'type': 'class-path',
                'value': lastToken,
                'path': None
            }
        return retClassPath

    def getToken(self, index):
        return self.tokens[index]

    def getType(self, index):
        return self.getToken(index)['type']

    def getValue(self, index):
        return self.getToken(index)['value']

    def currentToken(self):
        return self.tokens[self.index]

    def currentType(self):
        return self.currentToken()['type']

    def currentValue(self):
        return self.currentToken()['value']

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