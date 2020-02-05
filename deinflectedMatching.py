#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# deinflectedMatching.py : 02feb2020 CPM
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
for matching irrespective of English inflectional endings -S, -ED, and -ING in
a few simple cases for input stream token extraction
"""

import ellyChar

APOs = [ ellyChar.APO , ellyChar.APX ]   # apostrophes
EMBs = [ '.' , '/' ]                     # embedded punctuation short list

def terminate ( spc , npc ):

    """
    check char for termination of match range
    arguments:
        spc  - current char in stream
        npc  - next char in stream
    returns:
        True if current char terminates, False otherwise
    """

#   print ( "terminate:" , '<' + spc + '>' , '<' + npc + '>' )
    tm = False
    if spc in EMBs:
        if npc in EMBs:
            tm = True
    elif spc in APOs or ellyChar.isLetterOrDigit(spc):
        pass
    else:
        tm = True
#   print ( 'tm=' , tm )
    return tm

def icmpr ( cc , tc ):

    """
    compare text against string with case insensitivity

    arguments:
        cc    - chars to compare
        tc    - text chars

    returns:
        0 on match, n if mismatch at n chars before end, -1 if unmatched
    """

    k = len(cc)
    n = len(tc)
    if k > n: return -1
    if k == 0: return n
    for i in range(k):
        if cc[i].lower() != tc[i].lower(): return k - i
    return 0

class DeinflectedMatching(object):

    """
    define simple matching with simple deinflection for
    inheritance by a child class

    attributes:
        endg   - any ending removed for match
    """

    def __init__ ( self ):

        """
        initialization

        arguments:
            self
        """

        self.endg = ''

    def simpleDeinflection ( self , ss , ssp , ssl , mr ):

        """
        handle matching of certain forms of English inflectional endings
        (override this method appropriately for other languages)

        arguments:
            self -
            ss   - input string of chars to scan for match
            ssp  - current position in input string
            ssl  - limit of matching in input
            mr   - list of chars to look for next in input

        returns:
            inflection char count >= 0 on match, -1 otherwise
        """

#       print ( 'simpleDeinflection' , 'ssp=' , ssp , 'ssl=' , ssl )
        self.endg = ''       # null inflection by default
        if len(mr) == 0 and ssp == ssl:
            return 0
        if ssp < 2 or ss[ssp-2] == ' ':
            return -1
        ts = ss[ssp:]             # where to look for inflection
        mc = ss[ssp-1]            # last char matched
        lm = len(mr)
#       print ( ts , 'mc=' , mc , 'mr=' , mr )
        if not ellyChar.isLetter(mc):
            return -1
        dss = ssl - ssp           # count up extra input chars#
#       print ( 'dss=' , dss )
        if dss == 0:              # no more chars in input
            if lm == 0:           # check for exact match
                return 0
        elif dss == 1:            # just one char left in input
            if lm != 0:           # make sure all of pattern matched
                return -1
            elif ts[0] in APOs:
                if mc == 's':     # case of S'
                    self.endg = "-'s"
                    return 1
                else:
                    return 0
            elif ts[0].lower() == 's':
                self.endg = '-s'  # assume extra input S is for plural
                return 1
            elif mc == 'e' and ts[0].lower() == 'd':
                self.endg = '-ed' # an E was last matched char
                return 1
            elif ts[0] == '.':
                return 0          # but no inflection
        elif dss == 2:            # 2 extra chars
#           print ( 'ts=' , ts )
            if lm == 0:
                if ts[0].lower() == 'e':
                    if ts[1].lower() == 'd':
                        self.endg = '-ed' # E and D must be inflection
                        return 2
                    elif ts[1].lower() == 's':
                        self.endg = '-s'  # assume E is extra
                        return 2
                elif ts[0] in APOs and ts[1].lower() == 's':
#                   print ( "ending -'s" )
                    ss[ssp] = "'"         # normalization just in case
                    self.endg = "-'s"
                    return 2
                elif ts[1] in APOs and ts[0].lower() == 's':
#                   print ( "endings -s and -'s" )
                    ss[ssp]   = "'"       # reverse letters in next input
                    ss[ssp+1] = "s"       #
                    self.endg = '-s'
                    return 0
        elif dss == 3:       # 3 extra chars
#           print ( 'ts=' , ts , 'mr=' , mr )
            if ts[0].lower() == 'i':
                if ts[1].lower() == 'e':
                    if lm == 1 and mr[0] == 'y':
                        if ts[2].lower() == 's':
                            self.endg = '-s'
                            return 3
                        elif ts[2].lower() == 'd':
                            self.endg = '-ed'
                            return 3
                elif ts[1].lower() == 'n' and ts[2].lower() == 'g':
                    if lm == 0 or lm == 1 and mr[0] == 'e':
                        self.endg = '-ing'
                        return 3
            if lm == 0 and ts[0].lower() == mc and ts[1].lower() == 'e' and ts[2].lower() == 'd':
                self.endg = '-ed'
                return 3
        elif dss == 4:       # 4 extra chars
            if lm == 0 and ts[0].lower() == mc and ts[1] == 'i' and ts[2].lower() == 'n' and ts[3].lower() == 'g':
                self.endg = '-ing'
                return 4
            if ts[0].lower() == 'y' and ts[1].lower() == 'i' and ts[2].lower() == 'n' and ts[3].lower() == 'g':
                if lm == 2 and mr[0] == 'i' and mr[1] == 'e':
                    self.endg = '-ing'
                    return 4

        return -1    # extra chars not inflection

    def doMatchUp ( self , ccs , txs ):

        """
        match current text with vocabulary entry, possibly removing final inflection
        (this method assumes English; override it for other languages)

        arguments:
            self  -
            ccs   - chars for comparison
            txs   - text chars to be matched

        returns:
            count of txs chars matched, 0 on mismatch
        """

#       print ( 'match up ccs=' , ccs , 'txs=' ,txs )
        self.endg = ''                       # default inflection
        lcc = len(ccs)                       # comparison pattern
        ltx = len(txs)                       # input text chars
        if lcc == 0 or ltx < lcc: return 0

        nr = icmpr(ccs,txs)                  # do match on lists of chars
#       print ( 'nr=' , nr )

        if lcc < 4 and nr > 0:               # no stemming on short words
            return 0

#       try inflectional stemming to realize a match here,
#       but with abbreviated logic

        m = lcc - nr              # how many comparison chars matched so far
        k = m                     # get extent of text to look for termination
        nxtc = txs[m] if m < ltx else ' '
        while nxtc != ' ':
            curc = nxtc
            nxtc = txs[k+1] if k + 1 < ltx else ' '
            if terminate(curc,nxtc):
                break             # find current end of text to match
            k += 1

#       print ( 'k=' , k , 'm=' , m )

        ns = self.simpleDeinflection(txs,m,k,ccs[m:])

#       print ( 'ns=' , ns , 'm=' , m , ccs[m:] , txs[m:] )

        return 0 if nr > ns or m + ns < lcc else m + ns

#
# unit test
#

import sys

if __name__ == '__main__':

    tstg = [  # default examples
        'xxxxXY'  ,
        'xxxxxy’S',
        'xxxxxyS’',
        'xxxxxyS’S',
        'xxxxxyES’S',
        'xxxxxyS' ,
        'xxxxxyES',
        'xxxxxIED',
        'xxxxxyED'  ,
        'xxxxxIES'  ,
        'xxxxxyyED' ,
        'xxxxxyING' ,
        'xxxxxxyING',
        'xxx xyED'  ,
        'xxx xyS'   ,
        'xxx xyZ'
    ]

    L = 6   # where to divide for a match in default testing

    dm = DeinflectedMatching()

    if len(sys.argv) > 2:         # test a single specific matching
        cxs = list(sys.argv[1])   # comparison string
        ssb = list(sys.argv[2])   # text string to match
        print ( 'comparing' , ssb , '|' , ''.join(cxs) )
        adv = dm.doMatchUp(cxs,ssb)
        print ( 'advancing' , adv , ', removed {0}'.format(dm.endg) if dm.endg != '' else '' )
        sys.exit(0)

    for s in tstg:                # or test all default examples
        ssb = list(s.lower())     # get next text
        cxs = list(ssb[:L])       # comparison string is always first L chars!
        if cxs[-1] == 'i':
            cxs[-1] = 'y'         # restore spelling
        elif ssb[L-1:L+1] == 'yi':
            cxs[-1] = 'i'
            cxs.append('e')       # restore spelling
        print ( 'comparing' , ssb , '|' , ''.join(cxs) )
        adv = dm.doMatchUp(cxs,list(ssb))
        print ( 'advancing' , adv , ', removed {0}'.format(dm.endg) if dm.endg != '' else '' )
        print ()
