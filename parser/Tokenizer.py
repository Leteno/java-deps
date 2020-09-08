
import json, sys

def tokenize(content):
    return Tokenizer(content).tokenize()

class Tokenizer:
    def __init__(self, content):
        self.content = content
        self.index = 0
        self.size = len(content)

    def tokenize(self):
        tokens = []
        while self.index < self.size:
            ch, lastIndex = self.content[self.index], self.index
            if str.isalpha(ch) or ch == '_':
                tokens.append(self.variables())
            elif str.isnumeric(ch):
                tokens.append(self.number())
            elif ch == '.':
                tokens.append(self.dot(ch))
            elif ch in "(){}":
                tokens.append(self.bracket(ch))
            elif ch in ':;,':
                tokens.append(self.colonOrSemicolonOrComma(ch))
            elif ch in "<>":
                tokens.append(self.compare(ch))
            elif ch == '=':
                equalEqualObj = self.equalEqual()
                if equalEqualObj:
                    tokens.append(equalEqualObj)
                tokens.append(self.equal())
            elif ch in "\'\"":
                tokens.append(self.charOrString(ch))
            elif ch in "+-":
                tokens.append(self.operator(ch))
            elif ch == '/':
                tokens.append(self.slash())
            elif ch == '*':
                tokens.append(self.multiply())
            elif ch == '&':
                tokens.append(self.andToken())
            elif ch == '|':
                tokens.append(self.orToken())
            elif ch == '%':
                tokens.append(self.modToken())
            elif str.isspace(ch):
                self.index += 1
            else:
                assert False, "Tokenize: unknown ch'%s' in %s" % (ch, self.index)
            assert lastIndex < self.index, "Don't forget to increase self.index (Keep moving !)"
        return tokens

    def variables(self):
        value = self._variableStr()
        if value in ["public", "private", "protected"]:
            return { "type": "access-modifier", "value": value }
        elif value in ["void", "int", "long", "longlong", "float", "double" ]:
            return { "type": "data-type", "value": value }
        elif value in ["package", "import", "class", "interface", "extends", 
                        "implements", "return", "new", "static", "const",
                        "this"]:
            return { "type": value, "value": value }
        elif value in ["if", "while", "for", "break", "continue"]:
            return { "type": value, "value": value }
        elif value in ["true", "false"]:
            return { "type": "boolean", "value": value }
        else:
            return { "type": "variable", "value": value }

    def _variableStr(self):
        start, end = self.index, self.index
        while end < self.size and \
            (str.isalnum(self.content[end]) or self.content[end] in "_"):
            end += 1
        self.index = end
        return self.content[start:end]

    def number(self):
        start, end = self.index, self.index
        while end < self.size and str.isdecimal(self.content[end]):
            end += 1
        result = self.content[start:end]
        if end < self.size and self.content[end] == '.':
            end2 = end+1
            while end2 < self.size and str.isdecimal(end2):
                end2 += 1
            self.index = end2
            result = self.content[start:end2]
            return {
                'type': 'number',
                'value': result
            }
        self.index = end
        return {
            'type': 'decimal',
            'value': result
        }

    def dot(self, ch):
        self.index += 1
        return {
            'type': 'dot',
            'value': ch
        }

    def bracket(self, ch):
        self.index += 1
        if ch in "()":
            return {
                "type": "parenthesis",
                "value": ch
            }
        elif ch in "{}":
            return {
                "type": "bracket",
                "value": ch
            }

    def colonOrSemicolonOrComma(self, ch):
        self.index += 1
        if ch == ':':
            return {
                "type": "colon",
                "value": ch
            }
        elif ch == ';':
            return {
                "type": "semicolon",
                "value": ch
            }
        elif ch == ',':
            return {
                "type": "comma",
                "value": ch
            }

    def compare(self, ch):
        if ch in "<>":
            if self.index + 1 < self.size and '=' == self.content[self.index +1]:
                value = self.content[self.index : self.index+2]
                self.index += 2
                return {
                    "type": 'compare',
                    "value": value
                }
            self.index += 1
            return {
                "type": 'compare',
                "value": ch
            }

    def equalEqual(self):
        if '=' == self.content[self.index] and \
            self.index+1 < self.size and '=' == self.content[self.index+1]:
            self.index += 2
            return {
                "type": 'compare',
                "value": "=="
            }
        return None

    def equal(self):
        self.index += 1
        return {
            "type": "equal",
            "value": "="
        }

    def charOrString(self, ch):
        if ch == '\'':
            assert self.index + 2 < self.size, "' should have two char after it" % self.index
            char = self.content[self.index+1]
            assert str.isascii(char), "char should be ascii, but %s, at %s" % (char, self.index)
            assert self.content[self.index+2] == '\'', "' should have another ' at last: %s" % (self.index+2)
            self.index += 2
            return {
                "type": "char",
                "value": char
            }
        elif ch == '"':
            assert self.index + 1 < self.size, "\" should have at least one charater, at %s" % self.index
            start, end = self.index + 1, self.index + 1
            while end < self.size and self.content[end] != '"':
                end += 1
            assert end < self.size, "expect \" at %s" % end
            assert self.content[end] == '"'
            string = self.content[start:end]
            self.index = end + 1
            return {
                "type": "string",
                "value": string
            }

    def operator(self, ch):
        if ch in '+-*/':
            self.index += 1
            return {
                'type': 'operator',
                'value': ch
            }
        return None

    def divide(self):
        self.index += 1
        return {
            'type': 'operator',
            'value': '/'
        }

    def multiply(self):
        self.index += 1
        return {
            'type': 'operator',
            'value': '*'
        }

    def slash(self):
        start, end = self.index, self.index + 1
        if end < self.size and self.content[end] == '*':
            end += 1
            assert end + 2 < self.size
            while not (self.content[end + 1] == '*' and self.content[end+2] == '/'):
                end += 1
                assert end + 2 < self.size
            end += 2 + 1
            self.index = end
            return { 'type': 'comment', 'value': self.content[start:end]}
        elif end < self.size and self.content[end] == '/':
            end += 1
            while end + 1 < self.size and self.content[end+1] != '\n':
                # TODO '\n\r' for windows, however it may be fine.
                end += 1
            self.index = end + 1
            return { 'type': 'comment', 'value': self.content[start:end]}
        return self.divide()

    def andToken(self):
        if self.index + 1 < self.size and self.content[self.index+1] == '&':
            self.index += 2
            return { 'type': 'logic-and', 'value': '&&' }
        self.index += 1
        return { 'type': 'bit-and', 'value': '&' }

    def orToken(self):
        if self.index + 1 < self.size and self.content[self.index+1] == '|':
            self.index += 2
            return { 'type': 'logic-or', 'value': '||' }
        self.index += 1
        return { 'type': 'bit-or', 'value': '|' }

    def modToken(self):
        self.index += 1
        return { 'type': 'mod', 'value': '%' }

def test():
    f = open('Student.test.java', 'r')
    content = f.read()
    f.close()
    tokens = tokenize(content)
    f = open('Student.tokenizer.json', 'r')
    expect = json.load(f)
    f.close()
    assert tokens == expect, "tokens not equals: %s  %s" % (expect, tokens)
    return 0

if __name__ == '__main__':
    sys.exit(test())