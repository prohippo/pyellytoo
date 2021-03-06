#!/usr/bin/python3
# PyElly - rule-based tool for analyzing natural language (python v3.8)
#
# semanticCommand.py : 10nov2019 CPM
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
define operation codes for Elly cognitive and generative semantic procedures
"""

#### cognitive

Cadd  =   0  # add contribution to total score
Clhr  =   1  # inherit left
Crhr  =   2  #         right
Csetf =   3  # set   features
Crstf =   4  # reset features
Clftf =   5  # test left descendant features
Crhtf =   6  #      right
Csetc =   7  # set concept
Clftc =   8  # test left descendant concepts
Crhtc =   9  #      right
Ctrc  =  10  # trace
Cngt  =  11  # test n > token count
Cnlt  =  12  #      n <
Cpgt  =  13  # test p > position
Cplt  =  14  #      p <
Ccgt  =  15  # test c > char count
Cclt  =  16  #      c <

Copn = [     # operation names for dumping (must align with numerical codes above)
    'ADDN' , 'LHER' , 'RHER' , 'SETF' , 'RSTF' , 'LFTF' , 'RHTF' , 'SETC' , 'LFTC' ,
    'RHTC' , 'TRCE' , 'NGTR' , 'NLSS' , 'PGTR' , 'PLSS' , 'CGTR' , 'CLSS'
]

#### generative

Gnoop =  0  # do nothing
Gretn =  1  # return successfully
Gfail =  2  # return unsuccessfully
Gleft =  3  # run left  subconstituent
Grght =  4  #     right
Gblnk =  5  # insert space
Glnfd =  6  # insert \r\n
Gsplt =  7  # split off new output buffer
Gback =  8  # go back to preceding buffer
Gmrge =  9  # merge current buffer with newer ones
Gchng = 10  # move new buffer to current with substitutions
Gchck = 11  # check local variable
Gnchk = 12  # negated check of local variable
Gchkf = 13  # check semantic features
Gskip = 14  # for unconditional branch
Gvar  = 15  # define local variable
Gset  = 16  # set    local variable
Gpeek = 17  # get char from current or next buffervariable without changing buffer
Gextl = 18  # extract chars from buffer
Gextr = 19  # extract chars from next buffer
Ginsn = 20  # insert local variable into next buffer
Ginsr = 21  # insert local variable into buffer
Gshft = 22  # move n chars between buffers
Gdele = 23  # delete n chars in buffer
Gdelt = 24  # delete chars in buffer to substring
Gstor = 25  # store deletion in local variable
Gfnd  = 26  # find substring
Galgn = 27  # align to start of line
Gpick = 28  # special table lookup and insertion
Gappd = 29  # append string to buffer
Gget  = 30  # set local  variable from global variable
Gput  = 31  # set global variable from local  variable
Gassg = 32  # assign value of local variable to another
Gque  = 33  # use local variable as a character queue
Gunio = 34  # set union
Gintr = 35  # set intersection
Gcomp = 36  # set complement
Gobtn = 37  # obtain original text for token
Gcapt = 38  # capitalize first char in buffer
Gucpt = 39  # uncapitalize first char in buffer
Gtrce = 40  # instrumented no op for debugging
Gshow = 41  # see local variable for debugging
Gview = 42  # see parts of current and next buffer
Gproc = 43  # call procedure

Gerr  = 99  # error return value

Glen = {    # command lengths used in dumping generative procedures
    Gnoop : 1 ,
    Gretn : 1 ,
    Gfail : 1 ,
    Gleft : 1 ,
    Grght : 1 ,
    Gblnk : 1 ,
    Glnfd : 1 ,
    Gsplt : 1 ,
    Gback : 1 ,
    Gmrge : 1 ,
    Gchng : 3 ,
    Gchck : 4 ,
    Gnchk : 4 ,
    Gchkf : 3 ,
    Gskip : 2 ,
    Gvar  : 3 ,
    Gset  : 3 ,
    Gpeek : 3 ,
    Gextl : 3 ,
    Gextr : 3 ,
    Ginsr : 2 ,
    Ginsn : 2 ,
    Gshft : 2 ,
    Gdele : 2 ,
    Gdelt : 3 ,
    Gstor : 3 ,
    Gfnd  : 3 ,
    Galgn : 2 ,
    Gpick : 3 ,
    Gappd : 2 ,
    Gget  : 3 ,
    Gput  : 3 ,
    Gassg : 3 ,
    Gque  : 4 ,
    Gunio : 3 ,
    Gintr : 3 ,
    Gcomp : 3 ,
    Gobtn : 1 ,
    Gcapt : 1 ,
    Gucpt : 1 ,
    Gtrce : 1 ,
    Gshow : 3 ,
    Gview : 2 ,
    Gerr  : 1 ,
    Gproc : 2
}

Gopn = [    # operation names for dumping (must align with 44 numerical codes above)
    'PASS' , 'RETN' , 'FAIL' , 'LEFT' , 'RGHT' , 'BLNK' ,
    'LNFD' , 'SPLT' , 'BACK' , 'MRGE' , 'CHNG' , 'CHCK' ,
    'NCHK' , 'CHKF' , 'SKIP' , 'DEFV' , 'SETV' , 'PEEK' ,
    'EXTL' , 'EXTR' , 'INSN' , 'INSR' , 'SHFT' , 'DELE' ,
    'DLTO' , 'STOR' , 'FIND' , 'ALGN' , 'PICK' , 'APPD' ,
    'GETG' , 'PUTG' , 'ASSG' , 'QUEU' , 'UNIO' , 'INTR' ,
    'COMP' , 'OBTN' , 'CAPT' , 'UCPT' , 'TRCE' , 'SHOW' ,
    'VIEW' , 'CALL'
]
