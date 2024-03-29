#/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# generativeDefiner.py : 05jun2021 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2019, Clinton Prentiss Mah
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

"""
method to compile code for a generative semantic procedure and optionally
to display its logic
"""

import sys
import ellyBits
import semanticCommand

_simple = {  # commands with no arguments
    "noop"         : semanticCommand.Gnoop ,
    "pass"         : semanticCommand.Gnoop ,
    "return"       : semanticCommand.Gretn ,
    "fail"         : semanticCommand.Gfail ,
    "left"         : semanticCommand.Gleft ,
    "right"        : semanticCommand.Grght ,
    "blank"        : semanticCommand.Gblnk ,
    "space"        : semanticCommand.Gblnk ,
    "linefeed"     : semanticCommand.Glnfd ,
    "split"        : semanticCommand.Gsplt ,
    "back"         : semanticCommand.Gback ,
    "obtain"       : semanticCommand.Gobtn ,
    "capitalize"   : semanticCommand.Gcapt ,
    "uncapitalize" : semanticCommand.Gucpt ,
    "trace"        : semanticCommand.Gtrce
}

_dir = [ '<' , '>' ] # direction qualifier for some semantic commands

defaultVIEW = 5      # limits on VIEW command, if unspecified

def compileDefinition ( stb , inp ):

    """
    compile definition from input stream into executable generative semantic logic

    arguments:
        stb   - symbol table
        inp   - EllyDefinitionReader for procedure definition

    returns:
        procedure body as a list of commands and data on success, None otherwise
    """

    store = [ ]  # to save procedure body
    backl = [ ]  # back link stack for conditional branching

    ######## special method for error reporting

    def _err ( s='malformed command' , l='' ):

        """
        show an error message
        arguments:
            s  - message string
        returns:
            False
        """

        print ( '** generative semantic error:' , s , file=sys.stderr )
        if l != '': print ( '*  AT ' , l , file=sys.stderr )
        return False

    ######## special methods for handling conditional blocks

    def _elseBlock ( ):

        """
        handle an ELSE by closing a block and resolving a previous IF failure branch
        returns:
            True on success, False otherwise
        """

#       print ( "elseBlock" , len(backl) )
        if len(backl) == 0:
            return _err('no IF for ELSE')
        no = backl[-1]            # location of previous conditional branch
        br = store[no]            # save chaining link saved in location
        if br < 0:                # < 0 indicates backward branch saved for WHILE
            return _err('ELSE in WHILE block')
        store.append(semanticCommand.Gskip) # end execution of preceding block
        backl[-1] = len(store)    # update back link stack to next skip destination
        store.append(br)          # place holder for skip destination
        store[no] = len(store)    # previous conditional branch comes here
        return True

    def _ifTest ( negn , rs ):

        """
        add conditional test at start of block according to type of arguments
        arguments:
            negn - any negation of test
            rs   - argument string
        returns:
            True on success, False otherwise
        """

#       print ( "ifTest" , len(backl) , rs )
        if len(rs) == 0:
            return _err('incomplete IF or ELIF or WHILE')

        if rs[0] == '[': # testing semantic feature?
            k = rs.find(']')
            if k < 0 or negn > 0:
                return _err('malformed semantic features: ' + rs)
#           print ( 'features=' , rs[0:k+1] )
            fs = stb.getFeatureSet(rs[1:k].lower(),True)
            if fs == None:
                return _err('bad semantic features')
#           print ( 'bits=' , str(fs[0]) , str(fs[1]) )
            test = ellyBits.join(fs[0],fs[1])
#           print ( 'test=' , test )
            store.extend([ semanticCommand.Gchkf , test ])
        else:            # testing local variable
            ar = _eqsplit(rs)
#           print ( 'ar=' , len(ar) , ar )
            if len(ar) < 2:
                return _err('missing conditional test comparison')
            ls = ar[1].split(', ') # separator must be a comma followed by space!
            store.extend([ semanticCommand.Gchck+negn , ar[0].lower() , ls ])
        return True

    ########

    def _procParse ( line ):

        """
        parse a call to standalone procedure and write out code
        arguments:
            line  - text to parse; it should start with '(' and end with ')'
        returns:
            True on success, False otherwise
        """

        k = line.find(')')     # look for end of procedure name
        if k < 0:
            return _err('procedure definition',line)
        store.extend( [ semanticCommand.Gproc , line[1:k].lower() ] )
        return True

    def _operParse ( line ):

        """
        parse regular semantic operation and arguments and then write out code
        arguments:
            line  - text to parse, should be already stripped
        returns:
            True on success, False otherwise
        """

        negn = 0                    # negation indicator for Gchck and Gchkf operations
        k = line.find(' ')          # check for anything after operation code
        if k < 0:                   # if not, line has no arguments
            op = line.lower()       # extract the operation
            rs = ''                 # rest of string
        else:
            op = line[:k].lower()   # otherwise, line has arguments
            rs = line[k+1:].strip() # rest of string
            if op != semanticCommand.Gappd and rs[0] == '~':
                rs = rs[1:]         # preceding '~' means negation in check
                negn = 1            # remove '~' and set 0,1 numerical flag

