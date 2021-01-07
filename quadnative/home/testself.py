code='class Data:\n' \
     '\tdef __init__(self):\n'

def addmore(code,var,value):
    if type(value).__name__ == 'str':
        value='"'+value+'"'
    return code+'\t\tself.'+var+'='+value+'\n'
def test():
    globals().update({'x':22})
test()
print(globals()['x'])