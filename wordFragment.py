#!/usr/bin/python3
# Code for extending PyElly capabilities
#
# wordFragment.py : 07jun2021 CPM
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
    'able', 'acce', 'ache', 'admi', 'ague', 'aint', 'allo', 'ally', 'ampl', 'anal',
    'ance', 'anch', 'ange', 'anta', 'anti', 'appe', 'appl', 'appr', 'aran', 'arch',
    'area', 'arge', 'arri', 'arth', 'arti', 'ason', 'aste', 'astr', 'atch', 'ater',
    'atin', 'atio', 'atta', 'atte', 'ause', 'back', 'ball', 'band', 'bank', 'base',
    'batt', 'bill', 'blem', 'body', 'book', 'butt', 'call', 'camp', 'cana', 'cand',
    'care', 'case', 'cast', 'caus', 'ceiv', 'cent', 'cept', 'cert', 'cess', 'cham',
    'chan', 'char', 'chis', 'choo', 'chri', 'cide', 'cien', 'city', 'clos', 'coll',
    'colo', 'come', 'comm', 'comp', 'conc', 'cond', 'conf', 'cons', 'cont', 'conv',
    'cord', 'core', 'cost', 'coun', 'cour', 'cove', 'crea', 'cula', 'cult', 'curr',
    'date', 'deal', 'deci', 'defe', 'demo', 'dent', 'dera', 'desi', 'dest', 'diff',
    'disa', 'disc', 'dist', 'divi', 'down', 'dres', 'driv', 'each', 'earn', 'eart',
    'ease', 'easo', 'east', 'eath', 'eave', 'ecia', 'econ', 'ecor', 'ecre', 'edge',
    'edit', 'educ', 'eigh', 'elec', 'embe', 'empl', 'ente', 'enti', 'entr', 'epar',
    'epor', 'epre', 'eque', 'equi', 'eral', 'erse', 'erve', 'esca', 'esti', 'estr',
    'eter', 'evel', 'even', 'ever', 'exam', 'expe', 'face', 'fact', 'fall', 'feat',
    'fect', 'ffer', 'ffor', 'fiel', 'film', 'fina', 'fini', 'fire', 'foll', 'foot',
    'forc', 'fore', 'form', 'fort', 'free', 'fter', 'gain', 'game', 'gene', 'gest',
    'give', 'good', 'grad', 'gram', 'gree', 'grou', 'grow', 'half', 'hamp', 'hand',
    'happ', 'hard', 'hast', 'head', 'heal', 'hear', 'heat', 'heir', 'help', 'hero',
    'high', 'hist', 'hold', 'home', 'hone', 'icat', 'idea', 'ight', 'impl', 'impo',
    'impr', 'indu', 'inge', 'inst', 'inte', 'inve', 'isla', 'iste', 'istr', 'itch',
    'itio', 'itis', 'iver', 'ject', 'just', 'keep', 'kill', 'king', 'know', 'lace',
    'lack', 'land', 'lant', 'last', 'late', 'lati', 'lead', 'lean', 'lear', 'leas',
    'lect', 'lega', 'lete', 'lice', 'life', 'line', 'lion', 'list', 'live', 'llow',
    'loca', 'lock', 'long', 'look', 'love', 'lude', 'main', 'majo', 'make', 'mand',
    'mark', 'mate', 'mber', 'mean', 'medi', 'meet', 'ment', 'meth', 'mili', 'mine',
    'mini', 'miss', 'mmer', 'mode', 'mont', 'more', 'moun', 'move', 'mple', 'muni',
    'musi', 'nage', 'name', 'nati', 'nder', 'ndle', 'need', 'ngle', 'note', 'nsti',
    'nstr', 'nter', 'ntin', 'oach', 'oard', 'offe', 'offi', 'ogra', 'olve', 'omen',
    'ompl', 'onde', 'oney', 'onom', 'onst', 'ontr', 'open', 'oper', 'orig', 'orit',
    'orth', 'ossi', 'othe', 'ough', 'ounc', 'ound', 'oung', 'ount', 'ourn', 'ouse',
    'outh', 'over', 'pani', 'para', 'pare', 'park', 'part', 'pass', 'past', 'pect',
    'pend', 'perf', 'peri', 'pers', 'pert', 'plac', 'plan', 'play', 'plet', 'poin',
    'poli', 'port', 'pose', 'posi', 'post', 'pres', 'prin', 'pris', 'prob', 'proc',
    'prof', 'prom', 'prop', 'prot', 'prov', 'quar', 'ques', 'quir', 'race', 'rack',
    'ract', 'rade', 'radi', 'raft', 'rage', 'ranc', 'rand', 'rang', 'rate', 'rati',
    'read', 'real', 'rear', 'reas', 'rece', 'reco', 'redi', 'refe', 'refo', 'regi',
    'rele', 'reli', 'reme', 'remo', 'rent', 'repo', 'repr', 'resi', 'reso', 'ress',
    'rest', 'rict', 'ring', 'rive', 'road', 'rong', 'ront', 'room', 'rope', 'roun',
    'rove', 'sand', 'scan', 'scen', 'scho', 'scor', 'scou', 'scri', 'sear', 'seas',
    'secu', 'sent', 'seri', 'serv', 'seve', 'shad', 'shar', 'shel', 'ship', 'show',
    'side', 'sign', 'sist', 'soci', 'soft', 'spar', 'spec', 'spit', 'spla', 'spri',
    'stab', 'star', 'stat', 'ster', 'stit', 'stoc', 'stop', 'stor', 'stra', 'stre',
    'stri', 'stru', 'stud', 'succ', 'sult', 'supp', 'sure', 'tabl', 'tack', 'tain',
    'take', 'tall', 'tate', 'team', 'tech', 'temp', 'tend', 'tent', 'terf', 'term',
    'terr', 'test', 'ther', 'thor', 'time', 'tion', 'tone', 'tore', 'tory', 'tour',
    'town', 'trac', 'trad', 'trea', 'tree', 'trib', 'tric', 'trol', 'tron', 'tter',
    'ttle', 'ture', 'turn', 'ulat', 'ulti', 'unde', 'unit', 'urch', 'urse', 'velo',
    'vent', 'vers', 'vert', 'vest', 'vice', 'vict', 'vide', 'view', 'vill', 'visi',
    'vote', 'want', 'ward', 'wash', 'week', 'wing', 'work', 'writ', 'xper', 'year'
]

