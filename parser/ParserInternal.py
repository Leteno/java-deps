
__all__ = [ "do" ]

def do(content):
    pass

def test():
    f = open('Student.test.java', 'r')
    content = f.read()
    f.close()
    expectObj = {}
    assert(do(content) == expectObj)

if __name__ == '__main__':
    test()