#       print ( 'op=' , op , 'rs=' , rs )

        if op in _simple:           # nothing more to do if operation is simple
#           print ( "simple operation" )
            if len(rs) > 0 or negn > 0: return _err(l=line)
            store.append(_simple[op])
            return True             #

        if op == 'merge':
            if len(rs) == 0:
                store.append(semanticCommand.Gmrge)
            else:
                c = rs[0]
                store.append(semanticCommand.Gchng)
                ar = rs[1:].split(c)
                if len(ar) < 2:
                    return _err('incomplete MERGE substitution')
                else:
                    store.extend(ar[:2])
        elif op == 'end':
            if len(backl) == 0:
                return _err('unattached END')
            no = backl.pop()
#           print ( 'END @' , no , store[no] )
            nn = no
            while nn > 0:         # follow back links to identify type of block
                on = nn
                nn = store[nn]
            if nn < 0:            # handling WHILE?
                store.extend([ semanticCommand.Gskip , on-3 ])
            ln = len(store)       # end of block
            while True:
                on = store[no]    # fill in chained back links to resolve branches
                store[no] = ln    # all branches will now go to end of block
                if on <= 0: break
                no = on
#               print ( "back" , no , store[no] )
        elif op == 'else':
            if not _elseBlock(): return False
        elif op == 'elif':
            if len(rs) == 0:
                return _err('no ELIF comparison')
            if not _elseBlock() or not _ifTest(negn,rs):
                return False
            on = backl[-1]
#           print ( "extend back link" )
            backl[-1] = len(store)
            store.append(on)
        elif op == 'while' or op == 'if':
            if len(rs) == 0:
                return _err('no IF comparison')
            wh = (op == 'while')                 # are we dealing with WHILE?
#           print ( 'negation=',negn )
            if not _ifTest(negn,rs): return False
#           print ( "new back link" )
            backl.append(len(store))             # back link to conditional branch destination
            store.append(-1 if wh else 0)        # put in place holder with flag