x5Gm = [  # selected 5-gram indices
    'advan', 'agree', 'allow', 'ameri', 'assoc', 'ation', 'attle', 'avail', 'black', 'board',
    'break', 'build', 'busin', 'ceive', 'centr', 'centu', 'chang', 'chara', 'charg', 'child',
    'claim', 'class', 'clude', 'commo', 'compa', 'compe', 'const', 'conta', 'conte', 'contr',
    'conve', 'count', 'cours', 'court', 'cover', 'creat', 'cross', 'curre', 'decid', 'defen',
    'democ', 'depar', 'depen', 'desig', 'devel', 'direc', 'disco', 'distr', 'drive', 'ealth',
    'earin', 'earth', 'eason', 'educa', 'egion', 'elect', 'ember', 'emplo', 'enter', 'eport',
    'equen', 'ermin', 'escri', 'event', 'expec', 'famil', 'fathe', 'featu', 'fight', 'finan',
    'front', 'gener', 'gover', 'graph', 'green', 'gress', 'groun', 'happe', 'house', 'human',
    'icipa', 'ident', 'impor', 'indus', 'infor', 'insta', 'inter', 'inves', 'level', 'light',
    'llion', 'locat', 'manag', 'march', 'marke', 'matio', 'media', 'membe', 'milit', 'milli',
    'minut', 'mmuni', 'money', 'mount', 'natio', 'natur', 'ngine', 'night', 'offic', 'ology',
    'ommun', 'ontra', 'order', 'organ', 'ouble', 'paren', 'peopl', 'phone', 'pital', 'place',
    'plain', 'plete', 'polic', 'polit', 'posit', 'ppear', 'pport', 'pract', 'press', 'price',
    'proce', 'produ', 'progr', 'proje', 'prope', 'prote', 'prove', 'publi', 'quart', 'quest',
    'range', 'recor', 'refer', 'refor', 'regul', 'repla', 'repor', 'repub', 'resid', 'right',
    'river', 'roduc', 'round', 'schoo', 'scien', 'score', 'searc', 'seaso', 'secur', 'sland',
    'slate', 'socia', 'spect', 'splay', 'sport', 'stabl', 'stand', 'start', 'state', 'stati',
    'stone', 'store', 'story', 'strat', 'stree', 'struc', 'super', 'table', 'teach', 'techn',
    'tempt', 'theat', 'theor', 'think', 'tract', 'train', 'trans', 'treat', 'truct', 'ultur',
    'ument', 'under', 'unive', 'velop', 'volve', 'watch', 'water', 'women', 'world', 'ystem'
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
