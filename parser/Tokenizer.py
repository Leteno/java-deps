
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
            elif ch in "+-":
                tokens.append(self.operator())
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
        pass

    def number(self):
        start, end = self.index, self.index
        while end < self.size and str.isdecimal(self.content[end]):
            end += 1
        result = self.content[start, end]
        self.index = end
        if end < self.size and self.content[end] == '.':
            end2 = end+1
            while end2 < self.size and str.isdecimal(end2):
                end2 += 1
            result = self.content[start, end2]
            return {
                'type': 'number',
                'value': result
            }
        return {
            'type': 'decimal',
            'value': result
        }

    def operator(self):
        ch = self.content[self.index]
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