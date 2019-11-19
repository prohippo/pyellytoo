#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# syntaxSpecification.py : 16nov2019 CPM
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
interpreting full syntax specification of phrase or grammar rule
"""

import sys
import ellyChar
import ellyException
import featureSpecification

catid = { }  # feature IDs seen with categories

def scan ( strg ):

    """
    check for extent of syntax specification

    arguments:
        strg  - string of chars to scan

    returns:
        char count > 0 on finding possible syntax specification, 0 otherwise
    """

    n = 0
    for c in strg:
        if c == '.' or ellyChar.isLetterOrDigit(c): n += 1
        else: break
    else:
        return n
    c = strg[n]
    if c == ' ': return n
    if c != '[': return 0
    k = featureSpecification.scan(strg[n:])
    return n + k if k > 0 else 0

class SyntaxSpecification(object):

    """
    store encoded syntax category and features

    attributes:
        catg  - numerically encoded category (e.g. NOUN or VERB)
        synf  - syntactic features as EllyBits
    """

    def __init__ ( self , syms , spec ):

        """
        initialization from input string and symbol table

        arguments:
            self  -
            syms  - current symbol table
            spec  - input string

        exceptions:
            FormatFailure on error
        """

        self.catg = -1    # values to set on an error
        self.synf = None  #

#       print ( 'specification=' , spec  , file=sys.stderr )
        if spec == None:
            print ( '** null syntax specification' , file=sys.stderr )
            raise ellyException.FormatFailure

        s = spec.lower()  # must be lower case for all lookups

        n = 0
        for c in s:
            if not ellyChar.isLetterOrDigit(c) and c != '.': break
            n += 1

        if n == 0:
            print ( '** no syntactic category' , file=sys.stderr )
            raise ellyException.FormatFailure

        typs = s[:n]        # save category name
#       print ( 'catg=' , self.catg , file=sys.stderr )
        catg = syms.getSyntaxTypeIndexNumber(typs)
        if catg == None:
            raise ellyException.FormatFailure

        s = s[n:].strip()   # feature part of syntax

        if len(s) == 0:     # check if there are any features
            synf = featureSpecification.FeatureSpecification(syms,None)
            if typs == '...':
                synf.id = '...'
        elif typs == '...': # ... category may have no features!
            raise ellyException.FormatFailure
        else:               # decode features
#           print ( 'syms=' , syms , 's=' , s , file=sys.stderr )
            if len(s) < 4:
                print ( '** bad syntactic type or missing features= ' , typs+s , file=sys.stderr )
                raise ellyException.FormatFailure
            if typs in catid and catid[typs] != s[1]:
                print ( '** type' , typs.upper() , 'has two feature IDs:' , catid[typs] , s[1] , file=sys.stderr )
                raise ellyException.FormatFailure
            catid[typs] = s[1]
            synf = featureSpecification.FeatureSpecification(syms,s)

        # FormatFailure exception may be raised above, but will not be caught here

#       print ( 'success'  , file=sys.stderr )
        self.catg = catg
        self.synf = synf

    def __str__ ( self ):

        """
        show SyntaxSpecification

        arguments:
            self

        returns:
            string representation
        """

        fs = '  +....-....' if self.synf == None else self.synf.id + ' ' + str(self.synf)
        return 'type=' + str(self.catg) + ' ' + fs

#
# unit test
#

if __name__ == '__main__':

    import symbolTable

    stb = symbolTable.SymbolTable()
    stb.getSyntaxTypeIndexNumber('sent')
    stb.getSyntaxTypeIndexNumber('end')
    stb.getSyntaxTypeIndexNumber('unkn')
    stb.getSyntaxTypeIndexNumber('...')

#   note that ... may not have syntactic features specified

    spcl = sys.argv[1:] if len(sys.argv) > 1 else [ '...[.0,1]' , 'unkn[:x]' ]
    print ( 'testing' , len(spcl) , 'examples' )
    for spc in spcl:
        ns = scan(spc)
        sx = spc[:ns]
        print ( ns , 'chars in possible specification' )
        try:
            ss = SyntaxSpecification(stb,sx)
        except ellyException.FormatFailure:
            print ( '** fail on [' , sx , ']'  , file=sys.stderr )
            continue
        print ( 'syntax specification  {0:20s}='.format(sx) , end=' ' )
        print ( '' , ss )
