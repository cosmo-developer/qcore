#this class contain token information such as value type line call and file
class Token:
    def __init__(self, value, type, line, col, file="<stdin>"):
        self.value = value
        self.type = type
        self.line = line
        self.col = col
        self.file = file
    def __repr__(self):
        return str(self.value+':'+self.type)

##########################
####### Expression #######
##########################
#this expression contain left and write expression with associated operator +,-,/,*,<,>,<=,>=,And,Or
class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.right = right
        self.op = op

#this expression  contain numrical value 
class NumberExp:
    def __init__(self, tok):
        self.tok = tok

#this expression contain negative expression
class UnaryExp:
    def __init__(self, fact):
        self.fact = fact

#this expression contain variable name
class VarExp:
    def __init__(self, tok):
        self.tok = tok

#this expression contain variable name chain and right hand expression 
class VarAssignExp:
    def __init__(self, name, exp):
        self.name = name
        self.exp = exp

#this expression contain list of VarAssignExp
class MultiVarAssignExp:
    def __init__(self, listexp):
        self.listexp = listexp

#this expression contain list of expression and called body of function ,if ,loop 
class CompoundStatement:
    def __init__(self, statements):
        self.statements = statements
        self.counter = 0
    #this function return true if counter  < length of statements
    def havenext(self):
        return True if self.counter < len(self.statements) else False
    #this function return next statement from list 
    def next(self):
        self.counter += 1
        return self.statements[self.counter - 1]
    #this function set jump on label
    def setjump(self, counter):
        self.counter = counter
    #this function return current position of counter
    def getjump(self):
        return self.counter

#this expression contain information about loop statement
class LoopStatement:
    def __init__(self, var=None, condition=None, times=None, body=None):
        self.condition = condition
        self.var = var
        self.times = times
        self.body = body

#this expression contain list of main expression
class Statements:
    def __init__(self, statements):
        self.statements = statements
        self.counter = 0
    #this function return true if counter  < length of statements
    def havenext(self):
        return True if self.counter < len(self.statements) else False#e
    #this function return next statement from list 
    def next(self):
        self.counter += 1
        return self.statements[self.counter - 1]#E
    #this function set jump on label
    def setjump(self, counter):
        self.counter = counter
    #this function return current position of counter
    def getjump(self):
        return self.counter

#this expression contain information about if statement
class IfStatement:
    def __init__(self, condition, ifbody, elsebody, elseifbodies):
        self.ifbody = ifbody
        self.elsebody = elsebody
        self.elseifbodies = elseifbodies
        self.condition = condition

#this expression contain expression to return 
class ReturnStatement:
    def __init__(self, exp):
        self.exp = exp

#this expression contain argument supplied to print function
class PrintStatement:
    def __init__(self, args):
        self.args = args

#this expression contain line number data and use to write new line
class LineExp:
    def __init__(self, exp):
        self.exp = exp

#this expression contain space number data and use to write space
class SpaceExp:
    def __init__(self, exp):
        self.exp = exp

#this expression contain information about jump label
class IdExp:
    def __init__(self, exp):
        self.exp = exp

#this expression contain information about how to jump on which label
class JumpExp:
    def __init__(self, idexp, timeexp=None, conditionexp=None):
        self.idexp = idexp
        self.timeexp = timeexp
        self.conditionexp = conditionexp
        self.counter = 0
        self.out = -1

#this expression contain dictionary data
class TupleExp:
    def __init__(self, args):
        self.args = args

#this expression contain information about list function
class ListExp:
    def __init__(self, data):
        self.data = data

#this expression contain string data
class StringExp:
    def __init__(self, tok):
        self.tok = tok

#this expression contain list of  global variable and their expression
class GlobalExp:
    def __init__(self,vars, exp):
        self.vars=vars
        self.exp = exp

#this expression contain information about python function calling
class PyFuncExp:
    def __init__(self, name, args):
        self.name = name
        self.args = args

#this expression contain information about function defination in 'q' language
class FuncExp:
    def __init__(self, name, args, body):
        self.name = name
        self.args = args
        self.body = body

