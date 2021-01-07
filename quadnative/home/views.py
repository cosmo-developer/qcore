from django.shortcuts import render
from django.http import HttpResponse
import datetime
import random
import re
import os
from . import py_command as py_cmd
from .exps import *
from .values import *

code = 'class Data:\n' \
       '\tdef __init__(self):\n'


def refiner(something):
    value = ""  # e
    if type(something).__name__ == 'dict':  # e
        value += '{'
        for k in something:
            value += '\'' + k + '\':' + refiner(something[k]) + ','
        value = value[:len(value) - 1] + '}'
    elif type(something).__name__ == 'str':
        value = "'"
        if '\n' in something:
            something = something.replace('\n', '\\n') + "'"
        if "'" in something:
            value += something.replace('\'', '\\\'') + "'"
        else:
            value += something + "'"  # e
    elif type(something).__name__ == 'Value':
        value = refiner(something.value)
    elif type(something).__name__ == 'ArrayList':
        value = '['
        for i in something.items:
            value += refiner(i) + ','
        value = value[:len(value) - 1] + ']'
    else:
        value = something
    return str(value)


def addmore(code, var, value):
    return code + '\t\tself.' + var + '=' + str(refiner(value)) + '\n'  # e


log_data = ''


class Lexer:
    def __init__(self):
        self.tokens = []

    def tokenize(self, filename, code, lin_num, pre_include=[]):
        # print(code)
        for i in pre_include:
            code = 'Include(`' + i + '`);\n' + code
        rules = [
            ('PYTHON', r'Python+(.|\n|)+\[\[+(.|\n|)+\]\]'),  # PYTHON
            ('COMMENT2', r'<#(\n|.)*#>'),  # COMMENTS
            ('COMMENT1', r'#.*'),  # COMMENTS
            ('PHP', r'Php'),  # PHP
            ('LANGUAGES', r'EN'),
            ('NUM',r'Num'),
            ('IMPORTKWD', r'Include\(`[^`]*`\);'),
            ('JS', r'Js'),  # JS
            ('CLINE', r'Line'),
            ('TYPE', 'Type'),
            ('ID', 'Id'),
            ('TO', r'to'),
            ('FROM', r'From'),
            ('LIMITS', r'limits'),
            ('INCREAMENT', r'plus'),
            ('DECREAMENT', r'minus'),
            ('CONDITION', 'Condition'),
            ('JUMP', 'Jump'),
            ('CSPACE', r'Space'),
            ('KILL', r'Kill'),
            ('SESSION_KEY', r'Session.Key'),  # Server Segment
            ('COOKIE_KEY_TIME', r'Cookie.Key.Time'),  # Server Segment
            ('COOKIE_KEY', r'Cookie.Key'),  # Server Segment
            ('FILES_KEY', r'Files.Key'),  # Server Segment
            ('GET_KEY', r'Get.Key'),  # Server Segment
            ('POST_KEY', r'Post.Key'),  # Server Segment
            ('LOOP', r'Loop'),
            ('GLOBAL', r'Global'),  # &
            ('DIE', r'Die'),  # Die
            ('PRINT', r'Print'),  # Print
            ('RETURN', r'Return'),  # Return
            ('IF', r'If'),  # If
            ('OR', r'Or'),  # Or
            ('AND', r'And'),  # And
            ('ELSEIF', r'Elseif'),  # Elseif
            ('ELSE', r'Else'),  # Else
            ('CASE', r'case'),  # Case
            ('TIMES', r'Times'),  # Times
            ('ADD', r'Add'),  # Add
            ('AT', r'at'),  # at
            ('DELETE', r'Delete'),  # Delete
            ('LANG', r'Lang'),  # Lang
            ('REPLACE', r'Replace'),  # Replace
            ('WITH', r'With'),  # With
            ('POPULATE', r'Populate'),  # Populate
            ('FIND', r'Find'),  # Find
            ('XML', r'Xml'),  # Xml
            ('JSON', r'Json'),  # Json
            ('END', r'End'),  # End
            ('MIX', r'Mix'),  # Mix
            ('SPLIT', r'Split'),  # Split
            ('GET', r'Get'),  # Get
            ('TIME', r'Time'),  # Time
            ('LENGTH', r'Length'),  # Length
            ('LPAREN', r'\('),  # (
            ('RPAREN', r'\)'),  # )
            ('LBRACE', r'\{'),  # {
            ('RBRACE', r'\}'),  # }
            ('LBRACKET', r'\['),  # [
            ('RBRACKET', r'\]'),  # ]
            ('AMP', r'\&'),  # &
            ('LIST', r'List'),
            ('COMMA', r','),  # ,
            ('POINT', r'[.]'),  # .
            ('PCOMMA', r';'),  # ;
            ('COLON', r':'),  # :
            ('EQ', r'=='),  # ==
            ('NE', r'!='),  # !=
            ('LE', r'<='),  # <=
            ('GE', r'>='),  # >=
            ('ATTR', r'\='),  # =
            ('LT', r'<'),  # <
            ('GT', r'>'),  # >
            ('PLUS', r'\+'),  # +
            ('MINUS', r'-'),  # -
            ('MULT', r'\*'),  # *
            ('DIV', r'\/'),  # /
            ('VID', r'[a-z]\w*'),  # Variable IDENTIFIERS
            ('FID', r'[A-Z]\w*'),  # Function IDENTIFIERS
            ('FLOAT_CONST', r'\d(\d)*\.\d(\d)*'),  # FLOAT
            ('INTEGER_CONST', r'\d(\d)*'),  # INT
            ('STRING_CONST1', r'`[^`]*`'),  # CONST STRING
            ('STRING_CONST2', r'"[^"]*"'),  # CONST STRING
            ('NEWLINE', r'\n'),  # NEW LINE
            ('SPACEX', r'\s'),
            ('MISMATCH', r'(.| )')  # ANOTHER CHARACTER
        ]
        importfound = False
        tokens_join = '|'.join('(?P<%s>%s)' % x for x in rules)
        lin_start = 0
        col = 1
        for m in re.finditer(tokens_join, code):
            token_type = m.lastgroup
            token_lexeme = m.group(token_type)
            if token_type == 'NEWLINE':
                lin_start = m.end()
                lin_num = lin_num + 1
                col = 1
            elif token_type == 'SPACEX':
                col += 1
            elif token_type == 'MISMATCH':
                raise RuntimeError(
                    'Unexpected char "{}" from {} on col:{} line:{}'.format(token_lexeme, filename, col,
                                                                            lin_num - len(pre_include)))
            elif token_type == 'COMMENT1':
                for i in token_lexeme:
                    if i in [' ']:
                        col += 1
                    elif i in ['\n']:
                        col = 1
                        lin_num += 1
            elif token_type == 'COMMENT2':
                for i in token_lexeme:
                    if i in [' ']:
                        col += 1
                    elif i in ['\n']:
                        col = 1
                        lin_num += 1
            # '''('SESSION_KEY', r'Session.Key'),  # Server Segment
            # ('COOKIE_KEY_TIME', r'Cookie.Key.Time'),  # Server Segment
            # ('COOKIE_KEY', r'Cookie.Key'),  # Server Segment
            # ('FILES_KEY', r'Files.Key'),  # Server Segment
            # ('GET_KEY', r'Get.Key'),  # Server Segment
            # ('POST_KEY', r'Post.Key'),  # Server Segment'''
            elif token_type in ['SESSION_KEY', 'COOKIE_KEY_TIME', 'COOKIE_KEY', 'FILES_KEY', 'GET_KEY', 'POST_KEY']:
                col = (m.start() - lin_start) + 1
                self.tokens.append(Token(token_lexeme, 'VID', lin_num - len(pre_include), col, filename))
            elif token_type == 'IMPORTKWD':
                col = (m.start() - lin_start) + 1
                toimport = token_lexeme.replace('Include', '').replace('`', '').replace('"', '').replace('(',
                                                                                                         '').replace(
                    ')', '').replace(';', '')
                l = Lexer()
                self.tokens += l.tokenize(toimport, open(os.getcwd()+'/text/'+toimport).read(), 1)
            elif token_lexeme.isupper() and token_lexeme.isalnum():
                col = (m.start() - lin_start) + 1
                token_type = 'GLOBAL_VID';
                if token_lexeme in ['EN', 'ES']:
                    token_type = 'LANGUAGES'
                self.tokens.append(Token(token_lexeme, token_type, lin_num - len(pre_include), col, filename))
            else:
                col = (m.start() - lin_start) + 1
                if token_type == 'STRING_CONST1':
                    token_lexeme = token_lexeme.replace('`', '')
                elif token_type == 'STRING_CONST2':
                    token_lexeme = token_lexeme.replace('"', '')
                for i in token_lexeme:
                    if i in ['\n']:
                        lin_num += 1
                self.tokens.append(Token(token_lexeme, token_type, lin_num - len(pre_include), col, filename))
        return self.tokens


