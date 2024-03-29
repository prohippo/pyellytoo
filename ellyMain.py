#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# ellyMain.py : 03jun2021 CPM
# ------------------------------------------------------------------------------
# Copyright (c) 2019-20, Clinton Prentiss Mah
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
full Elly test driver reading from stdin and writing to stdout
with optional tree dump

this buffers and processes text with possibly more than one sentence
"""

import sys
import os.path
import ellyException
import ellyConfiguration

defaultsystem='test'

so = sys.stdout

globs = [ ]       # Elly global variables to initialize
dl    = -1        # tree display depth limit
plsb  = False     # show plausibility scoring in output

a = sys.argv[1:]  # drop invocation name of module in argument list

#
# interpret command line flags
#

while len(a) > 0 and a[0][0] == '-': # check for commandline flag
    flg = a.pop(0)
#   print ( 'flg=' , flg )
    if   flg == '-b':                # batch processing?
        interact = False
    elif flg == '-d':                # limit parse tree display depth?
        if len(a) > 0:
            dl = int(a.pop(0))
    elif flg == '-g':                # initialize global variables?
        if len(a) > 0:
            globs = a.pop(0).split(',')
    elif flg == '-p':
        plsb = True
    elif flg == '-noLang':           # turn off default language analysis?
        ellyConfiguration.language = ''
    elif len(flg) == 8 and flg[:6] == '-lang=':
        ellyConfiguration.language = flg[6:].upper()
#       print ( 'language=' , ellyConfiguration.language )

import stopExceptions
import ellySentenceReader
import ellyDefinitionReader
import ellyBase                      # must be imported LAST

interact = sys.stdin.isatty()        # to check for redirection of stdin (=0)

system  = a[0] if len(a) > 0 else defaultsystem
restore = a[1] if len(a) > 1 else None

if interact:
    print ( "PyElly" , ellyBase.release + "," , "Natural Language Filtering" )
    print ( "Copyright 2014-2021 under BSD open-source license by C.P. Mah" )
    print ( "All rights reserved" )
    print ()

    print ( "reading" , '<' + system + '>' , "definitions" )

eb = ellyBase.EllyBase(system,restore) # set up sentence translation

ix = 0
for gv in globs:                       # initialize global variables
    vr = 'gp' + str(ix)                # variable names = gp0, gp1, ...
    eb.setGlobalVariable(vr,gv)
    print ( vr , '=' , gv )
    ix += 1

if dl >= 0:                            # check for specific depth limit
    eb.ptr.setDepth(dl)                # if so, set it

base = ellyConfiguration.baseSource
sent = base + system + '.sx.elly'      # get stop punctuation exceptions
if not os.path.isfile(sent): sent = base + ellyConfiguration.defaultSystem + '.sx.elly'

ind = ellyDefinitionReader.EllyDefinitionReader(sent)
if ind.error != None:
    print ( 'cannot read stop exceptions' , file=sys.stderr )
    print ( ind.error , file=sys.stderr )
    sys.exit(1)

try:

    exs = stopExceptions.StopExceptions(ind)

    rdr = ellySentenceReader.EllySentenceReader(sys.stdin,exs) # set up sentence reader

except ellyException.TableFailure as e:

    print ( '** input initialization failure' , file=sys.stderr )
    sys.exit(1)

if interact:
    print ()
    print ( 'Enter text with one or more sentences per line.' )
    print ( 'End input with E-O-F character on its own line.' )

while True:
    if interact:
        print ( 'getting next sentence' )
    b = rdr.getNext()            # get next sentence
    if b == None: break          # EOF check
    if len(b) == 0: continue     # ignore empty lines
#   print ( 'main b=' , b )

    if interact:
        print ( 'translating' , b )
    bo = eb.translate(b,plsb)    # translate to output
    if bo == None:
        print ( 'ERROR: no translation\n\n' , file=sys.stderr )
        continue
    out = ''.join(bo)

    if interact:
        print ( '----------------------------------------------------------------' )
        if ellyConfiguration.inputEcho:
            print ( len(b) , 'chars in' )
            print ( ' [' + ''.join(b) + ']' )
            print ( len(out)  , 'chars out' )
        so.write( ' =[' + out + ']\n' ) # actual output in brackets
    else:
#       print ( len(bo) , list(bo) )
        so.write( ' ' + out )            # plain output only
        so.write( '\n' )                 #
        so.flush()

    if interact:
        print ( '----------------------------------------------------------------' )
        eb.ptr.dumpAll()         # show all parse tree nodes not already shown

if interact:
    print ( 'Good-bye' )
