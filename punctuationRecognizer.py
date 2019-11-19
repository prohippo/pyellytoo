#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# punctuationRecognizer.py : 16nov2019 CPM
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
builtin single-char punctuation recognition for PyElly grammars

provided as a convenience so that these common marks do not have to be listed
in an internal dictionary or an external table for every grammar definition

multiple-char punctuation MUST be defined elsewhere!
"""

import ellyBits
import ellyChar
import featureSpecification

# NOTE: category and feature names here must be in lower case!
#

category = 'punc' # must be used in grammars for punctuation syntax type!
pID      = '|'    # must be used for punctuation syntactic feature ID
sID      = '!'    #                              semantic  feature ID

sBRK     = 'brk'  # reserved for semantic identification of punctuation

RS = ellyChar.RS  # special control character

# the *x feature is used below to distinguish a period, a square bracket, or an m dash;
# syntax rules should check the other features of a leaf phrase node to determine which
# sense is meant. Remember that *x CANNOT be inherited!

defns = [                                      # syntactic significance of punctuation
    [ '[' , '[' + pID + '*l,*x,start]' ] ,    # equivalent to D: rules in *.g.elly
    [ ']' , '[' + pID + '*r,*x]' ] ,          #
    [ '(' , '[' + pID + '*l,start]' ] ,       # you may override any of these with explicit
    [ ')' , '[' + pID + '*r]' ] ,             # D: punctuation rules of higher plausibility
    [ '“' , '[' + pID + '*l,quo,start]' ] ,
    [ '”' , '[' + pID + '*r,quo]' ] ,
    [ '"' , '[' + pID + '*l,*r,quo,start]' ] ,
    [ '‘' , '[' + pID + '*l,quo,start]' ] ,
    [ '’' , '[' + pID + '*r,quo]' ] ,
    [ '`' , '[' + pID + '*l,quo,start]' ] ,
    [ "'" , '[' + pID + '*l,*r,quo,start]' ] ,
    [ ',' , '[' + pID + 'com]' , True ]  ,    # special status for comma only, so far
    [ '.' , '[' + pID + 'stop,emb,*x]' ] ,    # these will end sentences, but can be embedded
    [ '!' , '[' + pID + 'stop,emb]' ] ,
    [ '?' , '[' + pID + 'stop,emb]' ] ,
    [ ':' , '[' + pID + 'stop,emb]' ] ,
    [ ';' , '[' + pID + 'stop]' ] ,
    [ '…' , '[' + pID + 'start]' ]  ,         # horizontal ellipsis

    [ '\u3008' , '[' + pID + '*l,quo,start]' ] , # Chinese quotation left
    [ '\u3009' , '[' + pID + '*r,quo]' ] ,       #                   right
    [ '\u2122' ] ,                               # TM
    [ '\u2013' , '[' + pID + 'start]' ] ,        # en dash
    [ '\u2014' , '[' + pID + 'start,*x]' ] ,     # em dash
    [ '\u002d' , '[' + pID + 'hyph]'  ] ,        # hyphen or minus
    [ '\u2010' , '[' + pID + 'hyph]'  ] ,        # hyphen only
    [ '\uff0c' , '[' + pID + 'com]' , True ] ,   # Chinese comma
    [ '\u3002' , '[' + pID + 'stop,*x]' ]        # Chinese period
]

smfs  = {  # semantic features for particular punctuation
    ')' : '[' + sID + 'spcs]'
}

def _FS ( symbls , featrs , ftype=False ):
    """
    get ellyBits encoding of syntactic features
    arguments:
        syms   - symbol table for feature names
        featrs - feature string
        ftype  - True for semantic, False for syntactic
    returns:
        ellyBits object on success
    exceptions:
        FormatFailure on error
    """
    return featureSpecification.FeatureSpecification(symbls,featrs,ftype).positive

#
## end static definitions
#

class PunctuationRecognizer(object):

    """
    recognizer to support parsing

    attributes:
        catg     - syntactic category for recognized punctuation
        synf     - syntactic features
        semf     - semantic  features
        hpnc     - hash lookup for punctuation chars
    """

    def __init__ ( self , syms ):

        """
        initialization

        arguments:
            self  -
            syms  - Elly symbol table

        exceptions:
            FormatFailure on error
        """

        self.catg = syms.getSyntaxTypeIndexNumber(category)
        self.synf = None
        self.semf = None
        self.hpnc = { }
        brkg = _FS(syms,'[' + sID + sBRK + ']',True)
        zero = ellyBits.EllyBits()
#       print ( 'smfs=' , smfs )
        for sky in smfs.keys():   # predefine semantic features for punctuation
#           print ( 'sky=' , sky , ' : ' , smfs[sky] )
            smfs[sky] = _FS(syms,smfs[sky],True)
        for defn in defns:        #           syntactic
            pc = defn[0]
            if len(defn) > 1:
                sxf = _FS(syms,defn[1])
                smf = smfs[pc] if pc in smfs else brkg if len(defn) > 2 else zero
                self.hpnc[pc] = [ sxf  , smf  ]
            else:
                self.hpnc[pc] = [ zero , zero ]

    def match ( self , s ):

        """
        check whether list of chars corresponds to punctuation

        arguments:
            self  -
            s     - list or string of chars to check (usually an EllyToken root)

        returns:
            True if listed punctuation, False otherwise
        """

        if len(s) != 1:          # only single-char punctuation expected here!
            return False

        schr = s[0]              # possible punctuation char
        if not schr in self.hpnc:
            return False
        else:
            rec = self.hpnc[schr]
            self.synf = rec[0]   # for later reference along with synf.catg
            self.semf = rec[1]   #
            return True

#
# unit test
#

if __name__ == '__main__':

    import symbolTable

    ups = list('.?!ab,;:+cd()$%&\'\"ef-–—“”…hg`i™〈〉')

    print ( 'testing' , ups , len(ups) )
    symb = symbolTable.SymbolTable()
    punc = PunctuationRecognizer(symb)

    ft = symb.sxindx[pID]    # show synractic feature names for PUNC[| ]
    del ft['*left']
    del ft['*right']
    print ( 'punc [| ]:' , ft )

    for chu in ups:
        print ( '[' , chu , ']' , end=' ' )
        if punc.match(chu):
            print ( ' is PUNC' , punc.synf.hexadecimal() , ':' , punc.semf.hexadecimal() )
        else:
            print ( ' not PUNC' )

    chu = '\u001E'
    print ( '[ RS ]' , end=' ' )
    if punc.match(chu):
        print ( 'is PUNC' , punc.synf.hexadecimal() , ':' , punc.semf.hexadecimal() )
    else:
        print ( 'not PUNC' )