class Parser:
    def __init__(self, tokens, glob):
        self.tokens = tokens
        self.counter = -1
        self.c_t = None
        self.advance()
        self.glob = glob

    def advance(self):
        self.counter += 1
        if self.counter == len(self.tokens):
            raise RuntimeError('Exception: EOF')
        self.c_t = self.tokens[self.counter]
        return self.c_t

    def eat(self, type):
        if self.c_t.type == type:
            data = self.c_t
            self.advance()
            return data
        else:
            raise RuntimeError("Expected '{}' but found '{}' line:{} col:{} in {}"
                               .format(type, self.c_t.value, self.c_t.line, self.c_t.col, self.c_t.file))

    def eatx(self, types=[]):
        if self.c_t.type in types:
            data = self.c_t
            self.advance()
            return data
        else:
            raise RuntimeError("Expected '{}' but found '{}' line:{} col:{} in {}"
                               .format(['\' ' + v + ' \'or' for v in types], self.c_t.value, self.c_t.line,
                                       self.c_t.col, self.c_t.file))

    def parse(self):
        self.tokens.append(Token('end of file', 'EOF', -1, -1))
        return self.statements()

    # Scanners
    '''scan vid scans variable based functions such as Time, Replace,
    example.
        var.subvar.subvar.Replace("s")With("S");
    '''
    def scan_vid(self, stmts=[]):
        vars = []
        prelocated = False
        while (self.c_t.type == 'VID' or self.c_t.type == 'GLOBAL_VID') and not prelocated:
            chain = [self.c_t]
            self.advance()
            while self.c_t.type == 'POINT':
                self.advance()
                if self.c_t.type == 'VID':
                    chain.append(self.c_t)
                    self.advance()
                elif self.c_t.type == 'REPLACE':
                    self.advance()
                    self.eat('LPAREN')
                    toreplace = self.expr()
                    self.eat('RPAREN')
                    self.eat('WITH')
                    self.eat('LPAREN')
                    forreplace = self.expr()
                    self.eat('RPAREN')
                    self.eat('PCOMMA')
                    stmts.append(SelfReplaceExp(
                        chain, toreplace, forreplace))
                    prelocated = True
                    break
                elif self.c_t.type == 'DELETE':
                    self.advance()
                    self.eat('LPAREN')
                    e = self.expr()
                    self.eat('RPAREN')
                    stmts.append(DeleteExperssion(chain, e))
                    self.eat('PCOMMA')
                    prelocated = True
                    break
                elif self.c_t.type == 'PLUS':
                    self.advance()
                    self.eat('ATTR')
                    exp = self.expr()
                    self.eat('PCOMMA')
                    prelocated = True
                    stmts.append(DotAddExpression(chain, exp))
                    break
                elif self.c_t.type == 'TIME':
                    self.advance()
                    self.eat('LPAREN')
                    _format = self.expr()
                    self.eat('RPAREN')
                    self.eat('TO')
                    self.eat('LPAREN')
                    _toformat = self.expr()
                    self.eat('RPAREN')
                    _operator=None
                    _howmuch=None
                    # if self.c_t.type in ['INCREAMENT','DECREAMENT']:
                    _operator = self.eatx(['INCREAMENT', 'DECREAMENT'])
                    self.eat('LPAREN')
                    _howmuch = self.expr()
                    self.eat('RPAREN')
                    prelocated = True
                    stmts.append(TimeExpression(copy.copy(chain), _format, _toformat, _operator, _howmuch))
                    self.eat('PCOMMA')
                    break
                elif self.c_t.type == 'ADD':
                    self.advance()
                    self.eat('LPAREN')
                    exp = self.expr()
                    self.eat('RPAREN')
                    at = None
                    if self.c_t.type == 'AT':
                        self.eat('LPAREN')
                        at = self.expr()
                        self.eat('RPAREN')
                    prelocated = True
                    stmts.append(AddExpression(chain, exp, at))
                    self.eat('PCOMMA')
                    break
                elif self.c_t.type == 'INTEGER_CONST':
                    chain.append(int(self.c_t.value))
                    self.advance()
                elif self.c_t.type == 'IF':
                    self.advance()
                    cd = self.expr()
                    self.eat('LBRACKET')
                    stmt = self.compound()
                    ex = IfStatement(BinOp(ChainExpression([VarExp(v) for v in chain]), Token('==', 'EQ', 0, 0), cd),
                                     stmt, None, [])
                    self.eat('RBRACKET')
                    while self.c_t.type == 'ELSEIF':
                        self.advance()
                        pct = self.expr()
                        self.eat('LBRACKET')
                        stmt = self.compound()
                        ex.elseifbodies.append({'condition': BinOp(ChainExpression([VarExp(v) for v in chain]),
                                                                   Token('==', 'EQ', 0, 0), pct), 'body': stmt})
                        self.eat('RBRACKET')
                    if self.c_t.type == 'ELSE':
                        self.advance()
                        self.eat('LBRACKET')
                        stmt = self.compound()
                        ex.elsebody = stmt
                        self.eat('RBRACKET')
                    stmts.append(VarIfExpression(chain, ex))
                    self.eat('PCOMMA')
                    prelocated = True
                    break
            vars.append(copy.copy(chain))
        if not prelocated and self.c_t.type == 'ATTR':
            self.advance()
            mvx = MultiVarAssignExp([])
            for i in vars:
                mvx.listexp.append(VarAssignExp(i, self.expr()))
            self.eat('PCOMMA')
            stmts.append(mvx)
    #scan print scan print statement such as arguments of print function
    '''
        Print (9,4,Line);
    '''
    def scan_print(self, stmts=[]):
        self.advance()
        self.eat('LPAREN')
        stmts.append(PrintStatement(self.argparserex(sep='COMMA')))
        self.eat('RPAREN')
        self.eat('PCOMMA')
    #scan loop scan loop body such as condition and times
    '''
        a=(1,2,3,4,5,6,7);
        Loop(a) Condition(true)Times(a.Length):[#this is condition and times
            Print(value,Line);#this is loop body
        ]
    '''
    def scan_loop(self, stmts=[]):
        self.advance()
        self.eat('LPAREN')
        vid = self.eat('VID')
        self.eat('RPAREN')
        timeexp = None
        conditionexp = None
        body = None
        if self.c_t.type == 'TIMES':
            self.advance()
            self.eat('LPAREN')
            timeexp = self.expr()
            self.eat('RPAREN')
        if self.c_t.type == 'CONDITION':
            self.advance()
            self.eat('LPAREN')
            conditionexp = self.expr()
            self.eat('RPAREN')
        self.eat('COLON')
        self.eat('LBRACKET')
        body = self.compound()
        self.eat('RBRACKET')
        stmts.append(LoopStatement(vid, conditionexp, timeexp, body))
    #scan if scan if statement such as if body ,else body, elseif body and condition
    ''' 
        a=90;
        If a <100:[
            Print(a,Space,"is <100");
        ]
        Elseif a>100:[
            Print(a,Space,"is >100");
        ]
        Else:[
            Print(a,Space,"is ",a);
        ]
    '''
    def scan_if(self, stmts=[]):
        self.advance()
        cd = self.expr()
        self.eat('COLON')
        self.eat('LBRACKET')
        stmt = self.compound()
        ex = IfStatement(cd, stmt, None, [])
        self.eat('RBRACKET')
        while self.c_t.type == 'ELSEIF':
            self.advance()
            pct = self.expr()
            self.eat('COLON')
            self.eat('LBRACKET')
            stmt = self.compound()
            ex.elseifbodies.append({'condition': pct, 'body': stmt})
            self.eat('RBRACKET')
        if self.c_t.type == 'ELSE':
            self.advance()
            self.eat('COLON')
            self.eat('LBRACKET')
            stmt = self.compound()
            ex.elsebody = stmt
            self.eat('RBRACKET')
        stmts.append(ex)
    #this  function is a exceptional function of else if body when else if body without any if
    '''
        Elseif (true):[]#Elseif without if causes exception 
    '''
    def scan_elseif(self):
        print("ElseIf Comming without if")
        raise RuntimeError("from {} Elseif without if at line:{} col:{}"
                           .format(self.c_t.file, self.c_t.line, self.c_t.col))
    #this function scan return statement
    '''
        MyFunction(number):[
            Return number*number;
        ];
        Print (MyFunction(25));#625
    '''
    def scan_return(self, stmts=[]):
        self.advance()
        stmts.append(ReturnStatement(self.expr()))
        self.eat('PCOMMA')
    #this function scan List function with dictionary argument
    '''
        a=(name="sonu",from="india");
        List(a);
        Print(name,Space,from);
    '''
    def scan_list(self, stmts=[]):
        self.advance()
        stmts.append(ListExp(self.expr()))
        self.eat('PCOMMA')
    #this function scan global variable access
    '''
        DB.self="something";
        Print(DB.self,Line);
    '''
    def scan_global(self, stmts=[]):
        self.advance()
        listvar = []
        listexp = []
        while self.c_t.type == 'VID':
            listvar.append(self.c_t)
            self.advance()
        self.eat('ATTR')
        for v in listvar:
            listexp.append(self.expr())
        self.eat('PCOMMA')
        stmts.append(GlobalExp(listvar, listexp))
    #this function scan kill expression to kill or erase variable record from local and global variable
    '''
        a=90;
        Print (a,Line);#its print 90
        Kill(a);#this kill variable "a" 
        Print (a, Line);#its throw an error at run time for undefined variable 'a'
    '''
    def scan_kill(self, stmts=[]):
        self.advance()
        self.eat('LPAREN')
        id = self.eat('VID')
        self.eat('RPAREN')
        self.eat('PCOMMA')
        stmts.append(KillVarExp(id))

    # Scanner ends
    #this scan function bodies ifelse bodies ,loops bodies
    def compound(self):
        stmts = []
        while self.c_t.type != 'EOF':
            if self.c_t.type == 'VID':
                self.scan_vid(stmts)
            elif self.c_t.type == 'PRINT':
                self.scan_print(stmts)
            elif self.c_t.type == 'GLOBAL':
                self.scan_global(stmts)
            elif self.c_t.type == 'LOOP':
                self.scan_loop(stmts)
            elif self.c_t.type == 'IF':
                self.scan_if(stmts)
            elif self.c_t.type == 'KILL':
                self.scan_kill(stmts)
            elif self.c_t.type == 'ELSEIF':
                self.scan_elseif()
            elif self.c_t.type == 'RETURN':
                self.scan_return(stmts)
            elif self.c_t.type == 'GLOBAL_VID':
                vars = []
                prelocated = False
                while self.c_t.type == 'VID' or self.c_t.type == 'GLOBAL_VID' and not prelocated:
                    chain = [self.c_t]
                    self.advance()
                    while self.c_t.type == 'POINT':
                        self.advance()
                        if self.c_t.type == 'VID':
                            chain.append(self.c_t)
                            self.advance()
                        elif self.c_t.type == 'REPLACE':
                            self.advance()
                            self.eat('LPAREN')
                            toreplace = self.expr()
                            self.eat('RPAREN')
                            self.eat('WITH')
                            self.eat('LPAREN')
                            forreplace = self.expr()
                            self.eat('RPAREN')
                            self.eat('PCOMMA')
                            stmts.append(SelfReplaceExp(chain, toreplace, forreplace))
                            prelocated = True
                            break
                        elif self.c_t.type == 'ADD':
                            self.advance()
                            self.eat('LPAREN')
                            exp = self.expr()
                            self.eat('RPAREN')
                            at = None
                            if self.c_t.type == 'AT':
                                self.eat('LPAREN')
                                at = self.expr()
                                self.eat('RPAREN')
                            prelocated = True
                            stmts.append(AddExpression(chain, exp, at))
                            self.eat('PCOMMA')
                            break
                        elif self.c_t.type == 'DELETE':
                            self.advance()
                            self.eat('LPAREN')
                            e = self.expr()
                            self.eat('RPAREN')
                            stmts.append(DeleteExperssion(chain, e))
                            self.eat('PCOMMA')
                            prelocated = True
                            break
                        elif self.c_t.type == 'PLUS':
                            self.advance()
                            self.eat('ATTR')
                            exp = self.expr()
                            self.eat('PCOMMA')
                            prelocated = True
                            stmts.append(DotAddExpression(chain, exp))
                            break
                        elif self.c_t.type == 'INTEGER_CONST':
                            chain.append(int(self.c_t.value))
                            self.advance()
                    vars.append(copy.copy(chain))
                if not prelocated and self.c_t.type == 'ATTR':
                    self.advance()
                    mvx = MultiVarAssignExp([])
                    for i in vars:
                        mvx.listexp.append(VarAssignExp(i, self.expr()))
                    self.eat('PCOMMA')
                    stmts.append(mvx)

            elif self.c_t.type == 'LIST':
                self.scan_list(stmts)
            elif self.c_t.type == 'FID':
                temp = self.c_t
                if temp.value in list(self.glob.functions.keys()):
                    stmts.append(self.expr())
                    self.eat('PCOMMA')
                elif temp.value in list(self.glob.py_functions.keys()):
                    self.c_t.type = 'PFID'
                    stmts.append(self.expr())
                    self.eat('PCOMMA')
            else:
                break
        return CompoundStatement(stmts)
    #this scan whole programe such as assignment function calling ,definition loop elseif id , jump
    def statements(self):
        stmts = []
        while self.c_t.type != 'EOF':
            if self.c_t.type == 'VID':
                self.scan_vid(stmts)
            elif self.c_t.type == 'KILL':
                self.scan_kill(stmts)
            elif self.c_t.type == 'PYTHON':
                code = re.sub(r'Python+(|.|\n)+\[\[', r'', self.c_t.value)
                code = code.replace(']]', '')
                stmts.append(PythonCodeExp(code));
                self.advance()
            elif self.c_t.type == 'GLOBAL_VID':
                temp = self.c_t
                self.advance()
                data = {}
                dictexp = DictExp(temp, None, data)
                # if temp.file == 'configure.q':
                if os.path.basename(temp.file) == 'configure.q':
                    self.eat('LPAREN')
                    ep = self.expr()
                    self.eat('RPAREN')
                    dictexp.exp = ep
                    while self.c_t.type == 'VID':
                        temp = self.c_t
                        self.advance()
                        self.eat('LPAREN')
                        exp = self.expr()
                        self.eat('RPAREN')
                        dictexp.table.update({temp: exp})
                    self.eat('PCOMMA')
                    stmts.append(dictexp)
                elif self.c_t.type == 'POINT':
                    vars = []
                    self.advance()
                    prelocated = False
                    while self.c_t.type == 'VID' or self.c_t.type == 'GLOBAL_VID' and not prelocated:
                        chain = [temp, self.c_t]
                        self.advance()
                        while self.c_t.type == 'POINT':
                            self.advance()
                            if self.c_t.type == 'VID':
                                chain.append(self.c_t)
                                self.advance()
                            elif self.c_t.type == 'REPLACE':
                                self.advance()
                                self.eat('LPAREN')
                                toreplace = self.expr()
                                self.eat('RPAREN')
                                self.eat('WITH')
                                self.eat('LPAREN')
                                forreplace = self.expr()
                                self.eat('RPAREN')
                                self.eat('PCOMMA')
                                stmts.append(SelfReplaceExp(chain, toreplace, forreplace))
                                prelocated = True
                                break
                            elif self.c_t.type == 'PLUS':
                                self.advance()
                                self.eat('ATTR')
                                exp = self.expr()
                                self.eat('PCOMMA')
                                prelocated = True
                                stmts.append(DotAddExpression(chain, exp))
                                break
                            elif self.c_t.type == 'DELETE':
                                self.advance()
                                self.eat('LPAREN')
                                e = self.expr()
                                self.eat('RPAREN')
                                stmts.append(DeleteExperssion(chain, e))
                                self.eat('PCOMMA')
                                prelocated = True
                                break
                            elif self.c_t.type == 'ADD':
                                self.advance()
                                self.eat('LPAREN')
                                exp = self.expr()
                                self.eat('RPAREN')
                                prelocated = True
                                at = None
                                if self.c_t.type == 'AT':
                                    self.advance()
                                    self.eat('LPAREN')
                                    at = self.expr()
                                    self.eat('RPAREN')
                                stmts.append(AddExpression(chain, exp, at))
                                self.eat('PCOMMA')
                                break
                            elif self.c_t.type == 'INTEGER_CONST':
                                chain.append(int(self.c_t.value))
                                self.advance()
                        vars.append(copy.copy(chain))
                    if not prelocated and self.c_t.type == 'ATTR':
                        self.advance()
                        mvx = MultiVarAssignExp([])
                        for i in vars:
                            mvx.listexp.append(VarAssignExp(i, self.expr()))
                        self.eat('PCOMMA')
                        stmts.append(mvx)

            elif self.c_t.type == 'PRINT':
                self.scan_print(stmts)
            elif self.c_t.type == 'GLOBAL':
                self.scan_global(stmts)
            elif self.c_t.type == 'IF':
                self.scan_if(stmts)
            elif self.c_t.type == 'ELSEIF':
                self.scan_elseif()
            elif self.c_t.type == 'LIST':
                self.scan_list(stmts)
            elif self.c_t.type == 'ID':
                self.advance()
                self.eat('LPAREN')
                data = self.expr()
                self.eat('RPAREN')
                self.eat('PCOMMA')
                stmts.append(IdExp(data))
            elif self.c_t.type == 'JUMP':
                self.advance()
                self.eat('LPAREN')
                idexp = self.expr()
                timeexp = None
                conditionexp = None
                self.eat('RPAREN')
                if self.c_t.type == 'TIMES':
                    self.advance()
                    self.eat('LPAREN')
                    timeexp = self.expr()
                    self.eat('RPAREN')
                if self.c_t.type == 'CONDITION':
                    self.advance()
                    self.eat('LPAREN')
                    conditionexp = self.expr()
                    self.eat('RPAREN')
                self.eat('PCOMMA')
                stmts.append(JumpExp(idexp, timeexp, conditionexp))
            elif self.c_t.type == 'LOOP':
                self.scan_loop(stmts)
            elif self.c_t.type == 'FID':
                temp = self.c_t
                if temp.value in list(self.glob.functions.keys()):
                    stmts.append(self.expr())
                    self.eat('PCOMMA')
                elif temp.value in list(self.glob.py_functions.keys()):
                    self.c_t.type = 'PFID'
                    stmts.append(self.expr())
                    self.eat('PCOMMA')
                else:
                    self.advance()
                    self.eat('LPAREN')
                    arguments = self.args()
                    self.eat('RPAREN')
                    if self.c_t.type == 'PCOMMA':
                        self.advance()
                        stmts.append(PyFuncExp(temp, arguments))
                        self.glob.py_functions.update({temp.value: 0})
                    elif self.c_t.type == 'COLON':
                        self.advance()
                        self.eat('LBRACKET')
                        self.glob.functions.update({temp.value: 0})
                        body = self.compound()
                        self.eat('RBRACKET')
                        self.eat('PCOMMA')
                        stmts.append(FuncExp(temp, arguments, body))
            else:
                break
        return Statements(stmts)
    #this scan rigth hand evaluable expression consist of two compresion sepreted by And ,Or
    def expr(self):
        left = self.compr()
        temp = None
        while self.c_t.type in ['AND', 'OR']:
            temp = self.c_t
            self.advance()
            left = BinOp(left, temp, self.compr())
            # print("Logical\n",left.left,temp.value,left.right)
        return left
    #this scan arithematic expression sepreted by <,>,<=,>=,!=,==
    def compr(self):
        left = self.arithmetic()
        temp = None
        while self.c_t.type in ['LT', 'GT', 'EQ', 'LE', 'GE', 'NE']:
            temp = self.c_t
            self.advance()
            left = BinOp(left, temp, self.arithmetic())
            # print("Comparision\n", left.left, temp.value, left.right)
        return left
    #this scan mathematical expression sepreted by +,-,&
    def arithmetic(self):
        left = self.term()
        temp = None
        while self.c_t.type in ['PLUS', 'MINUS', 'AMP']:
            temp = self.c_t
            self.advance()
            left = BinOp(left, temp, self.term())
            # print("Arithematics\n", left.left, temp.value, left.right)
        return left
    #this scan mathematical expression sepreted by *,/
    def term(self):
        left = self.factor()
        temp = None
        while self.c_t.type in ['DIV', 'MULT']:
            temp = self.c_t
            self.advance()
            left = BinOp(left, temp, self.factor())
            # print("Term-arithematics\n", left.left, temp.value, left.right)
        return left
    #this scan expression
    def factor(self):
        temp = self.c_t
        # print("Terminal and NonTerminal\n", temp.value)
        if temp.type in ['INTEGER_CONST', 'FLOAT_CONST']:
            self.advance()
            return NumberExp(temp)
        elif temp.type == 'LPAREN':
            self.advance()
            if self.c_t.type == 'VID' and self.tokens[self.counter + 1].type == 'ATTR':
                args = self.argparser(sep='COMMA')
                self.eat('RPAREN')
                chain = [TupleExp(args)]
                while self.c_t.type == 'POINT':
                    self.advance()
                    if self.c_t.type == 'VID':
                        chain.append(DotVarAccess(self.c_t))
                        self.advance()
                    elif self.c_t.type == 'INTEGER_CONST':
                        chain.append(DotVarAccess(self.c_t))
                        self.advance()
                    elif self.c_t.type == 'END':
                        chain.append(EndExpression())
                        self.advance()
                    elif self.c_t.type == 'REPLACE':
                        self.advance()
                        self.eat('LPAREN')
                        e = self.expr()
                        self.eat('RPAREN')
                        self.eat('WITH')
                        self.eat('LPAREN')
                        w = self.expr()
                        self.eat('RPAREN')
                        chain.append(AssignReplaceExp(None, e, w))
                    elif self.c_t.type == 'SPLIT':
                        self.advance()
                        self.eat('LPAREN')
                        exp = self.expr()
                        self.eat('RPAREN')
                        chain.append(SplitExp(exp))
                    elif self.c_t.type == 'FIND':
                        self.advance()
                        self.eat('LPAREN')
                        _what = self.expr()
                        self.eat('RPAREN')
                        _from = None
                        _to = None
                        if self.c_t.type == 'FROM':
                            self.advance()
                            self.eat('LPAREN')
                            _from = self.expr()
                            self.eat('RPAREN')
                        if _from and self.c_t.type == 'TO':
                            self.advance()
                            self.eat('LPAREN')
                            _to = self.expr()
                            self.eat('RPAREN')
                        chain.append(FindExpression(_what, _from, _to))
                    elif self.c_t.type == 'MIX':
                        self.advance()
                        chain.append(MixExpression())
                    elif self.c_t.type == 'LANGUAGES':
                        chain.append(LangAccessExp(None, self.c_t))
                        self.advance()
                if self.c_t.type == 'LPAREN':
                    self.advance()
                    e = self.expr()
                    self.eat('RPAREN')
                    chain.append(CombinationalExp(None, e))
                return ChainExpression(chain)
            else:
                e = [self.expr()]
                if self.c_t.type == 'COMMA':
                    while self.c_t.type == 'COMMA':
                        self.advance()
                        e.append(self.expr())
                if len(e) == 1:
                    self.eat('RPAREN')
                    return e[0]
                else:
                    self.eat('RPAREN')
                    return ArrayExp(temp, e)

            temp = self.expr()
            self.eat('RPAREN')
            return temp
        elif temp.type == 'MINUS':
            self.advance()
            return UnaryExp(self.factor())
        elif temp.type == 'VID':
            self.advance()
            chain = [VarExp(temp)]
            while self.c_t.type == 'POINT':
                self.advance()
                if self.c_t.type == 'VID':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'INTEGER_CONST':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'END':
                    chain.append(EndExpression())
                    self.advance()
                elif self.c_t.type == 'SPLIT':
                    self.advance()
                    self.eat('LPAREN')
                    exp = self.expr()
                    self.eat('RPAREN')
                    chain.append(SplitExp(exp))
                elif self.c_t.type == 'REPLACE':
                    self.advance()
                    self.eat('LPAREN')
                    e = self.expr()
                    self.eat('RPAREN')
                    self.eat('WITH')
                    self.eat('LPAREN')
                    w = self.expr()
                    self.eat('RPAREN')
                    chain.append(AssignReplaceExp(None, e, w))
                elif self.c_t.type == 'FIND':
                    self.advance()
                    self.eat('LPAREN')
                    _what = self.expr()
                    self.eat('RPAREN')
                    _from = None
                    _to = None
                    if self.c_t.type == 'FROM':
                        self.advance()
                        self.eat('LPAREN')
                        _from = self.expr()
                        self.eat('RPAREN')
                    if _from and self.c_t.type == 'TO':
                        self.advance()
                        self.eat('LPAREN')
                        _to = self.expr()
                        self.eat('RPAREN')
                    chain.append(FindExpression(_what, _from, _to))
                elif self.c_t.type == 'MIX':
                    self.advance()
                    chain.append(MixExpression())
                elif self.c_t.type == 'LANGUAGES':
                    chain.append(LangAccessExp(None, self.c_t))
                    self.advance()
                elif self.c_t.type == 'LENGTH':
                    chain.append(LengthExpression())
                    self.advance()
                elif self.c_t.type == 'GET':
                    self.advance()
                    self.eat('LPAREN')
                    _from = _to = None
                    if self.c_t.type == '':
                        _from = self.eat('INTEGER_CONST')
                    elif self.c_t.type == 'STRING_CONST1':
                        _from = self.eat('STRING_CONST1')
                    elif self.c_t.type == 'STRING_CONST2':
                        _from = self.eat('STRING_CONST2')
                    self.eat('MINUS')
                    if self.c_t.type == 'INTEGER_CONST':
                        _to = self.eat('INTEGER_CONST')
                    elif self.c_t.type == 'STRING_CONST1':
                        _to = self.eat('STRING_CONST1')
                    elif self.c_t.type == 'STRING_CONST2':
                        _to = self.eat('STRING_CONST2')
                    self.eat('RPAREN')
                    limit = None
                    if _from and _to:
                        if _from.type in ['STRING_CONST1', 'STRING_CONST2']:
                            if self.c_t.type == 'LIMITS':
                                self.advance()
                                self.eat('LPAREN')
                                limit = self.expr()
                                self.eat('RPAREN')
                    chain.append(GetExpression(_from, _to, limit))
                elif self.c_t.type == 'NUM':
                    self.advance()
                    self.eat('LPAREN')
                    tmp=self.expr()
                    self.eat('RPAREN')
                    chain.append(NumExpression(tmp))
            if self.c_t.type == 'LPAREN':
                self.advance()
                if self.tokens[self.counter+1].type == 'MINUS':
                    _from = _to = None
                    if self.c_t.type == '':
                        _from = self.eat('INTEGER_CONST')
                    elif self.c_t.type == 'STRING_CONST1':
                        _from = self.eat('STRING_CONST1')
                    elif self.c_t.type == 'STRING_CONST2':
                        _from = self.eat('STRING_CONST2')
                    self.eat('MINUS')
                    if self.c_t.type == 'INTEGER_CONST':
                        _to = self.eat('INTEGER_CONST')
                    elif self.c_t.type == 'STRING_CONST1':
                        _to = self.eat('STRING_CONST1')
                    elif self.c_t.type == 'STRING_CONST2':
                        _to = self.eat('STRING_CONST2')
                    self.eat('RPAREN')
                    limit = None
                    if (_from and _to) or _to:
                        if _from.type in ['STRING_CONST1', 'STRING_CONST2']:
                            if self.c_t.type == 'LIMITS':
                                self.advance()
                                self.eat('LPAREN')
                                limit = self.expr()
                                self.eat('RPAREN')
                    chain.append(GetExpression(_from, _to, limit))
                else:
                    e = self.expr()
                    self.eat('RPAREN')
                    chain.append(CombinationalExp(None, e))
            return ChainExpression(chain)
        elif temp.type == 'STRING_CONST1':
            self.advance()
            temp.value = temp.value.replace('`', '')
            chain = [StringExp(temp)]
            while self.c_t.type == 'POINT':
                self.advance()
                if self.c_t.type == 'VID':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'INTEGER_CONST':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'END':
                    chain.append(EndExpression())
                    self.advance()
                elif self.c_t.type == 'REPLACE':
                    self.advance()
                    self.eat('LPAREN')
                    e = self.expr()
                    self.eat('RPAREN')
                    self.eat('WITH')
                    self.eat('LPAREN')
                    w = self.expr()
                    self.eat('RPAREN')
                    chain.append(AssignReplaceExp(None, e, w))
                elif self.c_t.type == 'FIND':
                    self.advance()
                    self.eat('LPAREN')
                    _what = self.expr()
                    self.eat('RPAREN')
                    _from = None
                    _to = None
                    if self.c_t.type == 'FROM':
                        self.advance()
                        self.eat('LPAREN')
                        _from = self.expr()
                        self.eat('RPAREN')
                    if _from and self.c_t.type == 'TO':
                        self.advance()
                        self.eat('LPAREN')
                        _to = self.expr()
                        self.eat('RPAREN')
                    chain.append(FindExpression(_what, _from, _to))
                elif self.c_t.type == 'MIX':
                    self.advance()
                    chain.append(MixExpression())
                elif self.c_t.type == 'LANGUAGES':
                    chain.append(LangAccessExp(None, self.c_t))
                    self.advance()
            return ChainExpression(chain)
        elif temp.type == 'STRING_CONST2':
            self.advance()
            temp.value = temp.value.replace('"', '')
            chain = [StringExp(temp)]
            while self.c_t.type == 'POINT':
                self.advance()
                if self.c_t.type == 'VID':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'INTEGER_CONST':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'END':
                    chain.append(EndExpression())
                    self.advance()
                elif self.c_t.type == 'REPLACE':
                    self.advance()
                    self.eat('LPAREN')
                    e = self.expr()
                    self.eat('RPAREN')
                    self.eat('WITH')
                    self.eat('LPAREN')
                    w = self.expr()
                    self.eat('RPAREN')
                    chain.append(AssignReplaceExp(None, e, w))
                elif self.c_t.type == 'FIND':
                    self.advance()
                    self.eat('LPAREN')
                    _what = self.expr()
                    self.eat('RPAREN')
                    _from = None
                    _to = None
                    if self.c_t.type == 'FROM':
                        self.advance()
                        self.eat('LPAREN')
                        _from = self.expr()
                        self.eat('RPAREN')
                    if _from and self.c_t.type == 'TO':
                        self.advance()
                        self.eat('LPAREN')
                        _to = self.expr()
                        self.eat('RPAREN')
                    chain.append(FindExpression(_what, _from, _to))
                elif self.c_t.type == 'MIX':
                    self.advance()
                    chain.append(MixExpression())
                elif self.c_t.type == 'LANGUAGES':
                    chain.append(LangAccessExp(None, self.c_t))
                    self.advance()
            return ChainExpression(chain)
        elif temp.type == 'CLINE':
            self.advance()
            if self.c_t.type == 'LPAREN':
                self.advance()
                data = LineExp(self.expr())
                self.eat('RPAREN')
                return data
            else:
                return LineExp(None)
        elif temp.type == 'CSPACE':
            self.advance()
            if self.c_t.type == 'LPAREN':
                self.advance()
                data = SpaceExp(self.expr())
                self.eat('RPAREN')
                return data
            else:
                return SpaceExp(None)
        elif temp.type == 'FID':
            if temp.value in self.glob.py_functions:
                self.advance()
                self.eat('LPAREN')
                args = self.argparserex('COMMA')
                self.eat('RPAREN')
                keyval = {}
                while self.c_t.type == 'VID':
                    t = self.c_t
                    self.advance()
                    self.eat('LPAREN')
                    exp = self.expr()
                    self.eat('RPAREN')
                    keyval.update({t.value: exp})
                keyval.update({'$': args})
                return FuncCallExp(temp, keyval, typecall='PFID')
            self.advance()
            self.eat('LPAREN')
            arg = self.argparserex('COMMA')
            self.eat('RPAREN')
            return FuncCallExp(temp, arg, typecall='FID')
        elif temp.type == 'PFID':
            self.advance()
            self.eat('LPAREN')
            args = self.argparserex('COMMA')
            self.eat('RPAREN')
            keyval = {}
            while self.c_t.type == 'VID':
                t = self.c_t
                self.advance()
                self.eat('LPAREN')
                exp = self.expr()
                self.eat('RPAREN')
                keyval.update({t.value: exp})
            keyval.update({'$': args})
            return FuncCallExp(temp, keyval, typecall='PFID')
        elif temp.type == 'GLOBAL_VID':
            self.advance()
            chain = [VarExp(temp)]
            while self.c_t.type == 'POINT':
                self.advance()
                if self.c_t.type == 'VID':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'INTEGER_CONST':
                    chain.append(DotVarAccess(self.c_t))
                    self.advance()
                elif self.c_t.type == 'END':
                    chain.append(EndExpression())
                    self.advance()
                elif self.c_t.type == 'REPLACE':
                    self.advance()
                    self.eat('LPAREN')
                    e = self.expr()
                    self.eat('RPAREN')
                    self.eat('WITH')
                    self.eat('LPAREN')
                    w = self.expr()
                    self.eat('RPAREN')
                    chain.append(AssignReplaceExp(None, e, w))
                elif self.c_t.type == 'LANGUAGES':
                    chain.append(LangAccessExp(None, self.c_t))
                    self.advance()
                elif self.c_t.type == 'MIX':
                    self.advance()
                    chain.append(MixExpression())
                elif self.c_t.type == 'LENGTH':
                    chain.append(LengthExpression())
                    self.advance()
                elif self.c_t.type == 'FIND':
                    self.advance()
                    self.eat('LPAREN')
                    _what = self.expr()
                    self.eat('RPAREN')
                    _from = None
                    _to = None
                    if self.c_t.type == 'FROM':
                        self.advance()
                        self.eat('LPAREN')
                        _from = self.expr()
                        self.eat('RPAREN')
                    if _from and self.c_t.type == 'TO':
                        self.advance()
                        self.eat('LPAREN')
                        _to = self.expr()
                        self.eat('RPAREN')
                    chain.append(FindExpression(_what, _from, _to))
                elif self.c_t.type == 'GET':
                    self.advance()
                    self.eat('LPAREN')
                    _from = _to = None
                    if self.c_t.type == 'INTEGER_CONST':
                        _from = self.eat('INTEGER_CONST')
                    elif self.c_t.type == 'STRING_CONST1':
                        _from = self.eat('STRING_CONST1')
                    elif self.c_t.type == 'STRING_CONST2':
                        _from = self.eat('STRING_CONST2')
                    self.eat('MINUS')
                    if self.c_t.type == 'INTEGER_CONST':
                        _to = self.eat('INTEGER_CONST')
                    elif self.c_t.type == 'STRING_CONST1':
                        _to = self.eat('STRING_CONST1')
                    elif self.c_t.type == 'STRING_CONST2':
                        _to = self.eat('STRING_CONST2')
                    self.eat('RPAREN')
                    limit = None
                    if _from and _to:
                        if self.c_t.type == 'LIMITS':
                            self.advance()
                            self.eat('LPAREN')
                            limit = self.expr()
                            self.eat('RPAREN')
                    chain.append(GetExpression(_from, _to, limit))
                if self.c_t.type == 'LPAREN':
                    self.advance()
                    if self.tokens[self.counter + 1].type == 'MINUS':
                        _from = _to = None
                        if self.c_t.type == 'INTEGER_CONST':
                            _from = self.eat('INTEGER_CONST')
                        elif self.c_t.type == 'STRING_CONST1':
                            _from = self.eat('STRING_CONST1')
                        elif self.c_t.type == 'STRING_CONST2':
                            _from = self.eat('STRING_CONST2')
                        self.eat('MINUS')
                        if self.c_t.type == 'INTEGER_CONST':
                            _to = self.eat('INTEGER_CONST')
                        elif self.c_t.type == 'STRING_CONST1':
                            _to = self.eat('STRING_CONST1')
                        elif self.c_t.type == 'STRING_CONST2':
                            _to = self.eat('STRING_CONST2')
                        self.eat('RPAREN')
                        limit = None
                        if (_from and _to) or _to:
                            if _from.type in ['STRING_CONST1', 'STRING_CONST2']:
                                if self.c_t.type == 'LIMITS':
                                    self.advance()
                                    self.eat('LPAREN')
                                    limit = self.expr()
                                    self.eat('RPAREN')
                        chain.append(GetExpression(_from, _to, limit))
                    else:
                        e = self.expr()
                        self.eat('RPAREN')
                        chain.append(CombinationalExp(None, e))
            return ChainExpression(chain)
        elif temp.type == 'TYPE':
            self.advance()
            self.eat('LPAREN')
            e = self.expr()
            self.eat('RPAREN')
            return TypeExp(e)
        else:
            pass
    #this function scan deliminated expression
    def argparser(self, sep='COMMA', outer=False):
        args = {}
        while self.c_t.type == 'VID':
            temp = self.c_t
            self.advance()
            self.eat('ATTR')
            args.update({temp.value: self.expr()})
            if self.c_t.type == sep:
                self.eat(sep)
        return args
    #this function is use to scan function argument such as argument with default values
    def args(self, sep='COMMA'):
        arguments = {}
        while self.c_t.type == 'VID':
            temp = self.c_t
            for a in arguments:
                if temp.value in a:
                    raise RuntimeError("from {} duplicate args {} at line:{} col:{}"
                                       .format(temp.file, temp.value, temp.line, temp.col))
            self.advance()
            if self.c_t.type == 'ATTR':
                self.advance()
                arguments.update({temp.value: self.expr()})
                if self.c_t.type == sep: self.eat(sep)
            else:
                arguments.update({temp.value: NumberExp(Token(0, 'INTEGER_CONST', temp.line, temp.col, temp.file))})
                if self.c_t.type == sep: self.eat(sep)
        return arguments
    #this function use to scan print argument
    def argparserex(self, sep='COMMA'):
        list = []
        while self.c_t.type == 'VID' or self.c_t.type == 'INTEGER_CONST' or \
                self.c_t.type == 'FLOAT_CONST' or self.c_t.type == 'STRING_CONST1' or \
                self.c_t.type == 'STRING_CONST2' or self.c_t.type == 'CLINE' or self.c_t.type == 'CSPACE' \
                or self.c_t.type == 'FID' or self.c_t.type == 'GLOBAL_VID' or self.c_t.type == 'TYPE' \
                or self.c_t.type == 'LPAREN':
            if self.c_t.value in self.glob.py_functions:
                self.c_t.type = 'PFID'
            list.append(self.expr())
            if self.c_t.type == sep:
                self.eat(sep)
        return list


