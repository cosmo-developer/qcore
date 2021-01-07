class Token:
    def __init__(self,value,type,line,col,file="<stdin>"):
        self.value=value
        self.type=type
        self.line=line
        self.col=col
        self.file=file
class SymbolTable:
    def __init__(self,name,parent=None):
        self.parent=parent
        self.symbols={}
        self.name=name
    def add(self,symbol,type,value):
        temp=self
        while temp!=None:
            if symbol in list(temp.symbols.keys()):
                temp.symbols.update({symbol:[type,value]})
                return
            temp=temp.parent
        self.symbols.update({symbol:[type,value]})
    def get(self,symbol,request='VID'):
        temp=self
        while temp!=None:
            if symbol.value in list(temp.symbols.keys()):
                return temp.symbols.get(symbol.value)
            else:
                temp=temp.parent
        if request == "VID":
            request='identifier'
        elif request == 'FID':
            request == 'function'
        print(self.symbols)
        raise RuntimeError(
            "Undefined {} {} from {} at line:{} col:{} inside:{}".format(
                request,symbol.value,symbol.file,symbol.line,symbol.col,self.name.value
            )
                           )


global_symbol_table=SymbolTable("GLOBAL",parent=None)

###################################
########## SERVER PARAMETERS  #####
###################################

global_symbol_table.add('Server.Segment.1','VID','segment:1')
global_symbol_table.add('Post.Key','VID','Post Key')
global_symbol_table.add('Get.Key','VID','Get Key')
global_symbol_table.add('Session.Key','VID','Session Key')
global_symbol_table.add('Cookie.Key','VID','Cookie Key')
global_symbol_table.add('Cookie.Key.Time','VID','1 month')


###############################
########## Nodes ##############
###############################
class NumberExpression:
    def __init__(self,tok):
        self.tok=tok

class VarExpression:
    def __init__(self,tok):
        self.tok=tok

class UnaryExpression:
    def __init__(self,exp):
        self.exp=exp

class ImportExpression:
    def __init__(self,exp):
        self.exp=exp

class BinOpExpression:
    def __init__(self,lexp,op,rexp):
        self.lexp=lexp
        self.op=op
        self.rexp=rexp

class ConditionExpression:
    def __init__(self,lexp,op,rexp):
        self.lexp=lexp
        self.op=op
        self.rexp=rexp

class IfExpression:
    def __init__(self,exp,tstatements=[],fstatements=[]):
        self.exp=exp
        self.tstatements=tstatements
        self.fstatements=fstatements

class ElseExpression:
    def __init__(self,statements=[]):
        self.statements=statements

class ElseifExpression:
    def __init__(self,exp,statements=[]):
        self.exp=exp
        self.statements=statements

class StringExpresssion:
    def __init__(self,tok):
        self.tok=tok

class FuncDefExpression:
    def __init__(self,name,params,stmts):
        self.name=name
        self.params=params
        self.stmts=stmts
        self.symboltable=SymbolTable(name,parent=global_symbol_table)
        for p in params:
            self.symboltable.add(p,params[p].tok.type,params[p])
        global_symbol_table.add(self.name.value,'FID',self)



class FuncCallExpresssion:
    def __init__(self,name,params,symboltable):
        self.name=name
        self.params=params # list of passing param functions
        self.symboltable=symboltable
        for p in self.params:
            self.symboltable.add(p,params[p].tok.type,params[p])

class PrintExpression:
    def __init__(self,args):
        self.args=args

class ReturnExpression:
    def __init__(self,exp):
        self.exp=exp

class NotExpression:
    def __init__(self,exp):
        self.exp=exp
class AssignExpression:
    def __init__(self,tok,exp):
        self.exp=exp
        self.tok=tok
class PrintExpression:
    def __init__(self,args):
        self.args=args

class TupleExpression:
    def __init__(self,listparams):
        self.listparams=listparams

class ListExpression:
    def __init__(self,tok):
        self.tok=tok
class BooleanExpression:
    def __init__(self,tok):
        self.tok=tok

class ReturnExpression:
    def __init__(self,exp):
        self.exp=exp

class PyFuncExpression:
    def __init__(self,name,args):
        self.args=args
        self.name=name
        global_symbol_table.add(self.name.value,self.name.type,self)
class PyFuncCallExpression:
    def __init__(self,name,args):
        self.args=args
        self.name=name
class MultiAssignment:
    def __init__(self,assignments):
        self.assignments=assignments

class LineExpression:
    def __init__(self,nline):
        self.nline=nline
class SpaceExpression:
    def __init__(self,nspace):
        self.nspace=nspace

class IdExpression:
    def __init__(self,tok):
        self.tok=tok

class JumpExpression:
    def __init__(self,id,times,condition,activeid):
        self.id=id
        self.times=times
        self.condition=condition
        self.activeid=activeid