#!/usr/bin/python3
# PyElly - rule-basee tool for analyzing natural language (Python v3.8)
#
# ellyDefinitionReader.py : 16nov2019 CPM
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
approximate a Java Reader class on UTF-8 text with cleanup of input
to remove blank lines and comments
"""

import sys
import codecs
import ellyChar

Slash = '\\'         # for escaping
Nul   = '\x00'       # ASCII NUL
RS    = ellyChar.RS  # ASCII RS control char

class EllyDefinitionReader(object):

    """
    read Elly input lines transparently from various types of UTF-8 sources
    with simple reformatting and stripping off comments

    attributes:
        buffer - for input lines
        error  - note exception
        trim   - remove leading and trailing white space?
    """

    def __init__ ( self , source=None , trim=True ):

        """
        set up virtual input stream

        arguments:
            self  -
            source- string list or file name
        """

        self.buffer = [ ] # for input text lines
        self.error = None
        self.trim = trim
        if source != None:
            self.assign(source)

    def _rems ( self , os ):

        """
        remove extra spaces

        arguments:
            self  -
            os    - original string

        returns:
            string without extra spaces
        """

        if not self.trim:
            return os
        ns = ''
        while True:
            k = os.find('  ')
            if k < 0: break
            ns += os[:k+1]
            os = os[k:].strip()
        ns += os
        return ns

    def save ( self , line ):

        """
        clean up input line and put into buffer if result is not empty

        arguments:
            self  -
            line  - UTF-8 string
        """

#       print ( 'len=' , len(line) , '[' , list(line) , ']' )
        if len(line) <= 1:             # definition lines should be nonempty
            return
        start = line[:2]
        if ( start == '# '  or         # filter out comment lines starting
             start == '#\r' or         # with "# " or consisting only of
             start == '#\n' ):         # "#" and "\r" or "\n" following and
            return
        if line[-2:] == ' #':
            line = line[:-1]           # drop "#" at the end of a line after space
        else:
            k = line.rfind(' # ')      # from the LAST " # " in a line
            if k >= 0: line = line[:k] # treat as comment
#       print ( 'line=' , line )

        le = line.strip()
        line = ''
        while len(le) > 0:
            k = le.find(Slash)         # look for \
            if k < 0:
                line += self._rems(le) # if none found, keep everything left
                break
            line += self._rems(le[:k]) # copy over everything up to found \
            le = le[k+1:]              # go past \
#           print ( 'le=' , le )
            if len(le) == 0:
                line += Slash          # final \ on line is kept
                break
            elif le[0] == Slash:
                line += Slash          # double \ becomes single \
                le = le[1:]
            elif le[0] == '0':
                line += Slash          # keep \0
            elif le[0] == 's':
                line += ellyChar.RS    # special separator char for input

        if len(line) > 0:
            self.buffer.append(line)   # add line to input

    def assign ( self , source ):

        """
        set up input buffer

        arguments:
            self  -
            source- string list or file name
        """

#       print ( "assign ", source )

        if isinstance(source,list):

#           print ( "from list of text lines" )

            for l in source:
                if isinstance(l,str):
                    self.save(l)  # fill buffer from list

        else:

#           print ( "from file" )

            try:
                inpt = codecs.open(source,"r","utf-8") # open UTF-8 file to get text
#               print ( inpt )
            except IOError as e:
                self.error = e
                return

            try:
                while True:
                    ls = inpt.readline()
#                   print ( '++ ', ls.strip(), '=' , len(ls) , type(ls) )
                    if len(ls) == 0: break          # EOF check
                    if len(ls) == 1: continue       # skip lines with only "\n"
                    self.save(ls)                   # add line to input
            except IOError as e:
                self.error = e

            inpt.close()      # close file after filling buffer

    def readline ( self ):

        """
        simulate function for standard input and file input

        arguments:
            self

        returns:
            next line in input as string on success or empty string on end of input
        """

        if len(self.buffer) == 0:
            return ""
        else:
            return self.buffer.pop(0)

    def unreadline ( self , line ):

        """
        put line back in input

        arguments:
            self  -
            line  - line to return
        """

        self.buffer.insert(0,line)

    def linecount ( self ):

        """
        get number of lines left to read

        arguments:
            self  -

        returns:
            current line count
        """

        return len(self.buffer)

    def dump ( self ):

        """
        show current contents of buffer for debugging
        with armoring for possible Unicode issues

        arguments:
            self  -
        """

        out = sys.stderr
        for b in self.buffer:
            out.write('{0:3d}'.format(len(b)))
            out.write(str(type(b)))
            b = encode(b)
            try:
                out.write('[' + b + ']')
            except UnicodeEncodeError:
                out.write('[**!**]')
            out.write('\n')

def encode ( s ):

    """
    encode special control chars for printing

    arguments:
        s  - string

    returns:
        encoded string
    """

    while True:
        n = s.find(RS)
        if n < 0: break
        s = s[:n] + '\\s' + s[n+1:]
    return s

#
# unit test
#

if __name__ == "__main__":

    unicodetext = [        # each string in array  must be Unicode!
        '6bcdef\\\\gh' ,   # encodes \\
        '0bcdefgh'   ,
        '1bcdefgh\n' ,
        '2bcdef\\gh' ,     # note: \ must be entered as \\ in Python strings
        '#3bcdefgh'  ,
        '4bcdefgh #xxx'  ,
        '5bcdefgh\\#xxx' , # encodes \
        'a\x00a' ,
        ''    ,
        '    ',
        '#   ',            # comment
        '#'   ,            # comment
        '##  ',            # not comment
        '    ##' ,         # not comment
        'xx ' + chr(0x6211) + chr(0x5011) + ' # Chinese Unicode' ,
        chr(0x00e9) + 't'   + chr(0x00e9) + ' # Latin-1 Unicode' ,
        '[-]&#[.]#*       num' ,
        '#\r\n' ,
        '#\n'   ,
        '\n'    ,
        ' ' + RS + ' tha'  # special PyElly separator to break up input
    ]  # default test input

    src = sys.argv[1] if len(sys.argv) > 1 else unicodetext
    inp = EllyDefinitionReader(src)
    if inp.error != None:
        print ( "error exit" )
        sys.exit(1)
    inp.dump()
    print ( '----' )
    while True:
        ll = inp.readline()
        if len(ll) == 0: break
        ln = len(ll)
        print ( ">>[" + encode(ll) + "]" , ln )