#this expression contain information about function calling
class FuncCallExp:
    def __init__(self, name, args, typecall='FID'):
        self.name = name
        self.args = args
        self.typecall = typecall

#this expression contain information about how to replace self value and other value
class SelfReplaceExp:
    def __init__(self, var, toreplace, withreplace):
        self.var = var
        self.toreplace = toreplace
        self.withreplace = withreplace

#this expression contain information about what to return after replace
class AssignReplaceExp:
    def __init__(self, var, toreplace, withreplace):
        self.var = var
        self.toreplace = toreplace
        self.withreplace = withreplace

#this expression contain information about configure file global variable
class DictExp:
    def __init__(self, var, exp, table):
        self.var = var
        self.exp = exp
        self.table = table



#this expression contain information about how to combine variable with expression
class CombinationalExp:
    def __init__(self, var, exp):
        self.var = var
        self.exp = exp

#this expression contain code of python
class PythonCodeExp:
    def __init__(self, code):
        self.code = code

#this expression contain variable and array list
class ArrayExp:
    def __init__(self, var, items):
        self.var = var
        self.items = items

#this expression contain information about which variable to kill
class KillVarExp:
    def __init__(self, var):
        self.var = var

#this expression is use to know about type of given expression
class TypeExp:
    def __init__(self, exp):
        self.exp = exp


#this expression contain information about language
class LangAccessExp:
    def __init__(self, var, lang):
        self.var = var
        self.lang = lang

#this expression contain information
class AssignByIndex:
    def __init__(self, var, index, exp):
        self.var = var
        self.index = index
        self.exp = exp

#this expression contain information about subvariable
class DotVarAccess:
    def __init__(self, tok):
        self.tok = tok

#this expression contain list of expression seprated by dot
class ChainExpression:
    def __init__(self, chain=[]):
        self.chain = chain
#this expression contain variable chain and expression to append
class DotAddExpression:
    def __init__(self,chain=[],exp=None):
        self.chain=chain
        self.exp=exp
#this expression contain last index of value
class EndExpression:
    def __init__(self):
        pass
#this expression contain   how to split expression by deliminator
class SplitExp:
    def __init__(self,exp):
        self.exp=exp
#this expression contain information about what to append in chain variable
class AddExpression:
    def __init__(self,chain,exp,at=None):
        self.chain=chain
        self.exp=exp
        self.at=at
#this expression is use to return lenth of string and array data
class LengthExpression:
    def __init__(self):
        pass
#this expression is use to performs delete operation on string array and dictionary     
class DeleteExperssion:
    def __init__(self,chain,exp):
        self.chain=chain
        self.exp=exp
# #this expression is use to performs find operation on string and dictionary       
class FindExpression:
    def __init__(self,_what,_from=None,_to=None):
        self._what=_what
        self._from=_from
        self._to=_to

class MixExpression:
    def __init__(self):
        pass

class GetExpression:
    def __init__(self,_from,_to,_limit):
        self._from=_from
        self._to=_to
        self._limit=_limit

class VarIfExpression:
    def __init__(self,chain,ifexp):
        self.chain=chain
        self.ifexp=ifexp

def replace_relative(_text='',_toreplace=[],_withreplace=[]):
    if len(_toreplace)!=len(_withreplace):raise RuntimeError("length must be equal {} with {} not valid"
                                                             .format(len(_toreplace),len(_withreplace)))
    for i in range(len(_toreplace)):
        _text=_text.replace(_toreplace[i],_withreplace[i])
    return _text

class TimeExpression:
    def __init__(self,chain,_format,_toformat,_operate,_howmuch):
        if _operate == None:
            _operate=Token('plus','INCREAMENT',0,0)
        if _howmuch == None:
            _howmuch=NumberExp(Token('0','INTEGER_CONST',0,0))
        self.chain=chain
        self._format=_format
        self._toformat=_toformat
        self._operate=_operate
        self._howmuch=_howmuch

class NumExpression:
    def __init__(self,tmp):
        self.tmp=tmp