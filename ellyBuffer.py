#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# ellyBuffer.py : 16nov2019 CPM
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
an input buffer class for Elly language analysis
"""

import ellyChar
import ellyToken
import unicodedata

separators = [                 # for breaking tokenization scan
    '-'  ,
    ' '  , '\u2009' ,
    '\t' , '\r' , '\n' ,
    ellyChar.RS ,
    '('  , ')'  ,
    '['  , ']'  ,
    '<'  , '>'  ,
    '"' , '\u201c' , '\u2018' , '\u201b' , '\u201f' ,
    '`' , '\u201d' ,            '\u201a' , '\u201e' ,
          '\u2013' , '\u2014' , '\u2026' ,
          '\u3008' , '\u3009'
]

PLS = '+'                     # special token chars
MIN = '-'
COM = ','
UNS = '_'
DOT = '.'

DSH = '--'                    # dash
ELP = '...'                   # ellipsis
SPH = ' -'                    # space + hyphen
DQM = '"'                     # ASCII double quote
APO = ellyChar.APO            # apostrophe literal
APX = '\u2019'                # Unicode apostrophe
RSQ = '\u2019'                # Unicode right single quote
RDQ = '\u201D'                #               double quote
RAB = '\u3009'                #               angle bracket

UELP = '\u2026'               # Unicode ellipsis

class EllyBuffer(object):

    """
    dynamically refilled text input buffer

    attributes:
        buffer  # text as list of single Unicode chars
        index   # save results of find operations
    """

    def __init__ ( self ):

        """
        create an empty buffer as expandable list of chars

        arguments:
            self
        """

        self.buffer = None
        self.index  = None
        self.clear()

    def __str__ ( self ):

        """
        get print representation of buffer

        arguments:
            self

        returns:
            Unicode string representation
        """

        nc = self.count()
        bf = self.buffer
        out = [ ]
        md = 16
        for i in range(nc):
            if i%md == 0: out.append('\n')
            out.extend([ '<' , bf[i] , '>' ])
        out.append('\n')
        return 'EllyBuffer: {:d} chars'.format(nc) + ''.join(out)

    def normalize ( self , s ):

        """
        convert all unrecognizable input chars to _ and any
        consecutive white spaces to a single space

        arguments:
            self -
            s    - Unicode string or char list to operate on
        returns:
            normalized sequence
        """

#       print ( '__ normalize' )
        spaced = False
        n = len(s)
        ns = [ ]
        for i in range(n):
            x = s[i]
            if ellyChar.isLetter(x):
                spaced = False
            elif ellyChar.isWhiteSpace(x):
                if spaced: continue
                x = ' '
                spaced = True
            elif not ellyChar.isText(x):
                x = '_'
                spaced = False
            else:
                spaced = False
            ns.append(x)
        return ns

    def clear ( self ):

        """
        set buffer to empty

        arguments:
            self
        """

        self.buffer = [ ]
        self._reset()

    def _reset ( self ):

        """
        clear offset from any previous find

        arguments:
            self
        """

        self.index = -1

    def append ( self , text ):

        """
        add chars to end of buffer

        arguments:
            self  -
            text  - text to append, string or list of chars
        """

        if not isinstance(text,list):
            text = list(text)            # get new text as list if not already
        if len(self.buffer) > 0:
            if not ellyChar.isWhiteSpace(self.buffer[-1]) and text[0] != ' ':
                self.buffer.append(' ')  # put in space separator if needed
        self.buffer.extend(text)         # add new text

    def prepend ( self , text ):

        """
        put chars at start of buffer

        arguments:
            self  -
            text  - text to prepend, string or list of chars
        """

#       print ( 'prepend=' , text )
        t = text[::-1]              # reverse text
        for c in t:
            self.buffer.insert(0,c) # put in chars at front of buffer
        self._reset()

    def extract ( self , n ):

        """
        take a number of chars from the front of buffer

        arguments:
            self  -
            n     - char count

        returns:
            list of chars
        """

        if n > len(self.buffer):          # too many chars?
            s = [ ]                       # if so, fail
        else:
            s = self.buffer[:n]           # get chars
            self.buffer = self.buffer[n:] # and remove from buffer
        self._reset()
        return s

    def getFound ( self , n=0 ):

        """
        get actual char matched by find methods or n chars past it

        arguments:
            self  -
            n     - how many chars ahead

        returns:
            the char on success, '' otherwise
        """

        if self.index < 0:        # check for previously successful find
            return ''             # if none, return null
        k = self.index + n
        if k >= len(self.buffer): # char is past end of buffer?
            return ''             # if so, return null
        else:
            return self.buffer[k] # return char

    def findSeparator ( self , skip=0 ):

        """
        scan for one of a list of separator chars in buffer

        arguments:
            self  -
            skip  - how many chars to skip in buffer to start scan

        returns:
            offset in buffer if char found, -1 otherwise
        """

        n = len(self.buffer)
        if skip >= n:                         # is skip too long?
            return -1                         # if so, fail

        if skip == 0 and self.buffer[0] == APO:
            return 1                          # special case!

#       print ( 'skip=' , skip, 'n=' , n )
        for k in range(skip,n):
            ck = self.buffer[k]
            if ck in separators:              # is buffer char a separator?
                self.index = k                # if so, note buffer position
                return k
            if ck == ellyChar.COM:
#               print ( 'comma k=' , k )
                if k + 1 < n:
                    ck1 = self.buffer[k+1]
                    if not ellyChar.isLetterOrDigit(ck1):
                        if ck1 in ellyChar.Grk:
                            return k

        return -1                             # fail

    def findBreak ( self ):

        """
        look for next token break in buffer

        arguments:
            self

        returns:
            remaining char count in buffer if no break is found
            otherwise, count of chars to next break if nonzero, but 1 if zero,
        """

        if len(self.buffer) == 0:
            return 0

        if self.buffer[0] == APO:
            return 1

        k = ellyChar.findExtendedBreak(self.buffer)
#       print ( 'findBreak k=' , k )
        if k > 2 and self.buffer[k-1] in [ APO , APX , DQM , RSQ , RDQ , RAB ]:
            k -= 1
        if k > 2 and self.buffer[k-1] in [ APO , APX , COM , DOT ]:
            k -= 1
        self.index = k
#       print ( 'adjusted k=' , k )
        return k

    def match ( self , text ):

        """
        compare chars at offset in buffer with text

        arguments:
            self  -
            text  - string to check

        returns:
            True on match, False otherwise
        """

        l = len(text)

        if len(self.buffer) < l:                 # enough chars for match?
            return False                         # if not, fail immediately
        else:
            return self.buffer[:l] == list(text) # otherwise, return results of comparison

    def skip ( self , n=1 ):

        """
        skip chars in buffer

        arguments:
            self  -
            n     - how many to skip
        """

        if len(self.buffer) >= n:
            self.buffer = self.buffer[n:]
            self._reset()

    def atToken ( self ):

        """
        look for combining token char at start of buffer

        arguments:
            self

        returns:
            True if found, False otherwise
        """

        if len(self.buffer) == 0: return False
        x = self.buffer[0]
        if x == '-' or x == '+': # look for suffix or prefix
            return True
        else:
            return ellyChar.isCombining(self.buffer[0])

    def atSpace ( self ):

        """
        look for space char at start of buffer

        arguments:
            self

        returns:
            True if found, False otherwise
        """

        if len(self.buffer) == 0:
            return False
        else:
            return ellyChar.isWhiteSpace(self.buffer[0])

    def peek ( self ):

        """
        look at next char in buffer without advancing position

        arguments:
            self

        returns:
            char if there is one, otherwise, ''
        """

        if len(self.buffer) > 0:
            return self.buffer[0]
        else:
            return ''

    def next ( self ):

        """
        get next char in buffer at and move ahead

        arguments:
            self

        returns:
            char if there is one, otherwise, ''
        """

        if len(self.buffer) > 0:
            c = self.buffer[0]
#           print ( "c=" , c )
            self.buffer = self.buffer[1:]
            return c
        else:
            return ''

    def count ( self ):

        """
        get number of chars left to scan

        arguments:
            self

        returns:
            char count
        """

        return len(self.buffer)

    def skipSpaces ( self ):

        """
        skip over spaces at start of buffer

        arguments:
            self
        """

        n = len(self.buffer)
        if n == 0: return None
        k = 0
        while k < n:
            if not ellyChar.isWhiteSpace(self.buffer[k]):
                break
            k += 1
        self.buffer = self.buffer[k:]
        self._reset()

    def isCapital ( self ):

        """
        test whether next char in buffer is capitalized

        arguments:
            self

        returns:
            True if so, otherwise False
        """

        if len(self.buffer) == 0:
            return False
        else:
            return self.buffer[0].isupper()

    def setCapital ( self ):

        """
        capitalize next char in buffer, if it is a letter

        arguments:
            self
        """

        if len(self.buffer) > 0:
            self.buffer[0] = self.buffer[0].upper()

    def refill ( self , s ):

        """
        replace contents of buffer with new input chars

        arguments:
            self  -
            s     - list or string of chars to fill with
        """

#       print ( 'refill' , s )
        self.clear()
        self.fill(s)

    def fill ( self , s ):

        """
        add chars after current content of buffer

        arguments:
            self  -
            s     - list or string of chars to fill with
        """

        self.append(self.normalize(s))

    def putBack ( self , w ):

        """
        put a token back into a buffer

        arguments:
            self  -
            w     - token to put back
        """

#       print ( 'put back token=' , w )
        wr = w.getRoot()
        if len(wr) == 0:
            return
        elif wr[-1] in ellyChar.Opn:
            self.prepend(wr)
            return
        elif self.atToken():
            self.prepend(ellyChar.SPC)
        ss = w.getSuffixes()
        if len(ss) > 0:
            self.prepend(' -' + ' -'.join(ss))
#       print ( "putBack@1" , len(self.buffer) )
#       print ( 'buffer=' , self.buffer )
        self.prepend(wr)
#       print ( "putBack@2" , len(self.buffer) )
#       print ( 'buffer=' , self.buffer )
        ps = w.getPrefixes()
        if len(ps) > 0:
            self.prepend('+ '.join(ps) + '+ ')
#       print ( "putBack@3" , len(self.buffer) )

    def getNext ( self ):

        """
        get next token from buffer (this method will be overridden)

        arguments:
            self

        returns:
            a token or None if buffer is empty
        """

        return self.getNextSimple()

    def getNextSimple ( self ):

        """
        get next token from buffer

        arguments:
            self

        returns:
            a token or None if buffer is empty
        """

#       print ( "super",len(self.buffer) )
        w = self._getRaw()
        if w == None:
            return None
#       print ( 'got w=' , str(w) )
#       print ( 'NextSimple' , str(self) )
        return w

    def _getRaw ( self ):

        """
        obtain next raw token from buffer

        arguments:
            self

        returns:
            EllyToken on success, None otherwise
        """

#       print ( '_getRaw() from' , len(self.buffer) , 'chars' )
#       print ( 'before skipping spaces, buffer=' , self.buffer )
        self.skipSpaces()
        ln = len(self.buffer)
#       print ( "after skip=",ln )
        if ln == 0:
            return None

        ## get length of next token and if it has
        ## initial - or +, check for word fragment

#       print ( 'buffer start=' , self.buffer[0] )

        k = 0                   # number of chars for next token

        cz = ' ' if ln == 0 else self.buffer[0]
        if cz in [ MIN , PLS ]:
            k = self.findSeparator(1)
        elif cz == APO:
            if ln > 2 and self.buffer[1].lower() == 's' and self.buffer[2] in separators:
                k = 2
            else:
                k = 1
        elif cz in [ COM , DOT , UELP ]:  # these can be tokens by themselves
            k = 1
        else:
#           print ( 'full token extraction' )
            k = self.findSeparator()
#           print ( 'k=' , k , 'ln=' , ln )
            if k < 0:           # break multi-char token at next separator
                k = ln          # if no separator, go up to end of buffer
            elif k == 0:
                k = 1           # immediate break in scanning
            else:
                while k < ln:       # look at any separator and following context
                    x = self.buffer[k]
                    if x != MIN and x != COM:
                        break       # no further check if separator not hyphen or comma
                    if k + 1 >= ln or not ellyChar.isDigit(self.buffer[k+1]):
#                       print ( 'x=' , x , 'buf=' , self.buffer[k:] )
                        break       # accept hyphen or comma if NOT followed by digit
                    else:           # otherwise, look for another separator
                        k = self.findSeparator(k+2)
                        if k < 0:   #
                            k = ln

        ## if token not delimited, take rest of buffer as
        ## will fit into token working area

        if k < 0: k = ln

#       print ( "take",k,"chars from",len(self.buffer),self.buffer )

        buf = self.extract(k) # get k characters

        ## special check for hyphen next in buffer after extraction

        if self.match(MIN):                    # hyphen immediately following?
            self.skip()                        # if so, take it
            if self.atSpace():                 # when followed by space
                buf.append(MIN)                # append hyphen to candidate token
                k += 1
            else:
                if not self.match(MIN):        # when not followed by another hyphen
                    self.prepend(ellyChar.SPC) # put back a space
                else:
                    self.skip()                # double hyphen = dash
                    self.prepend(ellyChar.SPC) # put back space after dash
                    self.prepend(MIN)          # put back second hyphen
                self.prepend(MIN)              # put back first
                self.prepend(ellyChar.SPC)     # put extra space before hyphen or dash

        ## fill preallocated token for current position from working area

#       print ( "raw text buf=" , buf )

        to = ellyToken.EllyToken(''.join(buf))

#       print ( "EllyBuffer token before=" , str(to) )

        ## strip off trailing non-token chars from token and put back in buffer

        km = k - 1
        while km > 0:
            x = buf[km]
            if ellyChar.isLetterOrDigit(x) or x == MIN or x == PLS or x == UNS:
                break
#           print ( 'trailing x=' , x )
            if x == APO or x == APX:
                if km > 0 and buf[km - 1] == 's':
                    break
            self.prepend(x)
            km -= 1
        km += 1
        if km < k:
            to.shortenBy(k - km,both=True)

#       print ( "EllyBuffer token=" , strx(to) )
#       print ( "next in buffer=" , self.buffer )
        return to

#
# unit test
#

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        test = [  # lines
            "'oops,'" ,
            'The aa vv.  We xx "yy" zz ee?  A U.S. resp wil do!' ,
            'more stuff.' ,
            'ff, gg, hh' ,
            '\u00c0\u00c1\u00c2 \u265e' ,
            'QQQQ' ,
            'zz\'s yy' ,
            '`DUM\'' ,
            'wh (123 456)' ,
            'aa-bb-cc' ,
            ellyChar.RS + 'www xxx' ,
            'sh*t' ,
            'xxx\u2122'
        ]
    else:
        test = [ ]
        try :
            inp = open(sys.argv[1],"r")
            while True:
                dat = inp.readline( )
                if len(dat) == 0: break
                test.append(dat.strip())
            inp.close()
        except IOError as e:
            print ( e , file=sys.stderr )
            sys.exit(1)

    eb = EllyBuffer()     # create an empty buffer

#   fill buffer with test data

    print ( len(test) , 'lines of input' )
    for r in test:
        print ( eb.count() , 'chars + [' + r + ']' )
        eb.append(r)
    print ( '------------' )
    print ()

    print ( 'getting text elements' )

    while eb.count() > 0: # extract consecutive text elements from buffer

        tkn = eb.getNext()
        if tkn == None: break
        print ( 'extract <' + ''.join(tkn.root) + '> ' , str(tkn) )
