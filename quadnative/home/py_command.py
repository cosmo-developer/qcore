__globals__ = globals()  # Don't erase it

import hashlib


def MyName(c=4, d=44):
    return c + c * c + d


def E(x):
    return [5, 5, 5, 5]


def Factorial(n):
    if n == 0:
        return 1
    else:
        return n * Factorial(n - 1)


def GiveMyName(yourname):
    return yourname


def SayHelloToUser(username):
    print("Hello User:", username)


def Max(n):
    if n == 0:
        return 1
    else:
        return n * Max(n - 1)


def Eval(exp):
    return eval(exp)


def Hash(data):
    return hashlib.sha3_512(data.encode('utf-8')).hexdigest()


def Execute(python_code):
    return exec(python_code)


def Something():
    return BACKUP.self + ' ' + ARRAY.index1 + '\n'


def Login(username, password):
    if username == DB.username and password == DB.password:
        return 'Logined Successfully'
    else:
        return 'Login Unsuccess'


def LaptopDetail():
    print('___Laptop Details____')
    print("Name:", LAPTOP.self)
    print("Type:", LAPTOP.type)
    print("Processor Inside:", LAPTOP.processor)
    print("Processor Speed:", LAPTOP.processor_speed)
    print("Storage Type:", LAPTOP.internal_type)
    print("Storage Capacity:", LAPTOP.internal_capacity)
    print("Price:", LAPTOP.price)
    return LAPTOP.self