#           print ( 'code save' )
        elif op == 'break' or op == 'breakif':
            k = len(backl) - 1
            while k >= 0:                        # find first enclosing WHILE block
                no = backl[k]
                while no > 0:                    # follow back links
                    no = store[no]
                if no < 0: break                 # stored -1 marks marks WHILE test
                k -= 1                           # stored  0 marks IF/ELIF, must continue
            else:
                return _err('no enclosing WHILE block')
            if op == 'break':
                store.append(semanticCommand.Gskip)  # put in branch command for BREAK
            else:
                ar = _eqsplit(rs)               # check can be on local variable only
                if len(ar) < 2:
                    return _err('no BREAKIF comparison')
                v = ar[0]                        # variable name
                if v[0] == '~':                  # get any sense of check
                    op = semanticCommand.Gchck   # (note sense of check reverses here)
                    v = v[1:]
                else:
                    op = semanticCommand.Gnchk   #
                store.extend([ op , v , ar[1] ]) # put conditional branch for BREAKIF
            on = len(store)                      # for updating back link
            store.append(backl[k])               # save old back link
            backl[k] = on                        # update back back link for branch

        elif op == 'var' or op == 'variable' or op == 'set':
            if len(rs) == 0:
                return _err(l=line)
            co = semanticCommand.Gset if op == 'set' else semanticCommand.Gvar
            ar = _eqsplit(rs)
            if len(ar) < 2:
                ar.append('')
            else:
                ars = ar[1].split(', ')
                ar[1] = ars[0]
            store.extend([ co , ar[0].lower() , ar[1] ])
        elif op == 'insert':
            ar = _getargs(rs)
            if ar == None:
                return _err(l=line)
            wh = ar.pop(0)
            sc = semanticCommand.Ginsr if wh == '<' else semanticCommand.Ginsn
            store.extend([ sc , ar[0] ])
        elif op == 'peek':
            ar = _getargs(rs)
            if ar == None:
                return _err(l=line)
            wh = ar.pop(0)
            store.extend([ semanticCommand.Gpeek , ar[0] , (wh == '<') ])
        elif op == 'extract':
            ar = _getargs(rs)
            if ar == None:
                return _err(l=line)
            wh = ar.pop(0)
            sc = semanticCommand.Gextr if wh == '<' else semanticCommand.Gextl
            if len(ar) == 1: ar.append('1')
            store.extend([ sc , ar[0] , int(ar[1]) ])
        elif op == 'shift' or op == 'delete':
            if len(rs) == 0:
                return _err(l=line)
            ar = rs.split(' ')
            first = ar[0].lower()
            co = ( semanticCommand.Gshft if op == 'shift'
              else semanticCommand.Gdelt if (first == 'to' or first == 'from')
              else semanticCommand.Gdele )
            if co == semanticCommand.Gdelt:
                strg = ' ' if len(ar) == 1 else ar[1]
                flag = 1 if first == 'to' else -1
                store.extend([ co , strg , flag ])
            else:
                nc = 11111   # bigger than any possible buffer
                if first != '<' and first != '>':
                    try:
                        nc = int(first)
                    except ValueError:
                        return _err(l=line)
                    if len(ar) > 1 and ar[1] == '>': nc = -nc
                elif co == semanticCommand.Gshft and len(ar) > 1:
                    return _err('bad SHIFT arguments')
                elif first == '>':
                    nc = -nc
                store.extend([ co , nc ])
        elif op == 'store':
            if len(rs) == 0:
                return _err(l=line)
            ar = rs.split(' ')
            nd = 0 if len(ar) == 1 else int(ar[1])
            store.extend([ semanticCommand.Gstor , ar[0] , nd ])
        elif op == 'find':
            if len(rs) == 0:
                return _err(l=line)
            ar = rs.split(' ')
            ss = ar.pop(0)
            if len(ar) > 1:
                return _err(l=line)
            elif len(ar) == 0:
                if not ss in ['<' , '>']:
                    df = '<'
                else:
                    df = ss
                    ss = ' '
            else:
                df = ar.pop(0)
                if not df in ['<' , '>']:
                    return _err(l=line)
            store.extend([ semanticCommand.Gfnd , ss , df == '<' ])
        elif op == 'align':
            if len(rs) != 1:
                return _err(l=line)
            sens = False if rs[0] == '>' else True
            store.extend([ semanticCommand.Galgn , sens ])
        elif op == 'pick':
#           print ( 'rs=' , rs )
            if len(rs) == 0:
                return _err(l=line)
            ar = rs.split(' ')
            if len(ar) < 2:
                return _err(l=line)
            chs = ar[1]
#           print ( 'chs=' , chs )
            if chs[0] != '(' or chs[-1] != ')':
                return _err('no PICK options')
            dic = { }
            ch = chs[1:-1].split('#')    # strip off ( )
#           print ( 'ch=' , ch )
            for p in ch:                 # get mappings
#               print ( 'p=' , p )
                if p != '':
                    he = p.split('=')
                    if len(he) == 2:     # should be only one assignment
                        dic[he[0]] = he[1]
#           print ( 'dic=' , dic )
            store.extend([ semanticCommand.Gpick , ar[0].lower() , dic ])
#           print ( 'store=' , store )
        elif op == 'append':
            store.extend([ semanticCommand.Gappd , rs ] )
        elif op == 'unicode':
            if len(rs) < 4 or rs[0] != '\\' or rs[1] != 'x':
                return _err('bad hexadecimal')
            cs = chr(int(rs[2:],16))
            store.extend([ semanticCommand.Gappd , cs ] )
        elif op == 'get' or op == 'put':
            co = semanticCommand.Gget if op == 'get' else semanticCommand.Gput
            av = rs.lower().split(' ')
            if len(av) < 2:
                return _err('missing global variable')
            store.extend([ co , av[0] , av[1] ])
        elif op == 'assign' or op == 'queue' or op == 'unqueue':
            ax = rs.split(' ')                  # separate any extra arguments
            av = ax[0].lower().split('=')       # get variable names
            if len(av) <= 1 or len(av[1]) == 0:
                return _err('incomplete ' + str(av).upper() + 'assignment')
            opn  = semanticCommand.Gassg if op == 'assign' else semanticCommand.Gque
            if opn == semanticCommand.Gassg:
                store.extend([ opn , av[0] , av[1] ])
            else:
                cnt = 0 if op == 'queue' else 1 if len(ax) <= 1 else int(ax[1])
                store.extend([ opn , av[0] , av[1] , cnt ])
        elif op == 'unite' or op == 'intersect' or op == 'complement':
            av = rs.lower().split('<<')
            if len(av) == 1 or len(av[1]) == 0:
                return _err('incomplete set operation')
            opn = ( semanticCommand.Gunio if op == 'unite' else
                    semanticCommand.Gintr if op == 'intersect' else
                    semanticCommand.Gcomp )
            store.extend([ opn , av[0] , av[1] ])
        elif op == 'show':
            k = rs.find(' ')
            vr = rs if k < 0 else rs[:k]
            ms = '' if k < 0 else rs[k+1:]
            store.extend([ semanticCommand.Gshow , vr , ms ])
        elif op == 'view':
            try:
                nm = int(rs) if len(rs) > 0 else defaultVIEW
                store.extend([ semanticCommand.Gview , nm ])
            except ValueError:
                _err('bad viewing range',l=line)
        else:
            return _err("bad operation: " + op)

