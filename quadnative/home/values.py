# value class contain ent ,string ,double value
class Value:
    def __init__(self, value,templated=False):
        self.template=value
        if templated:
            self.value =float(value)
        self.value = value
        self.templated=templated

    # operator overloading  divide self.value /other.value
    # if other.value or self.value are other then integer or double then throw an error 
    def __truediv__(self, other):
        return Value(self.value / other.value)

    # this operator overloading add self.value + other.value
    # in this operation both self.value and other.value are number then it return sum otherwise it's thorw an error
    def __add__(self, other):
        return Value(self.value + other.value)

    # this operator overloading add self.value - other.value
    # in this operation both self.value and other.value are number then it return difference otherwise it's thorw an error
    def __sub__(self, other):
        return Value(self.value - other.value)

    # this operator overloading add self.value * other.value
    # in this operation both self.value and other.value are number then it return product otherwise it's thorw an error
    def __mul__(self, other):
        return Value(self.value * other.value)

    def __lt__(self, other):
        return Value(self.value < other.value)

    def __gt__(self, other):
        return Value(self.value > other.value)

    def __le__(self, other):
        return Value(self.value <= other.value)

    def __ge__(self, other):
        return Value(self.value >= other.value)

    def __eq__(self, other):
        return Value(self.value == other.value)

    def __ne__(self, other):
        return Value(self.value != other.value)

    def __or__(self, other):
        return Value(self.value or other.value)

    def __and__(self, other):
        return Value(self.value and other.value)

    def __repr__(self):
        return str(self.template) if self.templated else str(self.value)

    # this function replace value of self
    def replaceself(self, toreplace, withreplace):
        if type(self.value).__name__ == 'str':
            self.value = self.value.replace(toreplace.value, withreplace.value)
        else:
            raise RuntimeError("Can't apply replace function on other than string")

    # this function replace and return but does not change it's value
    def replacenew(self, toreplace, withreplace):
        if type(self.value).__name__ == 'str':
            return Value(self.value.replace(toreplace.value, withreplace.value))
        else:
            raise RuntimeError("Can't apply replace function on other than string")



# this class contain python dictionary data
class Dictionary:
    def __init__(self, data):
        self.data = data #e

    # this function return value associated with the key
    def get(self, key):
        return self.data.get(key, None)

    # this function update value by the key
    def set(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return str(self.data)


import copy


# this class contain array type data
class ArrayList:
    def __init__(self, items=[]):
        self.items = copy.copy(items)

    def __repr__(self):
        return str(self.items)


# this class contain defination of function such as body of function and argument of function
class Function:
    '''
    name: Token
    args: {}
    body: CompoundStatement
    '''

    def __init__(self, name, args, body=None):
        self.name = name
        self.args = args
        self.body = body


# this data strucacture contain global and local difind variables record
class SymbolTable:
    def __init__(self, name, parent=None):
        self.symbols = {}
        self.name = name
        self.parent = parent

    def get(self, name):
        temp = self
        while temp != None:
            if name in list(temp.symbols.keys()):
                return temp.symbols[name]
            temp = temp.parent
        return None

    def set(self, name, value):
        temp = self
        while temp != None:
            if name in temp.symbols.keys():
                temp.symbols.update({name: value})
                return ""
            temp = temp.parent
        self.symbols.update({name: value})
        # if value ==  Value(None) and

    def remove(self, name):
        temp=self
        while temp:
            if name in temp.symbols.keys():
                temp.symbols.pop(name)
                return
            temp=temp.parent