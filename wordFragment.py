#!/usr/bin/python3
# Code for extending PyElly capabilities
#
# wordFragment.py : 03jun2021 CPM
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
basic n-gram extraction for finite indexing of text
"""

#
# hard-wired n-gram tables
# (edit to define an n-gram index set)
#

s2Gm = [  # 2-gram seeds for 3-gram indices
    "ab", "ac", "ad", "af", "ag", "ai", "al", "am",
    "an", "ap", "ar", "as", "at", "au", "av", "aw",
    "ba", "be", "bi", "bl", "bo", "br", "bu", "ca",
    "cc", "ce", "ch", "ci", "ck", "cl", "co", "cr",
    "ct", "cu", "da", "de", "di", "do", "dr", "du",
    "ea", "eb", "ec", "ed", "ee", "ef", "eg", "ei",
    "el", "em", "en", "eo", "ep", "er", "es", "et",
    "ev", "ex", "fa", "fe", "ff", "fi", "fl", "fo",
    "fr", "fu", "ga", "ge", "gh", "gi", "gl", "go",
    "gr", "gu", "ha", "he", "hi", "ho", "hu", "ia",
    "ib", "ic", "id", "ie", "if", "ig", "ik", "il",
    "im", "in", "io", "ir", "is", "it", "iv", "ja",
    "je", "jo", "ju", "ke", "ki", "la", "le", "li",
    "ll", "lo", "lt", "lu", "ma", "mb", "me", "mi",
    "mm", "mo", "mp", "mu", "na", "nc", "nd", "ne",
    "nf", "ng", "ni", "nn", "no", "ns", "nt", "nu",
    "nv", "oa", "ob", "oc", "od", "of", "og", "oi",
    "ol", "om", "on", "oo", "op", "or", "os", "ot",
    "ou", "ov", "ow", "pa", "pe", "ph", "pi", "pl",
    "po", "pp", "pr", "pu", "qu", "ra", "rc", "rd",
    "re", "rg", "ri", "rl", "rm", "rn", "ro", "rr",
    "rs", "rt", "ru", "rv", "sa", "sc", "se", "sh",
    "si", "sl", "so", "sp", "ss", "st", "su", "ta",
    "te", "th", "ti", "tl", "to", "tr", "tt", "tu",
    "ua", "ub", "uc", "ud", "ue", "ug", "ui", "ul",
    "um", "un", "up", "ur", "us", "ut", "va", "ve",
    "vi", "vo", "wa", "we", "wi", "wo", "xp", "ye"
]

x4Gm =  [  # selected 4-gram indices
    'ache', 'anti', 'appr', 'atta', 'band', 'bank', 'batt', 'bill', 'book', 'camp',
    'ceiv', 'cept', 'cert', 'cham', 'cien', 'conc', 'conf', 'conv', 'core', 'cost',
    'cove', 'cula', 'cult', 'deal', 'demo', 'desi', 'dest', 'disc', 'divi', 'driv',
    'earn', 'eath', 'eave', 'ecre', 'eigh', 'equi', 'erve', 'esca', 'face', 'fact',
    'fall', 'fect', 'film', 'fire', 'foll', 'foot', 'free', 'gest', 'give', 'gram',
    'grow', 'hamp', 'happ', 'hard', 'heat', 'help', 'hold', 'hone', 'idea', 'impl',
    'impr', 'indu', 'isla', 'itch', 'ject', 'kill', 'lean', 'lete', 'life', 'love',
    'lude', 'majo', 'meet', 'mili', 'mine', 'mini', 'moun', 'muni', 'musi', 'nage',
    'ndle', 'ngle', 'note', 'nsti', 'nstr', 'oach', 'offe', 'olve', 'omen', 'ompl',
    'onde', 'oney', 'open', 'ounc', 'pani', 'para', 'park', 'pass', 'past', 'pose',
    'post', 'prin', 'pris', 'prob', 'prof', 'prom', 'prop', 'prot', 'quar', 'ques',
    'quir', 'race', 'rade', 'rage', 'rear', 'refe', 'rele', 'reli', 'remo', 'rict',
    'road', 'room', 'rove', 'scou', 'seri', 'shad', 'shar', 'spar', 'spri', 'stop',
    'sult', 'tack', 'tech', 'temp', 'tend', 'terr', 'tour', 'town', 'trad', 'trib',
    'trol', 'urch', 'urse', 'velo', 'vict', 'view', 'vill', 'wash', 'writ', 'xper',
    'able', 'aint', 'allo', 'ally', 'ance', 'ange', 'appe', 'arch', 'area', 'arge',
    'arri', 'arti', 'ason', 'aste', 'atch', 'ater', 'atin', 'atio', 'atte', 'ause',
    'back', 'ball', 'base', 'butt', 'call', 'care', 'caus', 'cent', 'cess', 'chan',
    'char', 'choo', 'city', 'coll', 'come', 'comm', 'comp', 'cond', 'cons', 'cont',
    'cord', 'coun', 'cour', 'crea', 'dent', 'diff', 'dist', 'down', 'each', 'eart',
    'ease', 'easo', 'east', 'econ', 'ecor', 'edit', 'elec', 'embe', 'ente', 'enti',
    'entr', 'epar', 'epre', 'eral', 'erse', 'esti', 'estr', 'eter', 'evel', 'even',
    'ever', 'expe', 'ffer', 'fina', 'forc', 'fore', 'form', 'fort', 'fter', 'gain',
    'game', 'gene', 'good', 'gree', 'grou', 'hand', 'head', 'heal', 'hear', 'heir',
    'hero', 'high', 'hist', 'home', 'icat', 'ight', 'inge', 'inst', 'inte', 'iste',
    'istr', 'itio', 'itis', 'iver', 'just', 'king', 'know', 'lace', 'land', 'last',
    'late', 'lati', 'lead', 'lear', 'leas', 'lect', 'line', 'lion', 'list', 'live',
    'llow', 'loca', 'long', 'look', 'main', 'make', 'mand', 'mark', 'mate', 'mber',
    'mean', 'medi', 'ment', 'meth', 'miss', 'mont', 'more', 'move', 'mple', 'name',
    'nati', 'nder', 'need', 'nter', 'ntin', 'offi', 'ogra', 'onst', 'ontr', 'oper',
    'orth', 'othe', 'ough', 'ound', 'ount', 'ouse', 'outh', 'over', 'part', 'pect',
    'peri', 'pers', 'plac', 'plan', 'play', 'poin', 'poli', 'port', 'pres', 'prov',
    'ract', 'ranc', 'rand', 'rate', 'rati', 'read', 'real', 'reas', 'rece', 'reco',
    'redi', 'rent', 'resi', 'ress', 'rest', 'ring', 'rive', 'roun', 'sand', 'scho',
    'seas', 'sent', 'serv', 'seve', 'ship', 'show', 'side', 'sign', 'sist', 'soci',
    'soft', 'spec', 'star', 'stat', 'ster', 'stor', 'stra', 'stre', 'stri', 'stru',
    'stud', 'supp', 'sure', 'tabl', 'tain', 'take', 'tall', 'tate', 'team', 'tent',
    'term', 'test', 'ther', 'time', 'tion', 'tore', 'tory', 'trac', 'tran', 'trea',
    'tric', 'tter', 'ttle', 'ture', 'turn', 'unde', 'unit', 'vent', 'vers', 'vert',
    'vest', 'vice', 'vide', 'visi', 'want', 'ward', 'week', 'wing', 'work', 'year'
]

x5Gm = [  # selected 5-gram indices
    'allow', 'ameri', 'ation', 'board', 'build',
    'busin', 'ceive', 'centr', 'chang', 'child',
    'class', 'clude', 'compa', 'const', 'contr',
    'count', 'cover', 'creat', 'cross', 'curre',
    'defen', 'devel', 'direc', 'distr', 'drive',
    'ealth', 'earth', 'eason', 'elect', 'ember',
    'enter', 'eport', 'event', 'famil', 'gener',
    'gover', 'house', 'ident', 'infor', 'inter',
    'inves', 'level', 'light', 'llion', 'manag',
    'marke', 'matio', 'media', 'membe', 'milli',
    'mmuni', 'money', 'natio', 'night', 'offic',
    'ommun', 'order', 'organ', 'peopl', 'place',
    'polic', 'polit', 'posit', 'ppear', 'pport',
    'press', 'produ', 'progr', 'prove', 'publi',
    'quest', 'range', 'recor', 'repor', 'resid',
    'right', 'roduc', 'round', 'schoo', 'seaso',
    'socia', 'spect', 'sport', 'stand', 'start',
    'state', 'store', 'story', 'struc', 'table',
    'think', 'train', 'trans', 'truct', 'under',
    'unive', 'velop', 'water', 'world', 'ystem'
]

#
# a single hard-coded n-gram extraction function
#

Min = 2  # minimum n for n-grams
Max = 5  # maximum n

def divide ( strg ):

    """
    extract longest n-grams from a string of lowercase ASCII chars

    arguments:
        strg - input string
    returns:
        list of substrings from input
    """

    ngms = [ ]       # list to return

    ib = 0           # indices into input string
    il = len(strg)   #
    if il < Min: return ngms
    ie = il - 1

    nc = 0           # length of string already covered
    nl = il - ib     # number of chars left to cover
    nm = nl if nl < Max else Max  # length of next n-gram candidate

    while ib < ie:   # scan input string from start to end

        k = ib + nm
        if k <= nc:  # next n-gram must cover at least one new char
            ib += 1
            nl -= 1
            nm = nl if nl < Max else Max
            continue

        ss = strg[ib:k]
#       print ( "candidate n-gram=" , ss )
        if   nm == 5:
            if not ss in x5Gm:
                nm -= 1
                continue
        elif nm == 4:
            if not ss in x4Gm:
                nm -= 1
                continue
        elif nm == 3:
            if not ss[:2] in s2Gm:
                nm -= 1
                continue

        ngms.append(ss)  # save extracted n-gram
        nc = k           # update coverage
        ib += 1          # update input string indices
        nl -= 1          #
        nm = nl if nl < Max else Max

    return ngms

#
# unit test
#

import sys

if __name__ == '__main__':

    print ( 'testing word fragmentation' )

    if len(sys.argv) < 2:
        print ( "usage: X word" )
        sys.exit(0)

    w = sys.argv[1]  # word to decompose into n-grams

    ls = divide(w)

    print ( len(ls) , 'n-grams' )
    for g in ls:
        print ( g )