#       print ( 'success!' )
        return True

#
#   main loop for procedure compilation
#

    while True:
        line = inp.readline()
        if len(line) == 0: break
#       print ( '>>' , line )
        k = line.find(' # ')         # look for comments
        if k > 0:
            line = line[:k].rstrip() # and remove them
        if line[0] == '(':
            if not _procParse(line): # interpret procedure call
                return None
        elif not _operParse(line):   # interpret semantic command
#           print ( 'returning None on failure!' )
            return None

    if len(backl) == 0:
        return store
    else:
        _err('missing END')
        return None

_code = { 'SP' : '\x20, \xa0' , 'HT' : '\x09' , 'LF' : '\x0a' , 'NL' : '\x0a' , 'CR' : '\x0d' }

def _eqsplit ( s ):

    """
    divide argument string at first occurrence of an '=' or ' '

    arguments:
        s   - input string

    returns:
        an array with one or two substrings depending on success of division
    """

    k = s.find('=')
    if k < 0:
        k = s.find(' ')
        if k < 0:
            return [ s ]
        else:
            st = s[k+1:].upper()
            ss = _code[st] if st in _code else ''
            return [ s[:k] , ss ]
    else:
        return [ s[:k] , s[k+1:] ]

def _getargs ( rs ):

    """
    parse arguments for insert or extract or peek command

    arguments:
        self  -
        rs    - argument string for a command

    returns:
        argument list on success, None otherwise
    """

    ar = rs.split(' ')
#   print ( '_getargs' , ar )
    if len(ar) < 2: return None
    x = ar[0]
    if x in _dir:
        ar[1] = ar[1].lower()
        return ar
    elif ar[1] in _dir:
        ar[0] = ar[1]
        ar[1] = x.lower()
        return ar
    else:
        return None

#
# unit test
#

def showCode ( cod , pnx=None ):

    """
    show operations in compiled generative semantic procedure

    arguments:
        cod   - code to display
        pnx   - to check for definition of procedure name
    returns:
        mumber of instances of undefined subprocedures
    """

#   print ( 'pnx=' , pnx )
    if cod == None:
        print ( 'No Code' )
        return
    noe = 0
    loc = 0
    while len(cod) > 0:
        cdg = cod[0]
        dl  = semanticCommand.Glen[cdg]
        com = semanticCommand.Gopn[cdg]
        arg = cod[1:dl] if dl != 1 else ''
#       print ( 'dl=' , dl , 'arg=' , arg );
        if (pnx != None and
            cdg == semanticCommand.Gproc and
            not arg[0] in pnx):
            print ( '>{0:3d} **** call to unknown subprocedure: {1}'.format(loc,arg[0]) )
            noe += 1
        else:
            print ( '>{0:3d} {1} {2}'.format(loc,com,arg) )
        cod = cod[dl:]
        loc += dl
    return noe

if __name__ == "__main__":

    import ellyDefinitionReader
    import symbolTable

    stbd = symbolTable.SymbolTable()

    print ( 'generative semantic compilation test' )
    srcd = sys.argv[1] if len(sys.argv) > 1 else 'generativeDefinerTest.txt'
    inpd = ellyDefinitionReader.EllyDefinitionReader(srcd)
    if inpd.error != None:
        print ( "cannot read procedure definition" , file=sys.stderr )
        print ( inpd.error , file=sys.stderr )
        sys.exit(1)

    print ( 'input=' , srcd )

    codg = compileDefinition(stbd,inpd)
    if codg == None:
        print ( "semantic compilation error" , file=sys.stderr )
        sys.exit(1)

    print ( len(codg) , 'code elements in procedure' )
    showCode(codg)
