#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# dumpEllyGrammar.py : 05jul2020 CPM
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
methods to dump a grammar table
"""

import ellyChar
import cognitiveDefiner
import generativeDefiner
import sys

def dumpAll ( symbols , table , level ):

    """
    show the rules in an Elly grammar table

    arguments:
        symbols - symbol table
        table   - grammar table
        level   - degree of detail
    """

    noe = 0
    print ( len(symbols.ntindx) , 'syntactic categories' )

#   print ('subprocedure index=' , table.pndx )
    dumpInitializations(table.initzn)
    dumpMatrix(symbols,table.mat)
    dumpFeatures(symbols)
    noe += dumpSubprocedures(table.pndx,level > 0)
    noe += dumpSplits(symbols,table.splits,level > 2,table.pndx)
    noe += dumpExtensions(symbols,table.extens,level > 2,table.pndx)
    noe += dumpDictionary(symbols,table.dctn,level > 1,table.pndx)

    print ( "DONE" )
    if noe > 0:
        print ( '' )
        print ( '**' )
        print ( '**' , noe , 'call(s) to unknown subprocedure(s)!' )
        print ( '' )

def dumpInitializations ( inits ):

    """
    show global variable initializations

    arguments:
        inits  - DerivabilityMatrix object
    """

    print ()
    print ( "Global Variable Initializations" )
    print ( "-------------------------------" )

    for x in inits:
        print ( '{:<12.12s} = '.format(x[0]) , x[1] )

def dumpMatrix ( stb , matrix ):

    """
    show derivability matrix

    arguments:
        stb     - symbol table
        matrix  - DerivabilityMatrix object
    """

    print ()
    print ( "Derivability Matrix for Syntactic Structure Types" )
    print ( "-------------------------------------------------" )

    mat = matrix.dm
    ntno = len(stb.ntindx)
    for i in range(ntno):
        print ( '{:2} '.format(i) , end=' ' )
        print ( '{:<6.6s} : '.format(stb.ntname[i]) , end=' ' )
        bmr = mat[i]
        for j in range(ntno):
            if i != j and bmr.test(j):
                print ( '{} '.format(stb.ntname[j]) , end=' ' )
        print ()
        print ( "    " + bmr.hexadecimal() + " " + str(bmr.count()) + ' bytes' )

def dumpCategories ( stb ):

    """
    show syntactic categories

    arguments:
        stb     - symbol table
    """

    print ( "Syntactic Categories" )
    print ( "--------------------" )
    ntno = len(stb.ntname)
    for i in range(ntno):
        print ( '{:2}'.format(i) , stb.ntname[i] )

def dumpFeatures ( stb ):

    """
    show feature sets

    arguments:
        stb     - symbol table

    """

    print ()
    print ( "Feature Sets" )
    print ( "------------" )

    lb = [ 'Syntactic' , 'Semantic' ]
    for fs in [ stb.sxindx , stb.smindx ]:
        lbl = lb.pop(0)
        print ( '--' , lbl )
        fids = list(fs)          # must do in Python 3
        nols = len(fids)
        for i in range(nols):
            idn = fids[i]
            fl = fs[idn]
            print ( '[{0:2}] {1} '.format(i,idn) , end=' ' )
            sls = [ ]
            for f in fl:
                sls.append([ f , fs[idn][f] ])
            sls.sort(key=lambda x: x[1])
            for sr in sls:
                print ( '{0}={1}'.format(sr[0],sr[1]) , end=' ' )
            print ()

def dumpSubprocedures ( index , full , pxl=None ):

    """
    show standalone procedures

    arguments:
        index  - procedure index
        full   - flag for full dump
        pxl    - semantic subprocedure index
    returns:
        number of calls to unknown subprocedures
    """

    print ()
    print ( "Semantic Subprocedures" )
    print ( "----------------------" )

    noe = 0
    lps = index.keys()
    for p in lps:
        print ()
        print ( p )
        if index[p] == None:
            print ( '** undefined!' )
        elif full:
            noe += generativeDefiner.showCode(index[p].logic,pxl)
    return noe

def showMask ( msk ):

    """
    produce hexadecimal representation of feature mask

    arguments:
        msk  - bit string for mask

    returns:
        hexadecimal string
    """

    ln = len(msk)//2   # must do in Python 3
    hi = msk[ln:]
    lo = msk[:ln]

    sb = [ ]
    sb.append('+')
    for i in range(ln):
        sb.append('{:02x}'.format(lo[i]))
    sb.append('-')
    for i in range(ln):
        sb.append('{:02x}'.format(hi[i]))

    return ''.join(sb)

def showProcedures ( r , pxl=None ):

    """
    show semantic procedures for rule

    arguments:
        r    - rule
        pxl  - semantic subprocedure index
    returns:
        number of calls to undefined subprocedures
    """

    noe = 0
    print ( '  ** cognitive' )
    if r.cogs != None:
        cognitiveDefiner.showCode(r.cogs.logic)
    print ( '  ** generative' )
    if r.gens != None:
        noe += generativeDefiner.showCode(r.gens.logic,pxl)
    print ()
    return noe

def dumpSplits ( stb , splits , full , pxl=None ):

    """
    show 2-branch rules

    arguments:
        stb    - symbol table
        splits - listing of 2-branch rules
        full   - flag for full dump
        pxl    - procedure list for optional checking
    returns:
        number of calls to undefined subprocedures
    """

    print ()
    print ( "Splitting Rules" )
    print ( "---------------" )

    noe = 0
    no = 0
    for i in range(len(splits)):
        rv = splits[i]
        k = len(rv)
        if k == 0:
            continue

        ty = stb.ntname[i]

        for j in range(k):
            r = rv[j]
            print ( '(' + str(r.seqn) + ')' , end=' ' )
            print ( stb.ntname[r.styp] , end=' ' )
            sets = r.sfet.hexadecimal(False)
            rsts = r.sftr.hexadecimal(False)
            print ( '[{0}-{1}]->'.format(sets,rsts) , end=' ' )
            print ( ty + ' ' + showMask(r.ltfet) + ' ' , end=' ' )
            print ( stb.ntname[r.rtyp] + ' ' + showMask(r.rtfet) )

            if full: noe += showProcedures(r,pxl)

        no += k

    print ( no , "2-branch grammar rules" )
    return noe

def dumpExtensions ( stb, extens , full , pxl=None ):

    """
    show 1-branch rules

    arguments:
        stb    - symbol table
        extens - listing of 1-branch rules
        full   - flag for full dump
        pxl    - procedure list for optional checking
    returns:
        number of calls to undefined subprocedures
    """

    print ()
    print ( "Extending Rules" )
    print ( "---------------" )

    noe = 0
    no = 0

    for i in range(len(extens)):
        rv = extens[i]
        k = len(rv)
        if k == 0:
            continue

        ty = stb.ntname[i]

        for r in rv:
            print ( '(' + str(r.seqn) + ')' , end=' ' )
            print ( stb.ntname[r.styp] , end=' ' )
            sets = r.sfet.hexadecimal(False)
            rsts = r.sftr.hexadecimal(False)
            print ( '[{0}-{1}]->'.format(sets,rsts) , end=' ' )
            print ( ty + ' ' + showMask(r.utfet) )

            if full: noe += showProcedures(r,pxl)

        no += k

    print ( no , "1-branch grammar rules" )
    return noe

def dumpDictionary ( stb, dctn , full , pxl=None ):

    """
    dump internal dictionary

    arguments:
        stb   - symbol table
        dctn  - dictionary
        full  - flag for full dump
        pxl   - procedure list for optional checking
    returns:
        number of calls to undefined subprocedures
    """

    print ()
    print ( "Internal Dictionary" )
    print ( "-------------------" )

    noe = 0
    no = 0

    ws = dctn.keys()
#   print ( ws )

    for w in ws:

        dv = dctn[w]

        k = len(dv)
        if k == 0:
            continue

        for dr in dv:
            print ( stb.ntname[dr.styp] , end=' ' )
            print ( '[{}]->'.format(dr.sfet.hexadecimal(False)) , end=' ' )
            if w == ellyChar.RS:
                print ( '<RS>' )
            else:
                us = '"' + w + '"'
                print ( us )

            if full: noe += showProcedures(dr,pxl)

        no += k

    print ( len(dctn) , 'unique tokens in' , no , "dictionary rules" )
    return noe

#
# unit test
#

if __name__ == '__main__':

    import ellyException
    import ellyDefinition
    import ellyPickle

    nam = sys.argv[1] if len(sys.argv) > 1 else 'test'
    lvl = sys.argv[2] if len(sys.argv) > 2 else '3'
    ver = sys.argv[3] if len(sys.argv) > 3 else ''

    rul = ellyPickle.load(nam + '.rules.elly.bin')
    if rul == None:
        try:
            rul = ellyDefinition.Grammar(nam,True,ver)
        except ellyException.TableFailure:
            print ( 'grammar rules failed to compile' , file=sys.stderr )
            sys.exit(1)

    dumpAll(rul.stb,rul.gtb,int(lvl))