###############################
###############################
######### Interpreter #########
###############################
###############################
class Global:
    def __init__(self):
        self.global_statement = None
        self.py_functions = {}
        self.functions = {}
        self.global_symbol_table = None


class Interpreter:
    def __init__(self, tree, glob):
        self.tree = tree
        self.symbol_table = None
        self.loopstack = []
        self.glob = glob
        self.log = False
        self.stack = []
        self.print_data = ""
    #this is default visit method which deside which method is to be execute based on expression class name
    def visit(self, node, symbol_table=None):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, symbol_table)
    #this visit evaluate BinOp
    def visit_BinOp(self, node, symbol_table):
        left = self.visit(node.left, symbol_table)
        right = self.visit(node.right, symbol_table)
        result = None
        if node.op.value == '*':
            result = left * right
        elif node.op.value == '/':
            result = left / right
        elif node.op.value == '+':
            result = left + right
        elif node.op.value == '-':
            result = left - right
        elif node.op.value == '<':
            result = left < right
        elif node.op.value == '>':
            result = left > right
        elif node.op.value == '<=':
            result = left <= right
        elif node.op.value == '>=':
            result = left >= right
        elif node.op.value == '==':
            result = left == right
        elif node.op.value == '!=':
            result = left != right
        elif node.op.value == 'And':
            result = left & right
        elif node.op.value == 'Or':
            result = left | right
        elif node.op.value == '&':
            result = Value(str(left) + str(right))
        return result
    #this visit evaluate UnaryExp
    def visit_UnaryExp(self, node, symbol_table):
        num = self.visit(node.fact)
        return num * Value(-1)
        # print('Unary visited:',num)
    #this visit evaluate NumberExp
    def visit_NumberExp(self, node, symbol_table):
        if node.tok.type == 'INTEGER_CONST':
            return Value(int(node.tok.value))
        elif node.tok.type == 'FLOAT_CONST':
            return Value(float(node.tok.value))
        return Value(0)
    #this visit evaluate  VarAssignExp
    def visit_VarAssignExp(self, node, symbol_table):
        if len(node.name) > 0 and len(node.name) < 2:
            symbol_table.set(node.name[0].value, self.visit(node.exp, symbol_table))
        else:
            name = copy.copy(node.name)
            stackval = symbol_table.get(name[0].value)
            del name[0]
            last = name[len(name) - 1].value
            del name[len(name) - 1]
            for i in name:
                if type(stackval).__name__ == 'Dictionary':
                    stackval = stackval.get(i.value)
                if type(stackval).__name__ == 'ArrayList':
                    stackval = stackval[i]
            if type(stackval).__name__ == 'Value':
                stackval.value = self.visit(node.exp, symbol_table).value
            elif type(stackval).__name__ == 'Dictionary':
                stackval.data.update({last: self.visit(node.exp, symbol_table)})
            elif type(stackval).__name__ == 'ArrayList':
                stackval.items[last - 1] = self.visit(node.exp, symbol_table)
        if self.log:
            # print('Log/visitVarAssignExp:\n\t',valname,"=",symbol_table.get(valname),'\n\t__Symbol__Table__\n\t',symbol_table.symbols)
            pass
    #this visit evaluate MultiVarAssignExp
    def visit_MultiVarAssignExp(self, node, symbol_table):
        for i in node.listexp:
            self.visit(i, symbol_table)
    #this visit evaluate CompoundStatement
    def visit_CompoundStatement(self, node, symbol_table):
        while node.havenext():
            val = self.visit(node.next(), symbol_table)
            if val:
                return val
    #this visit evaluate method
    def no_visit_method(self, node, symbol_table):
        raise Exception(f"No visit_{type(node).__name__} method defined")
    #this visit evaluate IfStatement
    def visit_IfStatement(self, node, symbol_table):
        s_table = SymbolTable('If', symbol_table)
        elseifexecuted = False
        if self.visit(node.condition, symbol_table).value != False:
            for v in node.ifbody.statements:
                val = self.visit(v, s_table)
                if val:
                    return val
        elif len(node.elseifbodies) > 0:
            for i in node.elseifbodies:
                if self.visit(i['condition'], symbol_table).value != False:
                    val = self.visit(i['body'], s_table)
                    elseifexecuted = True
                    if val:
                        return val
                    break
        if node.elsebody is not None and not elseifexecuted:
            elseifexecuted = False
            for i in node.elsebody.statements:
                val = self.visit(i, s_table)
                if val:
                    return val
        return None
    #this visit evaluate VarExp
    def visit_VarExp(self, node, symbol_table):
        if self.log:
            print('Log/visit_VarExp:\n\t', node.tok.value, '=', symbol_table.get(node.tok.value))
        val = symbol_table.get(node.tok.value)
        if val:
            return val
        else:
            raise RuntimeError('Undefined variable "{}" at line:{} col:{} in {} from {}'
                               .format(node.tok.value, node.tok.line, node.tok.col, node.tok.file, symbol_table.name))
    #this visit evaluate ReturnStatement
    def visit_ReturnStatement(self, node, symbol_table):
        return self.visit(node.exp, symbol_table)
    #this visit evaluate TupleExp
    def visit_TupleExp(self, node, symbol_table):
        details = {}
        for i in node.args:
            details.update({i: self.visit(node.args[i], symbol_table)})
        return Dictionary(details)
    #this visit evaluate ListExp
    def visit_ListExp(self, node, symbol_table):
        value = self.visit(node.data, symbol_table)
        for i in value.data:
            symbol_table.set(i, value.data[i])
   #this visit evaluate StringExp
    def visit_StringExp(self, node, symbol_table):  # e
        return Value(node.tok.value)
   #this visit evaluate PrintStatement
    def visit_PrintStatement(self, node, symbol_table):
        for i in node.args:
            # print(self.visit(i, symbol_table), end='')
            self.print_data += str(self.visit(i, symbol_table))
   #this visit evaluate SpaceExp
    def visit_SpaceExp(self, node, symbol_table):
        if node.exp is not None:
            n = self.visit(node.exp, symbol_table)
            data = ""
            for i in range(n.value):
                data += " "
            return Value(data)
        else:
            return Value(" ")
   #this visit evaluate LineExp
    def visit_LineExp(self, node, symbol_table):
        if node.exp is not None:
            n = self.visit(node.exp, symbol_table)
            data = ""
            for i in range(n.value):
                data += "<br>"
            return Value(data)
        else:
            return Value("<br>")
   #this visit evaluate Statements
    def visit_Statements(self, node, symbol_table):
        while node.havenext():  # e
            val = self.visit(node.next(), symbol_table)  # e
            if type(val).__name__ == 'ArrayList':
                if len(val.items) == 2:
                    if val.items[0].value == 'EVALVAL$$$$$$':
                        self.print_data += str(val.items[1])
   #this visit evaluate IdExp
    def visit_IdExp(self, node, symbol_table):
        value = self.visit(node.exp, symbol_table)
        self.glob.global_symbol_table.set(value.value, Value(self.glob.global_statement.getjump()))
   #this visit evaluate JumpExp
    def visit_JumpExp(self, node, symbol_table):
        tojump = self.visit(node.idexp, symbol_table).value
        v = self.glob.global_symbol_table.get(tojump).value
        condition = node.conditionexp
        times = None if node.timeexp is None else self.visit(node.timeexp, symbol_table).value
        if condition is not None and times is not None:
            while times > node.counter and self.visit(condition, symbol_table).value == True:
                for i in range(v, self.glob.global_statement.getjump() - 1):
                    # print(global_statement.statements[i])
                    self.visit(self.glob.global_statement.statements[i], symbol_table)
                node.counter += 1
            node.counter = 0
        elif condition is not None:
            while self.visit(condition, symbol_table).value == True:
                for i in range(v, self.glob.global_statement.getjump() - 1):
                    self.visit(self.glob.global_statement.statements[i], symbol_table)
        elif times is not None:
            while times > node.counter:
                for i in range(v, self.glob.global_statement.getjump() - 1):
                    self.visit(self.glob.global_statement.statements[i], symbol_table)
                node.counter += 1
            node.counter = 0
        elif times is None and condition is None:
            while True:
                for i in range(v, self.glob.global_statement.getjump() - 1):
                    self.visit(self.glob.global_statement.statements[i], symbol_table)
   #this visit evaluate GlobalExp
    def visit_GlobalExp(self, node, symbol_table):
        for i in range(len(node.vars)):
            self.glob.global_symbol_table.parent.set(node.vars[i].value, self.visit(node.exp[i]))
   #this visit evaluate LoopStatement
    def visit_LoopStatement(self, node, symbol_table):
        stm = SymbolTable('LOOP', symbol_table)
        var = node.var.value
        if node.condition is not None and node.times is not None:
            value = symbol_table.get(var)
            if type(value).__name__ == 'Value':
                i = 0
                while i < self.visit(node.times, stm).value and self.visit(node.condition, stm).value == True:
                    i += 1
                    for j in node.body.statements:
                        stm.set('key', Value(var))
                        stm.set('value', symbol_table.get(var))
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'Dictionary':
                keys = list(value.data.keys())
                i = 0
                k = 0
                while i < self.visit(node.times, stm).value and self.visit(node.condition, stm).value == True:
                    i += 1
                    if k == len(keys): k = 0
                    key = keys[k]
                    k += 1
                    for j in node.body.statements:
                        stm.set('key', Value(key))
                        stm.set('value', value.data[key])
                        keys = list(symbol_table.get(var).data.keys)
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'ArrayList':
                i = 0
                k = 0
                while i < self.visit(node.times, stm).value and self.visit(node.condition, stm).value == True:
                    i += 1
                    if k == len(value.items): k = 0
                    k += 1
                    stm.set('key', Value('#'))
                    for j in node.body.statements:
                        stm.set('value', value.items[k - 1])
                        value = symbol_table.get(var)
                        val = self.visit(j, stm)
                        if val:
                            return val
        elif node.condition is not None:
            value = symbol_table.get(var)
            if type(value).__name__ == 'Value':
                while self.visit(node.condition, stm).value == True:
                    for j in node.body.statements:
                        value = symbol_table.get(var)
                        stm.set('key', Value(var))
                        stm.set('value', value)
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'Dictionary':
                keys = list(value.data.keys())
                k = 0
                while self.visit(node.condition, stm).value == True:
                    if k == len(keys): k = 0
                    key = keys[k]
                    k += 1
                    stm.set('key', Value(key))
                    stm.set('value', value.data[key])
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'ArrayList':
                k = 0
                while self.visit(node.condition, stm).value == True:
                    if k == len(value.items): k = 0
                    k += 1
                    stm.set('key', Value('#'))
                    stm.set('value', value.items[k - 1])
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
        elif node.times is not None:
            value = symbol_table.get(var)
            if type(value).__name__ == 'Value':
                stm.set('key', Value(var))
                stm.set('value', value)
                i = 0
                while i < self.visit(node.times, stm).value:
                    i += 1
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'Dictionary':
                keys = list(value.data.keys())
                i = 0
                k = 0
                while i < self.visit(node.times, stm).value:
                    i += 1
                    if k == len(keys): k = 0
                    key = keys[k]
                    k += 1
                    stm.set('key', Value(key))
                    stm.set('value', value.data[key])
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'ArrayList':
                i = 0
                k = 0
                while i < self.visit(node.times, stm).value:
                    i += 1
                    if k == len(value.items): k = 0
                    k += 1
                    stm.set('key', Value('#'))
                    stm.set('value', value.items[k - 1])
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
        elif node.condition is None and node.times is None:
            value = symbol_table.get(var)
            if type(value).__name__ == 'Value':
                stm.set('key', Value(var))
                stm.set('value', value)
                for i in node.body.statements:
                    val = self.visit(i, stm)
                    if val:
                        return val
            elif type(value).__name__ == 'Dictionary':
                for i in list(value.data.keys()):
                    stm.set('key', Value(i))
                    stm.set('value', value.data[i])
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
            elif type(value).__name__ == 'ArrayList':
                for i in value.items:
                    stm.set('key', Value(value.items.index(i) + 1))
                    stm.set('value', i)
                    for j in node.body.statements:
                        val = self.visit(j, stm)
                        if val:
                            return val
        # print("Aesop")
   #this visit evaluate FuncExp
    def visit_FuncExp(self, node, symbol_table):
        f = Function(node.name, node.args, node.body)
        self.glob.global_symbol_table.parent.set(node.name.value, f)
   #this visit evaluate PyFuncExp
    def visit_PyFuncExp(self, node, symbol_table):
        f = Function(node.name, node.args, None)
        self.glob.global_symbol_table.parent.set(node.name.value, f)
   #this visit evaluate FuncCallExp
    def visit_FuncCallExp(self, node, symbol_table):
        if node.typecall == 'FID':
            stm = SymbolTable(node.name.value, symbol_table)
            func = self.glob.global_symbol_table.get(node.name.value)
            if not func:
                raise RuntimeError('Function not found:{} at line:{} col:{} in file:{}'
                                   .format(node.name.value, node.name.line, node.name.col, node.name.file))
            if len(func.args) < len(node.args):
                raise RuntimeError("Too many argument supplied function:{} at line:{} col:{} in file:{}"
                                   .format(func.name.value, node.name.line, node.name.col, node.name.file))
            evaluated = []
            for i in func.args:
                evaluated.append(self.visit(func.args[i], symbol_table))
            i = 0
            newevaluated = []
            for j in node.args:  # e
                newevaluated.append(self.visit(j, symbol_table))  # e
            for j in newevaluated:  # e
                evaluated[i] = j
                i += 1
            i = 0
            for j in func.args:  # e
                stm.symbols.update({j: evaluated[i]})
                i += 1
            for i in func.body.statements:  # e
                val = self.visit(i, stm)
                if val:
                    return val
        elif node.typecall == 'PFID':
            stm = SymbolTable(node.name.value, symbol_table)
            args = copy.copy(node.args)
            all = args.pop('$')
            f = self.glob.global_symbol_table.get(node.name.value)
            if len(f.args) < len(all) or len(f.args) < len(args):
                raise RuntimeError('Too many argument supplied function:{} line:{} col:{} in {}'
                                   .format(node.name.value, node.name.line, node.name.col, node.name.file))
            evaluated = {}
            for i in f.args:
                evaluated.update({i: self.visit(f.args[i], symbol_table)})
            k = 0
            keys = list(evaluated.keys())
            for i in all:
                evaluated.update({keys[k]: self.visit(i, symbol_table)})
                k += 1
            for i in args:
                evaluated.update({i: self.visit(args[i], symbol_table)})
            argument_pass_str = ""
            for i in evaluated:
                argument_pass_str += i + "="
                if type(evaluated[i].value).__name__ == 'str':
                    argument_pass_str += '"' + evaluated[i].value + '",'
                else:
                    argument_pass_str += str(evaluated[i].value) + ","
            argument_pass_str = argument_pass_str[:len(argument_pass_str) - 1]
            pyzf = "py_cmd." + f.name.value + "(" + argument_pass_str + ")"
            val = eval(pyzf)
            if val != None:
                return Value(val)
   #this visit evaluate SelfReplaceExp
    def visit_SelfReplaceExp(self, node, symbol_table):
        if len(node.var) == 1:
            data = symbol_table.get(node.var[0].value)
            data.replaceself(self.visit(node.toreplace, symbol_table), self.visit(node.withreplace, symbol_table))
        else:
            stackval = symbol_table.get(node.var[0].value)
            del node.var[0]
            last = node.var[len(node.var) - 1]
            del node.var[len(node.var) - 1]
            for i in node.var:
                if type(stackval).__name__ == 'Dictionary':
                    stackval = stackval.get(i.value)
            if type(stackval).__name__ == 'Value':
                stackval.replaceself(self.visit(node.toreplace, symbol_table),
                                     self.visit(node.withreplace, symbol_table))
            elif type(stackval).__name__ == 'Dictionary':
                val = stackval.data[last.value]
                val.replaceself(self.visit(node.toreplace, symbol_table), self.visit(node.withreplace, symbol_table))
                stackval.data.update({last.value: val})
   #this visit evaluate AssignReplaceExp
    def visit_AssignReplaceExp(self, node, symbol_table):
        return self.stack[len(self.stack) - 1].replacenew(self.visit(node.toreplace, symbol_table),
                                                          self.visit(node.withreplace, symbol_table))
   #this visit evaluate DictExp
    def visit_DictExp(self, node, symbol_table):
        template = code
        data = {}
        selfvalue = self.visit(node.exp, self.glob.global_symbol_table)  # e
        data.update({'$': selfvalue})  # e
        data.update({'self':selfvalue})
        template = addmore(template, 'self', selfvalue.value)  # e
        self.glob.global_symbol_table.parent.set(node.var.value, Dictionary(data))
        for i in node.table:
            val = self.visit(node.table[i])
            template = addmore(template, i.value, val.value if type(val).__name__ == 'Value' else (
                val.data if type(val).__name__ == 'Dictionary' else val.items))
            data.update({i.value: val})
        exec(template)
        py_cmd.__globals__.update({node.var.value: eval('Data()')})
   #this visit evaluate CombinationalExp
    def visit_CombinationalExp(self, node, symbol_table):
        strval = self.visit(node.exp, symbol_table).value
        dic = self.stack[len(self.stack) - 1].data
        for k in dic:
            strval = strval.replace('{}{}{}'
                                    .format('{', k, '}'), str(dic[k].value))
        return Value(strval)
   #this visit evaluate PythonCodeExp
    def visit_PythonCodeExp(self, node, symbol_table):
        exec(node.code, py_cmd.__globals__)
   #this visit evaluate ArrayExp
    def visit_ArrayExp(self, node, symbol_table):
        data = ArrayList()
        data.items.clear()
        for i in node.items:
            data.items.append(self.visit(i, symbol_table))
        return data
   #this visit evaluate KillVarExp
    def visit_KillVarExp(self, node, symbol_table):
        symbol_table.remove(node.var.value)
   #this visit evaluate TypeExp
    def visit_TypeExp(self, node, symbol_table):
        value = self.visit(node.exp, symbol_table)
        if type(value).__name__ == 'Value':
            if type(value.value).__name__ == 'str':
                return Value("String")
            elif type(value.value).__name__ == 'int':
                return Value("Integer")
            elif type(value.value).__name__ == 'float':
                return Value('Float')
        elif type(value).__name__ == 'ArrayList':
            return Value("Array")
        elif type(value).__name__ == 'Dictionary':
            return Value('Dictionary')
   #this visit evaluate AssignByIndex
    def visit_AssignByIndex(self, node, symbol_table):
        if self.log:
            print('Log/visit_AssignByIndex:\n\t', node.var.value, '=', symbol_table.get(node.var.value))
        returned = symbol_table.get(node.var.value)
        if self.log:
            print("Log/visit_AssignByIndex:\n\t", node.var.value, ' Is type of', type(returned))
        if type(returned).__name__ == 'ArrayList':
            returned.items[int(node.index.value) - 1] = self.visit(node.exp)
        elif type(returned).__name__ == 'Value':
            if type(returned.value).__name__ == 'str':
                returned.value[int(node.index.value) - 1] = self.visit(node.exp)
            else:
                raise RuntimeError('from {} "{}" of type({}) is not subscriptable at line:{} col:{}'
                                   .format(node.var.file, node.var.value, type(returned.value), node.var.line,
                                           node.var.col))
   #this visit evaluate LangAccessExp
    def visit_LangAccessExp(self, node, symbol_table):
        l = Lexer()
        f = l.tokenize('lang.' + node.lang.value + '.q', open('lang.' + node.lang.value + '.q').read(), 1, [])
        i = 0
        dicc = {}
        for i in range(0, len(f)):
            if f[i].type in ['STRING_CONST1', 'STRING_CONST2']:
                orig = f[i].value
                i += 1
                if f[i].type == 'ATTR':
                    i += 1
                    if f[i].type in ['STRING_CONST1', 'STRING_CONST2']:
                        tval = Value(f[i].value)
                        i += 1
                        if f[i].type == 'PCOMMA':
                            i += 1
                            dicc.update({orig: tval})
        val = dicc.get(self.stack[len(self.stack) - 1].value, None)
        if val:
            return val
        return self.stack[len(self.stack) - 1]
   #this visit evaluate ChainExpression
    def visit_ChainExpression(self, node, symbol_table):  # e
        if len(node.chain) == 1:  # e
            return self.visit(node.chain[0], symbol_table)  # e
        else:
            for i in node.chain:
                self.stack.append(self.visit(i, symbol_table))
            val = self.stack[len(self.stack) - 1]
            for i in node.chain:
                self.stack.pop()
            return val
   #this visit evaluate DotVarAccess
    def visit_DotVarAccess(self, node, symbol_table):
        if type(self.stack[len(self.stack) - 1]).__name__ == 'Dictionary':
            return self.stack[len(self.stack) - 1].data[node.tok.value]  # e
        elif type(self.stack[len(self.stack) - 1]).__name__ == 'ArrayList':
            return self.stack[len(self.stack) - 1].items[int(node.tok.value) - 1]
        elif type(self.stack[len(self.stack) - 1]).__name__ == 'Value':
            if type(self.stack[len(self.stack) - 1].value).__name__ == 'str':
                return self.stack[len(self.stack) - 1].value[int(node.tok.value) - 1]
   #this visit evaluate DotAddExpression
    def visit_DotAddExpression(self, node, symbol_table):
        if len(node.chain) == 1:
            val = symbol_table.get(node.chain[0].value)
            if type(val).__name__ == 'ArrayList':
                val.items.append(self.visit(node.exp, symbol_table))
            elif type(val).__name__ == 'Value':
                if type(val.value).__name__ == 'str':
                    val.value += self.visit(node.exp, symbol_table).value
        else:
            stackval = symbol_table.get(node.chain[0].value)
            del node.chain[0]
            last = node.chain[len(node.chain) - 1]
            del node.chain[len(node.chain) - 1]
            for i in node.chain:
                if type(stackval).__name__ == 'Dictionary':
                    stackval = stackval.get(i.value)
            if type(stackval).__name__ == 'Value':
                stackval.value += self.visit(node.exp, symbol_table).value
            elif type(stackval).__name__ == 'Dictionary':
                val = stackval.data[last.value]
                val.value += self.visit(node.exp, symbol_table).value
                stackval.data.update({last.value: val})
   #this visit evaluate EndExpression
    def visit_EndExpression(self, node, symbol_table):
        if type(self.stack[len(self.stack) - 1]).__name__ == 'ArrayList':
            return self.stack[len(self.stack) - 1].items[len(self.stack[len(self.stack) - 1].items) - 1]
        elif type(self.stack[len(self.stack) - 1]).__name__ == 'Value':
            if type(self.stack[len(self.stack) - 1].value).__name__ == 'str':
                return Value(self.stack[len(self.stack) - 1].value[len(self.stack[len(self.stack) - 1].value) - 1])
   #this visit evaluate SplitExp
    def visit_SplitExp(self, node, symbol_table):
        if type(self.stack[len(self.stack) - 1]).__name__ == 'Value':
            return ArrayList(self.stack[len(self.stack) - 1].value.split(self.visit(node.exp, symbol_table).value))
   #this visit evaluate AddExpression
    def visit_AddExpression(self, node, symbol_table):
        if len(node.chain) == 1:
            val = symbol_table.get(node.chain[0].value)
            if type(val).__name__ == 'ArrayList':
                if node.at:
                    val.items.insert(self.visit(node.at, symbol_table).value, self.visit(node.exp, symbol_table))
                else:
                    val.items.append(self.visit(node.exp, symbol_table))
            elif type(val).__name__ == 'Value':
                if type(val.value).__name__ == 'str':
                    if node.at:
                        i = self.visit(node.at, symbol_table).value
                        if i == 0:
                            val.value = self.visit(node.exp, symbol_table).value + val.value
                        elif i == len(val.value):
                            val.value += self.visit(node.exp, symbol_table).value
                        else:
                            first = val.value[:self.visit(node.at).value]
                            second = val.value[self.visit(node.at).value:]
                            val.value = first + self.visit(node.exp).value + second
                    else:
                        val.value += self.visit(node.exp, symbol_table).value
                elif type(val).__name__ == 'Dictionary':
                    val.data.update({self.visit(node.at).value: self.visit(node.exp, symbol_table)})
        else:
            stackval = symbol_table.get(node.chain[0].value)
            del node.chain[0]
            last = node.chain[len(node.chain) - 1]
            del node.chain[len(node.chain) - 1]
            for i in node.chain:
                if type(stackval).__name__ == 'Dictionary':
                    stackval = stackval.get(i.value)
            if type(stackval).__name__ == 'Value':
                if type(stackval.value).__name__ == 'str':
                    if node.at:
                        i = self.visit(node.at, symbol_table).value
                        if i == 0:
                            stackval.value = self.visit(node.exp, symbol_table).value + stackval.value
                        elif i == len(stackval.value):
                            stackval.value += self.visit(node.exp, symbol_table).value
                        else:
                            first = stackval.value[:self.visit(node.at).value]
                            second = stackval.value[self.visit(node.at).value:]
                            stackval.value = first + self.visit(node.exp).value + second
                    else:
                        stackval.value += self.visit(node.exp, symbol_table).value
            elif type(stackval).__name__ == 'Dictionary':
                val = stackval.data[last.value]
                if type(val).__name__ == 'ArrayList':
                    if node.at:
                        val.items.insert(self.visit(node.at, symbol_table).value, self.visit(node.exp, symbol_table))
                    else:
                        val.items.append(self.visit(node.exp, symbol_table))
                elif type(val).__name__ == 'Value':
                    if node.at:
                        i = self.visit(node.at, symbol_table).value
                        if i == 0:
                            val.value = self.visit(node.exp, symbol_table).value + val.value
                        elif i == len(val.value):
                            val.value += self.visit(node.exp, symbol_table).value
                        else:
                            first = val.value[:self.visit(node.at).value]
                            second = val.value[self.visit(node.at).value:]
                            val.value = first + self.visit(node.exp).value + second
                    else:
                        val.value = val.value + self.visit(node.exp, symbol_table).value
                elif type(val).__name__ == 'Dictionary':
                    val.data.update({last.value: self.visit(node.exp, symbol_table)})
   #this visit evaluate LengthExpression
    def visit_LengthExpression(self, node, symbol_table):
        val = self.stack[len(self.stack) - 1]
        if type(val).__name__ == 'Dictionary':
            return Value(len(val.data.keys()))
        elif type(val).__name__ == 'Value':
            return Value(len(val.value))
        elif type(val).__name__ == 'ArrayList':
            return Value(len(val.items))
   #this visit evaluate DeleteExperssion
    def visit_DeleteExperssion(self, node, symbol_table):
        if len(node.chain) == 1:
            val = symbol_table.get(node.chain[0].value)
            if type(val).__name__ == 'ArrayList':
                val.items.pop(self.visit(node.exp, symbol_table).value)
        else:
            stackval = symbol_table.get(node.chain[0].value)
            del node.chain[0]
            last = node.chain[len(node.chain) - 1]
            del node.chain[len(node.chain) - 1]
            for i in node.chain:
                if type(stackval).__name__ == 'Dictionary':
                    stackval = stackval.get(i.value)
            if type(stackval).__name__ == 'Dictionary':
                val = stackval.data[last.value]
                if type(val).__name__ == 'ArrayList':
                    val.items.pop(self.visit(node.exp, symbol_table).value - 1)
                elif type(val).__name__ == 'Dictionary':
                    val.data.pop(self.visit(node.exp, symbol_table).value)
   #this visit evaluate FindExpression
    def visit_FindExpression(self, node, symbol_table):
        val = self.stack[len(self.stack) - 1]
        tofind = self.visit(node._what)
        if type(val).__name__ == 'Dictionary':
            for i in val.data:
                if type(tofind).__name__ == 'Value':
                    if tofind == val.data[i]:
                        return Value(i)
                elif type(tofind).__name__ == 'Dictionary':
                    if tofind.data == val.data[i]:
                        return Value(i)
                elif type(tofind).__name__ == 'ArrayList':
                    if tofind.items == val.data[i]:
                        return Value(i)
        elif type(val).__name__ == 'Value':
            if type(val.value).__name__ == 'str' and node._from == None and node._to == None:
                try:
                  return Value(val.value.index(tofind.value) + 1)
                except ValueError:
                    return Value(0)
            elif type(val.value).__name__ == 'str' and node._from and node._to == None:
                try:
                    return Value(val.value.index(tofind.value, self.visit(node._from).value - 1) + 1)
                except ValueError:
                    return Value(0)
            elif type(val.value).__name__ == 'str' and node._from and node._to:
                try:
                    return Value(
                        val.value.index(tofind.value, self.visit(node._from).value - 1, self.visit(node._to).value - 1) + 1)
                except ValueError:
                    return Value(0)
        elif type(val).__name__ == 'ArrayList':
            return self.findout(val, tofind, node)
   #this visit evaluate findout
    def findout(self, val, tofind, node):
        if node._from == None and node._to == None:
            if type(tofind).__name__ == 'Value':
                return Value(val.items.index(tofind.value) + 1)
            elif type(tofind).__name__ == 'Dictionary':
                return Value(val.items.index(tofind.data) + 1)
            elif type(tofind).__name__ == 'ArrayList':
                return Value(val.items.index(tofind.items) + 1)
        elif node._from and node._to == None:
            if type(tofind).__name__ == 'Value':
                return Value(val.items.index(tofind.value, self.visit(node._from).value - 1) + 1)
            elif type(tofind).__name__ == 'Dictionary':
                return Value(val.items.index(tofind.data, self.visit(node._from).value - 1) + 1)
            elif type(tofind).__name__ == 'ArrayList':
                return Value(val.items.index(tofind.items, self.visit(node._from).value - 1) + 1)
        elif node._from and node._to:
            if type(tofind).__name__ == 'Value':
                return Value(
                    val.items.index(tofind.value, self.visit(node._from).value - 1, self.visit(node._to).value - 1) + 1)
            elif type(tofind).__name__ == 'Dictionary':
                return Value(
                    val.items.index(tofind.data, self.visit(node._from).value - 1, self.visit(node._to).value - 1) + 1)
            elif type(tofind).__name__ == 'ArrayList':
                return Value(
                    val.items.index(tofind.items, self.visit(node._from).value - 1, self.visit(node._to).value - 1) + 1)
        return Value(0)
   #this visit evaluate MixExpression
    def visit_MixExpression(self, node, symbol_table):
        val = self.stack[len(self.stack) - 1]
        if type(val).__name__ == 'Value':
            l = list(val.value)
            random.shuffle(l)
            return Value("".join(l))
        elif type(val).__name__ == 'ArrayList':
            random.shuffle(val.items)
            return val
   #this visit evaluate GetExpression
    def visit_GetExpression(self, node, symbol_table):
        val = self.stack[len(self.stack) - 1]
        if type(val).__name__ != 'Value':
            raise RuntimeError("Error")
        if node._to.type == 'INTEGER_CONST' and node._from.type == 'INTEGER_CONST':
            if node._limit:
                raise RuntimeError("Limit Only supported in both string or int string mode at line:{} col:{} file:{}"
                                   .format(node._to.line, node._to.col + 1, node._to.file))
            return Value(val.value[int(node._from.value) - 1:int(node._to.value)])
        elif node._to.type in ['STRING_CONST1', 'STRING_CONST2'] and node._from.type == 'INTEGER_CONST':
            limit = self.visit(node._limit, symbol_table).value if node._limit else 1
            s = 0
            sub = ""
            partition = ""
            for i in range(int(node._from.value) - 1, len(val.value)):
                partition += val.value[i]
                if s < limit:
                    if val.value[i] == node._to.value:
                        s += 1
                        sub += partition
                        partition = ""
                else:
                    break
            return Value(sub)
        elif node._to.type == 'INTEGER_CONST' and node._from.type in ['STRING_CONST1', 'STRING_CONST2']:
            if node._limit:
                raise RuntimeError("Limit Only supported in both string or int string mode at line:{} col:{} file:{}"
                                   .format(node._to.line, node._to.col + 1, node._to.file))
            value = val.value[val.value.index(node._from.value):int(node._to.value)]
            return Value(value);
        elif node._to.type in ['STRING_CONST1', 'STRING_CONST2'] and node._from.type in ['STRING_CONST1',
                                                                                         'STRING_CONST2']:
            limit = self.visit(node._limit, symbol_table).value if node._limit else 1
            s = 0
            sub = ""
            partition = ""
            for i in range(val.value.index(node._from.value), len(val.value)):
                partition += val.value[i]
                if s < limit:
                    if val.value[i] == node._to.value:
                        s += 1
                        sub += partition
                        partition = ""
                else:
                    break
            return Value(sub)
   #this visit evaluate VarIfExpression
    def visit_VarIfExpression(self, node, symbol_table):
        self.visit(node.ifexp, symbol_table)
   #this visit evaluate relative
    def replace_relative(self, _text='', _toreplace=[], _withreplace=[]):
        if len(_toreplace) != len(_withreplace): raise RuntimeError("length must be equal {} with {} not valid"
                                                                    .format(len(_toreplace), len(_withreplace)))
        for i in range(len(_toreplace)):
            _text = _text.replace(_toreplace[i], _withreplace[i])
        return _text
   #this visit evaluate TimeExpression
    def visit_TimeExpression(self, node, symbol_table):
        val = None
        if len(node.chain) == 1:
            val = symbol_table.get(node.chain[0].value)
        else:
            stackval = symbol_table.get(node.chain[0].value)
            del node.chain[0]
            last = node.chain[len(node.chain) - 1]
            del node.chain[len(node.chain) - 1]
            for i in node.chain:
                if type(stackval).__name__ == 'Dictionary':
                    stackval = stackval.get(i.value)
            if type(stackval).__name__ == 'Dictionary':
                val = stackval.data[last.value]

        _toformat = self.replace_relative(self.visit(node._toformat).value, ["H", "S", "m", "d", "Y", "M"],
                                          ["%H", "%S", "%m", "%d", "%Y", "%M"])
        _format = self.replace_relative(self.visit(node._format).value, ["H", "S", "m", "d", "Y", "M"],
                                        ["%H", "%S", "%m", "%d", "%Y", "%M"])
        time = datetime.datetime.strptime(val.value, _format)
        if node._operate.value == 'minus':
            time = time - datetime.timedelta(days=self.visit(node._howmuch).value)
        else:
            time = time + datetime.timedelta(days=self.visit(node._howmuch).value)
        val.value = str(time.strftime(_toformat))
        val.template=str(time.strftime(_toformat))
   #this visit evaluate NumExpression
    def visit_NumExpression(self,node,symbol_table):
        val=self.stack[len(self.stack)-1]
        format=self.visit(node.tmp,symbol_table)
        if type(val).__name__ == 'Value' and type(format).__name__ == 'Value':
            if type(val.value).__name__ in ['float','int'] and type(format.value).__name__ == 'str':
                if len(str(val.value).split('.')[0]) < len(format.value.split('.')[0]):
                    required_zeros=len(format.value.split('.')[0])-len(str(val.value).split('.')[0])
                    newval=round(val.value,len(format.value.split('.')[1]))
                    str_val=str(newval)
                    for i in range(required_zeros):str_val='0'+str_val
                    return Value(str_val,templated=True)
                else:
                    return Value(round(val.value,len(format.value.split('.')[1])),templated=True)

