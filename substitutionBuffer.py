#!/usr/bin/python3
# PyElly - rule-basee tool for analyzing natural language (Python v3.8)
#
# substitutionBuffer.py 16nov2019 CPM
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
text input macro substitution with various wildcards and optional components
(which may NOT contain wildcards except for _)
"""

import ellyChar
import ellyWildcard
import ellyBuffer
import ellyBufferEN
import ellyBufferZH
import ellyConfiguration
import macroTable

BufferType = (
    ellyBufferEN.EllyBufferEN if ellyConfiguration.language == 'EN' else
    ellyBufferZH.EllyBufferZH if ellyConfiguration.language == 'ZH' else
    ellyBuffer.EllyBuffer
)

class SubstitutionBuffer(BufferType):

    """
    input buffer with macro substitutions automatically applied

    attributes:
        sup   - instance as parent class
        mtb   - macro substitution rules
    """

    def __init__ ( self , macros ):

        """
        initialization with macro table

        arguments:
            self   -
            macros - indexed macro substitutions
        """

        self.buffer = None
        self.sup = super(SubstitutionBuffer,self)
#       print ( "parent:",self.sup )

        self.sup.__init__() # run initialization for parent class

        self.mtb = macros   # save macros

    def getNext ( self ):

        """
        get next token from buffer after any macro expansions

        arguments:
            self

        returns:
            EllyToken on success, None on failure

        exceptions:
            StemmingError
        """

#       print ( 'SUB getNext' )
#       print ( 'buffer=' , self.buffer )
        limit = 2*len(self.buffer)       # maximum expansion allowed

        oto = None
        while True:
#           print ( 'substitution@0=' , self.buffer )
            to = self.sup.getNext()      # get the next token with parent method first
                                         #   (for side effects)
#           print ( 'substitution@1=' , self.buffer )
            if to == None: return None   # stop on end of input
#           print ( 'to=' , to , 'divided=' , to.isSplit() )
            if oto == None: oto = to
#           print ( 'subs to=' , to )
            self.putBack(to)             # put it back in buffer for pattern matching
#           print ( 'substitution@2=' , self.buffer )
            if not self.expand(): break  # apply macro substitutions on buffer
                                         # until no more will match

#           print ( 'substitution@3=' , self.buffer )
            if len(self.buffer) > limit: # to avoid infinite expansion
                return None

#       print ( 'substitution *=' , self.buffer )
        self.divided = oto.dvdd
#       print ( 'SUB expanded' )
#       print ( 'buffer=' , self.buffer )
        nto = self.sup.getNext()         # then get next token
        if nto.getRoot() == oto.getRoot():
            nto = oto
#       print 'substitution nto=' , nto
#       print ( 'buffer=' , self.buffer )
        return nto

    def expand ( self ):

        """
        implement macro pattern match and substitution in buffer

        arguments:
            self

        returns:
            True if any substitution done, False otherwise
        """

        done = False

#       print ( 'expanding' )
#       print ( 'text=' , str(self) )

        while True:

            # use first char to select subset of macros to match against

            x = self.peek()
            if x == None: break
#           print ( 'expand x=' , ord(x) , x )
            lr = self.mtb.getRules(x)
#           print ( len(lr) , ' macros to check' )

            # try selected macros sequentially on start of input buffer

            for r in lr:
#               print ( 'rule=' , r )
                if self._match(r):
#                   print ( 'macro matched' )
                    done = True
                    break
            else:
#               print ( 'no macros matched' )
                break

#           print ( 'expanded=' , str(self) )

        return done

    def _match ( self , rule ):

        """
        compare a macro pattern to input text and substitute on match
        (easier to do both in one method because of match bindings)

        arguments:
            self  -
            rule  - [ pattern , spaces , rewriting ]

        returns:
            True if matched and substituted, False otherwise
        """

        capital = self.isCapital()   # starts with capital?

        pattern = rule[0]            # split up macro substitution rule
        spaces  = rule[1]            #
        rewrite = rule[2]            #

#       print ( 'pattern=' , ellyWildcard.deconvert(pattern) )
#       print ( 'text   =' , self.buffer )

        lim = len(self.buffer)       # limit on any expansion after match

#       print ( 'lim=' , lim )

        mbd = ellyWildcard.match(pattern,self.buffer,0,lim,spaces) # try to match
#       print ( 'match=' , not (mbd == None) )
        if mbd == None: return False                               # if no match bindings, stop

        mbl = len(mbd)               # limit on wildcard bindings from match

#       print ( 'mbl=' ,mbl )

        # compile substitution for matched macro

        mr = 0                       # index variable for rewriting
        me = len(rewrite)            # limit

#       print ( "rewrite len=",me,rewrite )

        ob = [ ]                     # for substitution output

        while mr < me:               # iterate on rewrite

            c = rewrite[mr]          # next char in rewrite
#           print ( '_match c=' , c )
            mr += 1

            if c != '\\':            # literal char
                ob.append(c)         # if so, put into output
            elif mr < me:            # otherwise, look for binding index
                x = rewrite[mr]      # index must be single digit
                try:
                    k = int(x)
#                   print ( "binding:" , '\\' + x , mbl )
                    if k < mbl:
                        r = mbd[k]   # get bind record
                        ob.extend(self.buffer[r[0]:r[1]]) # add bound chars to output
                except ValueError:
                    ob.append(ellyChar.SPC)               # otherwise treat as spac
                mr += 1              # skip over char after \
            else:
                ob.append(c)         # no index number, save \

#       print ( "ob:",ob )

        # copy substitution back

        nm = mbd[0]                      # number of chars matched
        self.buffer = self.buffer[nm:]   # remove them from buffer

#       print ( "remainder:",self.buffer )

        if self.atToken():
            self.prepend(ellyChar.SPC)   # insert space if none already there
        self.prepend(ob)                 # put substitution into input buffer at start
#       print ( "after:",    self.buffer )

        if capital:                      # restore any capitalization
            self.setCapital()

        return True                      # successful match

#
# unit test
#

if __name__ == "__main__":

    import sys
    import ellyDefinitionReader
    import ellyException

    basn = ellyConfiguration.baseSource + '/'
    filn = sys.argv[1] if len(sys.argv) > 1 else 'test'
    mrdr = ellyDefinitionReader.EllyDefinitionReader(basn + filn + '.m.elly')

    print ( "loading rules for" , filn )

    if mrdr.error != None:
        print ( mrdr.error , file=sys.stderr )
        sys.exit(1)
    mtbl = macroTable.MacroTable(mrdr)
    sbuf = SubstitutionBuffer(mtbl)

    print  ( 'enter text for macro substitution' )
    while True:
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            l = sys.stdin.readline()
        except KeyboardInterrupt:
            break
        l = l.strip()
        if len(l) == 0: break

        sbuf.clear()
        sbuf.append(list(l))

        print ( sbuf.buffer )

        while True:
            print ( "buf len=" , len(sbuf.buffer) )
            try:
                t = sbuf.getNext()
            except ellyException.StemmingError:
                print ( 'stemming error' , file=sys.stderr )
                break
            if t == None: break
            print ( ">>>>" , str(t) )
            b = sbuf.buffer
            if len(b) > 5: b = b[:5]
            print ( 'TO' , b )
        print ( "------------" )
    sys.stdout.write("\n")
