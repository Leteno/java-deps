
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
    meetEndAsPossible, will skip all the wrong statement, FSM will move on
    stopTokens, FSM will stop if current first token is in the list.
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

    '''
    Support such clause:
    * package
    * import
    * class-clause
    '''
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

        if self.currentType() in ["class", "interface"]:
            # class or interface = =)
            return self.classClause(AccessModifier, Static, Final)
        elif self.currentType() in ['data-type', 'variable']:
            # method or declare
            # TODO class info
            DataType = self.dataTypeExpr()
            assert self.index < self.size
            # TODO skip for now. elegance..
            if self.currentType() not in ['variable']:
                self.index += 1
                return None
            assert self.currentType() == 'variable', "currentType: %s" % self.currentToken()
            Name = self.currentToken()
            self.index += 1
            assert self.index < self.size
            if self.currentValue() == '(':
                # is method
                return self.methodClause(AccessModifier, Static, Final, DataType, Name)
            elif self.currentValue() in ['=', ';']:
                # is declare
                return self.declaration(AccessModifier, Static, Final, DataType, Name)
            else:
                assert False, "Unknown type: %s" % self.currentToken()
        # TODO skip it by now
        self.index += 1

    '''
    Support:
    * package a.b.c.d;
    '''
    def packageClause(self):
        self.index += 1 # package
        path = self.classPathExpr()
        assert self.currentValue() == ';'
        self.index += 1
        return {
            'type': 'package',
            'path': path
        }

    '''
    Support:
    * import a.b.c.d.E;
    '''
    def importClause(self):
        self.index += 1 # import
        path = self.classPathExpr()
        assert self.currentValue() == ';'
        self.index += 1
        return {
            'type': 'import',
            'path': path
        }

    '''
    Support:
    * a
    * a.b.c
    * a.b.c in a.b.c.d()
    '''
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

    '''
    Support:
    * [access-modifier: public/private/protected] [static] [final] class A
        [extends a.b.c.d]
        [implements iA, iB] {
            <ClassStatements> # TODO
        }
    '''
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

    '''
    Support:
    * a.b.c
    * a.b.c, d.e.f
    '''
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

    def dataTypeExpr(self, allowEmpty=False):
        if self.currentType() == 'data-type':
            DataType = self.currentToken()
            self.index += 1
            return DataType
        elif self.currentType() == 'variable':
            DataType = self.classPathExpr()
            # no need to increase self.
            return DataType
        elif allowEmpty:
            return None
        else:
            assert False, "Unknown DataType: %s" % self.currentToken()

    def methodClause(self, AccessModifier, Static, Final, DataType, Name):
        assert self.currentValue() == '('
        self.index += 1
        Args = self.arguments()
        assert self.currentValue() == ')'
        self.index += 1
        if self.currentValue() == '{':
            # method clause
            self.index += 1
            MethodStatements = self.statements(
                meetEndAsPossible=True, stopTokens=['}'])
            assert self.currentValue() == '}'
            self.index += 1
            return {
                'type': 'method-clause',
                'name': Name,
                "access-modifier": AccessModifier,
                "static": Static,
                "final": Final,
                'return-type': DataType,
                'arguments': Args,
                'statements': MethodStatements,
            }
        elif self.currentValue() == ';':
            # method declare
            return {
                "type": 'method-declare',
                'name': Name,
                "access-modifier": AccessModifier,
                "static": Static,
                "final": Final,
                'return-type': DataType,
                'arguments': Args,
            }
        else:
            assert False, "Unknown Type: %s" % self.currentToken()

    def arguments(self):
        Args = {
            'type': 'arguments',
            'arguments': []
        }
        while True:
            DataType = self.dataTypeExpr(allowEmpty=True)
            if DataType:
                assert self.currentType() == 'variable'
                Name = self.currentToken()
                self.index += 1
                Args['arguments'].append({
                    'data-type': DataType,
                    'name': Name,
                })
            else: # None
                return Args

    def declaration(self, AccessModifier, Static, Final, DataType, Name):
        # TODO
        while self.currentValue() != ';':
            self.index += 1
        return None

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
    assert expect == ast, "expect: %s, actual: %s" % (expect, json.dumps(ast))
    return 0

if __name__ == '__main__':
    sys.exit(test())