if __name__ == '__main__':
    import test

    lexer = Lexer()
    global_symbol_table = SymbolTable('module')
    global_symbol_table.set('true', Value(1))
    global_symbol_table.set('false', Value(0))
    segments = test.segments('debug.q')
    print_text = ""
    glob = Global()
    included = False
    for i in segments:
        if i[0] == 'TEXT':
            print_text += i[1]
        else:
            lexer.tokens.clear()
            data = lexer.tokenize('debug.q', i[1], i[2], ['command.q', 'configure.q'] if not included else [])
            included = True
            g = Global()
            g.global_symbol_table = SymbolTable(str(i[2]), global_symbol_table)
            p = Parser(data, glob=glob)
            stmt = p.parse()
            g.global_statement = stmt
            i = Interpreter(stmt, g)
            i.visit(stmt, g.global_symbol_table)
            i.stack.clear()
            print_text += i.print_data
    print(print_text)
    open('index.html', 'w').write(print_text)
# except Exception as ex:
#     print('\n', ex)


# Create your views here.
from . import test
def index(request, path):
    path=os.getcwd()+'/text/'+path
    lexer = Lexer()
    global_symbol_table = SymbolTable('module')
    global_symbol_table.set('true', Value(1))
    global_symbol_table.set('false', Value(0))
    segments = test.segments(path)
    print_text = ""
    glob = Global()
    included = False
    for i in segments:
        if i[0] == 'TEXT':
            print_text += i[1]
        else:
            lexer.tokens.clear()
            data = lexer.tokenize(path, i[1], i[2], ['command.q', 'configure.q'] if not included else [])
            included = True
            g = Global()
            g.global_symbol_table = SymbolTable(str(i[2]), global_symbol_table)
            p = Parser(data, glob=glob)
            stmt = p.parse()
            g.global_statement = stmt
            i = Interpreter(stmt, g)
            i.visit(stmt, g.global_symbol_table)
            i.stack.clear()
            print_text += i.print_data
    return HttpResponse(print_text)