#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# extendedContext.py : 03jun2021 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2021, Clinton Prentiss Mah
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
PyElly extended capabilities through special generative semantic subprocedures
"""

#
# currently supporting only ActiveWatch n-gram analysis,
# but could also be a way of implementing arithmetic
# in Elly generative semantics
#
# (edit this file to add more special subprocedures)
#
# all subprocedures will get their input from the Elly
# auxiliary output buffer using the method _enstrg()
#
# this code directly accesses the Elly framework for rewriting input
# text, like other generative semantic subprocedures, and so is set up,
# as a nobject-oriented subclass to InterpretiveContext

import wordFragment

import interpretiveContext
import ellyChar

class ExtendedContext(interpretiveContext.InterpretiveContext):

    """
    switchboard for calling external Python code in generative semantics

    attributes:
        ptbl - externally defined subprocedures
    """

    def __init__ ( self , syms , procs , glbls , hiery ):

        """
        set up for special external subprocedures

        arguments:
            self   -
            syms  - symbol table
            procs - standalone procedure dictionary
            glbls - global variables dictionary
            hiery - conceptual hierarchy
        """

        super(ExtendedContext,self).__init__(syms,procs,glbls,hiery)
        self.ptbl = { }
        self.ptbl['xngm'] = self._xngm

    def checkName ( self , name ):

        """
        check if name is defined

        arguments:
            self -
            name - procedure name

        returns:
            True if defined, False otherwise
        """

        return name in self.ptbl

    def executeName ( self , name ):

        """
        run subproceure

        arguments:
            self -
            name - of subprocedure

        returns:
            True on success, False otherwise
        """

        if not name in self.ptbl: return False

        return self.ptbl[name]()

    def _enstrg ( self ):

        """
        get chars from auxiliary buffer

        arguments:
            self

        returns:
            chars joined into a string
        """

        self.deleteCharsFromBuffer(100)
        chi = list(self.getDeletion())
        cho = [ ]
        for ch in chi:
            if ellyChar.isLetter(ch):
                cho.append(ellyChar.Unmapping[ellyChar.Mapping[ord(ch)]])
        return "".join(cho)

    def _xngm ( self ):

        """
        run n-gram extraction

        arguments:
            self

        returns:
            True on success, False otherwise
        """

        strg = self._enstrg()
        if len(strg) == 0: return False
        ngls = wordFragment.divide(strg)
        for ng in ngls:
            self.insertCharsIntoBuffer(ng)
            self.insertCharsIntoBuffer(' ')
        self.deleteCharsFromBuffer(-1)
        return True

#
# unit testing from command line argument input
#

import sys

if __name__ == "__main__":

    sinp = "megaclassic" if len(sys.argv) == 1 else sys.argv[1]
    print ( 'input=' , sinp )

    ctx = ExtendedContext(None,None,None,None)
    ctx.splitBuffer()
    ctx.insertCharsIntoBuffer(sinp)
    ctx.backBuffer()

    print ( ctx.executeName('xngm') )

    ctx.deleteCharsFromBuffer(-100)
    print ( ctx.getDeletion() )
