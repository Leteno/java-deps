
def tokenize(content):
    pass

def test():
    f = open('Student.test.java', 'r')
    content = f.read()
    f.close()
    tokens = tokenize(content)
    expect = {}
    assert tokens == expect, "tokens not equals: %s  %s" % (expect, tokens)

if __name__ == '__main__':
    test()