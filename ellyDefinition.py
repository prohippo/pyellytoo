#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# ellyDefinition.py : 15nov2019 CPM
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
language definition tables that can be pickled for quicker PyElly startup
"""

import sys
import os.path
import symbolTable
import nameTable
import macroTable
import grammarTable
import patternTable
import compoundTable
import vocabularyTable
import morphologyAnalyzer
import conceptualHierarchy
import ellyDefinitionReader
import ellyConfiguration
import ellyException
import ellyPickle

from ellyPickle import grammar
from ellyPickle import vocabulary

class EllyDefinition(object):

    """
    superclass for managing Elly definitions

    attributes:
        errors  - accumulated errors needed by inpT() method
    """

    def __init__ ( self ):

        """
        initialization

        arguments:
            self
        """

        self.errors = [ ]     # initialize as empty list

    def inpT ( self , system , part ):

        """
        inherited method to compose table input

        arguments:
            self   -
            system - which set of table definitions?
            part   - which table to read in?

        returns:
            EllyDefinitionReader on success, None otherwise
        """

        basn = ellyConfiguration.baseSource
        if not basn[-1] == '/': basn += '/'
        suf  = '.' + part + '.elly'
        filn = basn + system + suf
        if not os.path.exists(filn):
            filn = basn + ellyConfiguration.defaultSystem + suf
        print ( 'reading' , filn , end=' ' , file=sys.stderr )
        rdr = ellyDefinitionReader.EllyDefinitionReader(filn)
        if rdr.error != None:
            self.errors.append(rdr.error)
            print ( ': failed' , file=sys.stderr )
            return None
        else:
            print ( ': succeeded' , file=sys.stderr )
            return rdr

class Grammar(EllyDefinition):

    """
    Elly language rule definitions

    attributes:
        stb   - symbols
        mtb   - macro substitution rules
        gtb   - grammar rules
        ptb   - pattern for syntactic types
        ntb   - personal names
        ctb   - compound entities by template
        hry   - conceptual hierarchy
        man   - morphology analyzer
        rls   - saved PyElly software ID
    """

    def __init__ ( self , system , create , rid=None ):

        """
        load all definitions from binary or text files

        arguments:
            self     -
            system   - which PyElly application
            create   - whether to create new binary
            rid      - PyElly release ID

        exceptions:
            TableFailure on error
        """

        super(Grammar,self).__init__()

        self.rls = rid
        sysf = system + grammar

        if create:
            print ("recompiling grammar rules" )

            self.stb = symbolTable.SymbolTable()  # new empty table to fill in

            el = [ ]

            try:
                self.mtb = macroTable.MacroTable(self.inpT(system,'m'))
            except ellyException.TableFailure:
                el.append('macro')
            try:
                self.gtb = grammarTable.GrammarTable(self.stb,self.inpT(system,'g'))
                self.stb.setBaseSymbols()
            except ellyException.TableFailure:
                el.append('grammar')
            try:
                self.ptb = patternTable.PatternTable(self.stb,self.inpT(system,'p'))
            except ellyException.TableFailure:
                el.append('pattern')

            try:
                self.hry = conceptualHierarchy.ConceptualHierarchy(self.inpT(system,'h'))
            except ellyException.TableFailure:
                el.append('concept')

            try:
                self.ntb = nameTable.NameTable(self.inpT(system,'n'))
            except ellyException.TableFailure:
                el.append('name')

            try:
                self.ctb = compoundTable.CompoundTable(self.stb,self.inpT(system,'t'))
            except ellyException.TableFailure:
                el.append('compound')

            sa = self.inpT(system,'stl')
            pa = self.inpT(system,'ptl')
            try:
                self.man = morphologyAnalyzer.MorphologyAnalyzer(sa,pa)
            except ellyException.TableFailure:
                el.append('morphology')

            if len(el) > 0:
                print ( 'rule FAILures on' , el , file=sys.stderr )
                raise ellyException.TableFailure

            if self.rls != None:
                ellyPickle.save(self,sysf)

        else:
            print ( "loading saved grammar rules from" , sysf )

            gram = ellyPickle.load(sysf)
            if gram == None:
                raise ellyException.TableFailure
            if gram.rls != rid:
                print ( 'inconsistent PyElly version for saved rules' , file=sys.stderr )
                sys.exit(1)
            self.stb = gram.stb  # copy in saved language definition objects
            self.mtb = gram.mtb  #
            self.gtb = gram.gtb  #
            self.ptb = gram.ptb  #
            self.ctb = gram.ctb  #
            self.ntb = gram.ntb  #
            self.hry = gram.hry  #
            self.man = gram.man  #

class Vocabulary(EllyDefinition):

    """
    Elly vocabulary definition

    attributes:
        vtb    - vocabulary table maintained externally
    """

    def __init__ ( self , system , create=False , syms=None ):

        """
        load vocabulary definitions from text file

        arguments:
            self    -
            system  - which PyElly application
            create  - whether to create new binary
            syms    - Elly symbols defined for vocabulary

        exceptions:
            TableFailure on error
        """

#       print ( 'set vocabulary' )
        super(Vocabulary,self).__init__()

        try:
            if create:
                dT = self.inpT(system,'v')
#               dT.dump()
                vocabularyTable.build(system,syms,dT)
            else:
                sysf = system + vocabulary
                print ( "loading saved vocabulary rules from" , sysf )

            self.vtb = vocabularyTable.VocabularyTable(system)
        except ellyException.TableFailure:
            print ( 'rule FAILures on vocabulary' , file=sys.stderr )
            raise ellyException.TableFailure

#
# unit test
#

if __name__ == '__main__':

    sym = symbolTable.SymbolTable()
    nam = sys.argv[1] if len(sys.argv) > 1 else 'test'
    idn = sys.argv[2] if len(sys.argv) > 2 else ''
    rnw = (idn == '')
    print ( 'PyElly' , idn , ', system=' , nam , 'renew=' , rnw )
    print ( "------------ grammar" )
    try:
        grm = Grammar(nam,rnw)
    except ellyException.TableFailure:
        print ( 'grammar rules failed to load' , file=sys.stderr )
        if rnw: print ( '  after recompilation' , file=sys.stderr )
        sys.exit(1)

#   print ( dir(grm) )
    print ( grm.stb )
    print ( grm.mtb )
    print ( grm.gtb )
    print ( grm.ptb )
    print ( grm.ntb )
    print ( grm.ctb )
    print ( grm.hry )
    print ( grm.man )
    for e in grm.errors:
        print ( " *err   " , e )
    print ( "------------ internal dictionary" )
    print ( grm.gtb.dctn.keys() )
    print ( "------------ external vocabulary" )
    try:
        voc = Vocabulary(nam,rnw,sym)
    except ellyException.TableFailure:
        print ( 'vocabulary failed to load' , file=sys.stderr )
        sys.exit(1)
    print ( voc.vtb )
    for e in voc.errors:
        print ( " *err   " , e )
    syn = grm.stb.sxindx
    sem = grm.stb.smindx
    print ( 'synf=' , syn.keys() )
    print ( 'semf=' , sem.keys() )
