
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
            ch = self.content[self.index]
            if str.isalpha(ch) or ch == '_':
                tokens.append(self.variables())
            elif str.isnumeric(ch):
                tokens.append(self.number())
            elif ch == '.':
                tokens.append(self.dot(ch))
            elif ch in "(){}":
                tokens.append(self.bracket(ch))
            elif ch in ':;':
                tokens.append(self.colonOrComma(ch))
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
                obj = self.commentStart()
                tokens.append(obj if obj else self.divide())
            elif ch == '*':
                obj = self.commentEnd()
                tokens.append(obj if obj else self.multiply())
            elif str.isspace(ch):
                self.index += 1
            else:
                assert False, "Tokenize: unknown ch(%s) in %s" % (ch, self.index)
        return tokens

    def variables(self):
        value = self._variableStr()
        if value in ["public", "private", "protected"]:
            return { "type": "access-modifier", "value": value }
        elif value in ["void", "int", "long", "longlong", "float", "double" ]:
            return { "type": "data-type", "value": value }
        elif value in ["package", "import", "class", "return", "break", "continue"]:
            return { "type": value, "value": value }
        elif value in ["if", "while", "for"]:
            return { "type": "controller", "value": value }
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

    def colonOrComma(self, ch):
        self.index += 1
        if ch == ':':
            return {
                "type": "colon",
                "value": ch
            }
        elif ch == ';':
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
            self.index+1 < self.size and '=' == self.content[self.index]:
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
        pass

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

    def commentStart(self):
        start, isComment = self.index, False
        while self.index + 1 < self.size and self.content[self.index + 1] == '*':
            self.index += 1
            isComment = True
        if isComment:
            return { 'type': 'comment-start', 'value': self.content[start, self.index]}
        return None

    def commentEnd(self):
        start, end, isComment = self.index, self.index, False
        while end + 1 < self.size and self.content[end + 1] == '*':
            end += 1
        if end + 1 < self.size and self.content[end + 1] == '/':
            self.index = end + 1
            isComment = True
        if isComment:
            return { 'type': 'comment-end', 'value': self.content[start, self.index]}
        return None

def test():
    f = open('Student.test.java', 'r')
    content = f.read()
    f.close()
    tokens = tokenize(content)
    expect = {}
    assert tokens == expect, "tokens not equals: %s  %s" % (expect, tokens)

if __name__ == '__main__':
    test()