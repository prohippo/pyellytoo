#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (Python v3.8)
#
# cognitiveProcedure.py : 14nov2019 CPM
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
procedure to determine plausibility of phrase in Elly parse
"""

import sys
import ellyBits
import semanticCommand
import cognitiveDefiner
import ellyException

class CognitiveProcedure(object):

    """
    cognitive semantic procedure attached to grammar rule

    attributes:
        logic   - code and data for procedure
    """

    def __init__ ( self , syms , defn , nwy=0 ):

        """
        initialization from EllyDefinitionReader input

        arguments:
            self  -
            defn  - EllyDefinitionReader
        """

        self.logic = cognitiveDefiner.convertDefinition(syms,defn,nwy)

    def score ( self , cntx , phrs ):

        """
        compute plausibility score

        arguments:
            self  -
            cntx  - interpretive context
            phrs  - associated phrase

        returns:
            integer plausibility score
        """

        if self.logic == None: return 0
#       print ( 'cognitive scoring: phrs=' , phrs )

        trce = False           # enable diagnostic tracing
        clno = 0               # clause index
        psum = 0               # to accumulate plausibility score

        for cls in self.logic: # go through all clauses

            clno += 1
#           print ( 'clno=' , clno )
            for p in cls[0]:   # go through all predicates of clause
                op = p[0]
#               print ( 'cog sem op=' , op )
                if op == semanticCommand.Ctrc:
                    print ( '  at phrase' , phrs.krnl.seqn , ': rule=' , phrs.krnl.rule.seqn , end=' ' , file=sys.stderr )
                    print ( 'with current bias= ' , phrs.krnl.rule.bias , file=sys.stderr )
                    print ( '  l:' , phrs.krnl.lftd , file=sys.stderr )
                    print ( '  r:' , phrs.krnl.rhtd , file=sys.stderr )
                    print ( ' ' , phrs.ntok , 'token(s) spanned' , end=' ' , file=sys.stderr )
                    print ( '@' + str(phrs.krnl.posn) , file=sys.stderr )
                    print ( file=sys.stderr )
                    trce = True
                    break
                elif op == semanticCommand.Clftf or op == semanticCommand.Crhtf:
                    # test features of descendants
#                   print ( 'op=' , p , file=sys.stderr )
                    if phrs.krnl.lftd == None: break
#                   print ('lftd=' , phrs.krnl.lftd.krnl.seqn , file=sys.stderr )
                    dph = ( phrs.krnl.lftd if op == semanticCommand.Clftf or phrs.krnl.rhtd == None
                            else phrs.krnl.rhtd )
#                   print ( 'dph=' , dph , file=sys.stderr )
                    bts = dph.krnl.semf.compound()
#                   print ( 'bts=' , bts , file=sys.stderr )
#                   print ( 'cnd=' , p[1] , file=sys.stderr )
                    if not ellyBits.check(p[1],bts): break
                elif op == semanticCommand.Clftc or op == semanticCommand.Crhtc:
                    # check concepts of descendants
                    if phrs.krnl.lftd == None: break
                    if cntx == None:
                        print ( '  no context for conceptual hierarchy'  , file=sys.stderr )
                        break
                    dph = ( phrs.krnl.lftd if op == semanticCommand.Clftc or phrs.krnl.rhtd == None
                            else phrs.krnl.rhtd )
                    cnc = dph.krnl.cncp
                    cx = p[1]  # concepts to check against
                    mxw = -1
                    mxc = None
                    for c in cx:
                        w = cntx.wghtg.hiery.isA(cnc,c)
                        if mxw < w:
                            mxw = w
                            mxc = c
                    if mxw < 0: break
                    cntx.wghtg.noteConcept(mxc)
                elif op == semanticCommand.Cngt or op == semanticCommand.Cnlt:
                    # check token count of evaluated phrase
                    nt = phrs.ntok
                    nm = p[1]
                    if op == semanticCommand.Cngt:
                        if nt <= nm: break
                    else:
                        if nt >= nm: break
                elif op == semanticCommand.Cpgt or op == semanticCommand.Cplt:
                    # check position of evaluated phrase
                    po = phrs.krnl.posn
                    nm = p[1]
#                   print ( 'po=' , po , 'nm=' ,nm )
                    if op == semanticCommand.Cpgt:
                        if po <= nm: break
                    else:
                        if po >= nm: break
#                   print ( 'no break' )
                elif op == semanticCommand.Ccgt or op == semanticCommand.Cclt:
                    # check token count of evaluated phrase
                    nc = phrs.lens
                    nm = p[1]
                    if op == semanticCommand.Ccgt:
                        if nc <= nm: break
                    else:
                        if nc >= nm: break
                else:
                    # unknown command
                    print ( 'bad cog sem action=' , op , file=sys.stderr )
                    break

            else:             # execute actions of clause if ALL predicates satisfied
                if trce:
                    ncls = len(self.logic)
                    print ( '  cog sem at clause' , clno , 'of' , ncls , file=sys.stderr )
#                   print ( '   =' , cls[1] , file=sys.stderr )
                    print ( file=sys.stderr )
                for a in cls[1]:                      # get next action
                    op = a[0]
                    if op == semanticCommand.Cadd:    # add to score?
                        psum += a[1]
                    elif op == semanticCommand.Csetf: # set   semantic features?
                        phrs.krnl.semf.combine(a[1])
                    elif op == semanticCommand.Crstf: # reset semantic features?
                        phrs.krnl.semf.reset(a[1])
                    elif op == semanticCommand.Csetc: # set concepts?
                        phrs.krnl.cncp = a[1]
                    elif phrs.krnl.lftd == None:
                        pass
                    elif op == semanticCommand.Clhr:  # inherit from left descendant?
                        phrs.krnl.semf.combine(phrs.krnl.lftd.krnl.semf)
                        phrs.krnl.cncp = phrs.krnl.lftd.krnl.cncp
                    elif op == semanticCommand.Crhr:  # inherit from right?
                        dsc = phrs.krnl.rhtd if phrs.krnl.rhtd != None else phrs.krnl.lftd
                        phrs.krnl.semf.combine(dsc.krnl.semf)
                        phrs.krnl.cncp = dsc.krnl.cncp
#                   if trce:
#                       print ( '->' , phr.krnl.semf , file=sys.stderr )

                break  # ignore subsequent clauses on taking action

        inc = 0                  # compute conceptual contribution
        rwy = phrs.krnl.rule.nmrg
#       print ( 'conceptual plausibility' , file=sys.stderr )
        if rwy == 2:             # 2-branch splitting rule?
#           print ( '2-branch!' )
            inc = cntx.wghtg.relateConceptPair(phrs.krnl.lftd.krnl.cncp,phrs.krnl.rhtd.krnl.cncp)
#           print ( phrs.krnl.lftd.krnl.cncp , ':' , phrs.krnl.rhtd.krnl.cncp , '=' , inc , '!' , file=sys.stderr )
            if inc > 1:
                phrs.krnl.ctxc = cntx.wghtg.getIntersection()
#           print ( '2-way bias incr=' , inc , file=sys.stderr )
        elif phrs.krnl.lftd != None:  # 1-branch extending rule?
#           print ( '1-branch!' , file=sys.stderr )
            dst = cntx.wghtg.interpretConcept(phrs.krnl.lftd.krnl.cncp)
            if dst > 0:
                phrs.krnl.ctxc = cntx.wghtg.getIntersection()
                inc = 1
#           print ( '1-way bias incr=' , inc , file=sys.stderr )
        if inc > 0: psum += inc  # only positive increments contribute
#       print ( 'phrase' , phrs.krnl.seqn, 'intersect=' , phrs.krnl.ctxc , file=sys.stderr )

        if trce:
            print ( '  raw plausibility=' , phrs.krnl.bias , file=sys.stderr )
            print ( '  adjustment=' , psum , end=' ' , file=sys.stderr )
            print ( 'sem[' + phrs.krnl.semf.hexadecimal() + ']' , file=sys.stderr )
            print ( file=sys.stderr )
        return psum

#
# unit test
#

if __name__ == '__main__':

    import ellyDefinitionReader
    import procedureTestFrame

    default = [    # expects procedureTestFrame definitions
        "?>>?" ,
        "p>10000 >> +100" ,
        "l[!f0,f1]>>*l[!f3] XXXX" ,
        "l(YYYY)  >>+1" ,
        "n>2>>-1" ,
        ">>*l[!f3,-f4,-one]-2" ,
        "c<4>>+2"
    ]

    frame = procedureTestFrame.ProcedureTestFrame()
    phr = frame.phrase
    ctx = frame.context
    stb = ctx.syms

    src = sys.argv[1] if len(sys.argv) > 1 else default
    inp = ellyDefinitionReader.EllyDefinitionReader(src)
    if inp.error != None:
        sys.exit(1)
    try:
        cgs = CognitiveProcedure(stb,inp)
    except ellyException.FormatFailure:
        print ( "cognitive semantic conversion error" , file=sys.stderr )
        sys.exit(1)

    cognitiveDefiner.showCode(cgs.logic)

    print ( 'phr=' , phr )
    s = cgs.score(ctx,phr)
    print ( 'plausibility=' , s )
