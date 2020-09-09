
import json, sys

def buildAST(tokens):
    return ASTBuilder(tokens).buildAST()

class ASTBuilder:
    def __init__(self, tokens):
        self.tokens = tokens

    def buildAST(self):
        self.size = len(self.tokens)
        self.index = 0
        ret = self.statements(meetEndAsPossible=True)
        assert self.index == self.size, "break at %s, %s" % (self.index, self.size)
        return ret

    '''
    TODO: remove stopToken when FSM is stable.
    '''
    def statements(self, meetEndAsPossible=False, stopTokens=[]):
        stmts, oldIndex = [], self.index
        while self.index < self.size:
            if self.currentType() in stopTokens or \
                self.currentValue() in stopTokens:
                break
            stmt = self.statement()
            if not stmt:
                if meetEndAsPossible:
                    continue
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

        # unset to avoid bug
        currentType, currentValue = None, None

        oldIndex = self.index
        AccessModifier, Static, Final = None, None, None
        if self.currentType() == "access-modifier":
            AccessModifier = self.currentToken()
            self.index += 1
            assert self.index < self.size
        if self.currentType() == "static":
            Static = self.currentToken()
            self.index += 1
            assert self.index < self.size
        if self.currentType() == "final":
            Static = self.currentToken()
            self.index += 1
            assert self.index < self.size

        currentType, currentValue = self.currentType(), self.currentValue()
        if self.currentType() in ["class", "interface"]:
            # class or interface = =)
            return self.classClause(AccessModifier, Static, Final)
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

    def classClause(self, AccessModifier, Static, Final):
        assert self.currentType() in ["class", "interface"]
        classType = self.currentToken()
        self.index += 1
        assert self.currentType() == "variable", "fail at %s" % self.index
        className = self.currentToken()
        self.index += 1
        Extends, Implements = None, []
        if self.currentType() == "extends":
            self.index += 1
            Extends = self.classPathExpr()
            assert Extends, "extends is null at: %s" % self.index
        if self.currentType() == "implements":
            self.index += 1
            Implements = self.classListExpr()
            assert Implements, "implements is null at: %s" % self.index
        assert self.currentValue() == "{"
        self.index += 1
        ClassStatements = self.statements(meetEndAsPossible=True, stopTokens=["}"])
        assert self.currentValue() == "}"
        self.index += 1
        return {
            "type": "class-clause",
            "class-type": classType, # class, interface
            "className": className,
            "access-modifier": AccessModifier,
            "static": Static,
            "final": Final,
            "extends": Extends,
            "implements": Implements,
            "class-statements": ClassStatements
        }

    def classListExpr(self):
        ClassList = []
        Class = self.classPathExpr()
        assert Class
        ClassList.append(Class)
        while self.currentValue() == ",":
            Class = self.classPathExpr()
            assert Class
            ClassList.append(Class)
        return ClassList

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