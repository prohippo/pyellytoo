#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# vocabularyElement.py : 16nov2019 CPM
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
vocabulary element from external table lookup
"""

import sys
import ellyBits
import ellyException
import ellyDefinitionReader
import generativeProcedure
import unicodedata

gens = [ '*' ]      # define generative procedure for translation
geno = [ 'obtain' ] # default generative procedure

inptx = ellyDefinitionReader.EllyDefinitionReader(geno)
obtnp = generativeProcedure.GenerativeProcedure(None,inptx)

class VocabularyElement(object):

    """
    vocabulary term plus definition

    attributes:
        chs   - list of chars in term
        cat   - syntactic category
        syf   - syntactic flags
        smf   - semantic  flags
        bia   - initial plausibility score
        con   - associated concept
        gen   - generative procedure

        _nt   - number of translations
        _ln   - total char length of term
    """

    def __init__ ( self , dta ):

        """
        initialization of vocabulary object from retrieved record

        arguments:
            self  -
            dta   - what DB support returns

        throws:
            FormatFailure on error
        """

        self._ln = 0
        rec = dta[1]                     # data record found for search key
#       print ( 'voc rec=' , rec , file=sys.stderr )
        r = rec.split('=:')              # split off term in data record
        if len(r) <= 1: return           # the '=:' is mandatory
        d = r[1].strip().split(' ')      # definition is right of '=:'
#       print ( 'VEntry: define as' , d , file=sys.stderr )
        if len(d) <  4: return           # it should have at least 4 parts
        ur = r[0].strip()                # term left of '=:'
        self.chs = list(ur)              # save it
        self.cat = int(d.pop(0))         # syntactic category
#       print ( '    full term=' , ''.join(self.chs) , file=sys.stderr )
        sy = d.pop(0)
        nb = len(sy)*4
        self.syf = ellyBits.EllyBits(nb) # allocate bits
        self.syf.reinit(sy)              # set syntactic features
        sm = d.pop(0)
        nb = len(sm)*4
        self.smf = ellyBits.EllyBits(nb) # allocate bits
        self.smf.reinit(sm)              # set semantic  features
        self.bia = int(d.pop(0))         # save initial plausibility
        if len(d) > 0:                   # any concept?
            self.con = d.pop(0).upper()  # if so, save it
        else:
            self.con = '-'

#       print ( '    translation=' , d , file=sys.stderr )

        if len(d) == 0:        # no further definition?
            self.gen = obtnp   # if so, then use default procedure
            self._nt = 0       #   i.e. no translation
        elif d[0][0] == '=':   # simple translation?
            dfs = ' '.join(d)  # just in case translation had spaces
#           print ( 'def ext=' , dfs , file=sys.stderr )
            pls = [ 'append ' + dfs[1:] ]
            inpts = ellyDefinitionReader.EllyDefinitionReader(pls)
            self.gen = generativeProcedure.GenerativeProcedure(None,inpts)
            self._nt = 1
        elif d[0][0] == '(':   # get predefined procedure
            inpts = ellyDefinitionReader.EllyDefinitionReader([ d[0] ])
            self.gen = generativeProcedure.GenerativeProcedure(None,inpts)
            self._nt = 0
        else:                  # otherwise, set for selection of translation
#           print ( 'multi selection, d=' , d , file=sys.stderr )
            cm = 'pick LANG (' # construct instruction to select
            for p in d:
                if p[-1] == ',':
                    p = p[:-1]
                cm += p + '#'  # build selection clauses
            cm += ')'
            gens[0] = cm       # replace action
#           print ( 'cm=' , cm )
#           print ( 'gens=' , gens )
            inpts = ellyDefinitionReader.EllyDefinitionReader(gens)
            self.gen = generativeProcedure.GenerativeProcedure(None,inpts)
            if self.gen == None:
                print ( 'vocabulary generative semantic failure' , file=sys.stderr )
                print ( 'gens=' , gens , file=sys.stderr )
                raise ellyException.FormatFailure
#           print ( 'vocabulary gen.logic' )
#           generativeDefiner.showCode(self.gen.logic)
            self._nt = len(d)

        self._ln = len(self.chs)

    def __str__ ( self ):

        """
        Unicode string representation

        arguments:
            self

        returns:
            representation of vocabulary element on success, None otherwise
        """

        tm = ''.join(self.chs)

        df  = 'cat=' + str(self.cat) + ' '
        df += self.syf.hexadecimal(False) + ' : ' + self.smf.hexadecimal(False) + ' '
        df += 'plaus=' + str(self.bia) + ' , '
        df += 'concp=' + self.con + ', '
        df += str(self._nt) + ' TRANSLATION'
        if self._nt != 1: df += 's'

#       print ( 'df=' , df )

        return '[' + tm + '] ' + df

    def length ( self ):

        """
        get total length of any match

        arguments:
            self

        returns:
            char count
        """

        return self._ln
