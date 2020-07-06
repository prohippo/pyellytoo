# README.md

# for PyElly v2.+

PyElly is an integrated toolkit of rule-based natural language processing capabilities
written in Python. This repository contains PyElly v2.*, which was created initially
by converting PyElly v1.6 from Python 2.7 code into Python 3.8 code. 

PyElly is aimed at students in high school who want to build class projects as a way
to gain firsthand experience with computation linguistics. It also may be of interest
to data scientists who need to dig deeper into their text data. The BSD licensing of
PyElly sets almost no restriction on what you can do with it.

The earlier pyelly GitHub repository https://github.com/prohippo/pyelly.git contains
the Python 2.7 code for PyElly v1.6.1.  This is provided for reference and for Python
users not yet migrated to Python 3.*. All further PyElly development will be for
PyElly 2.*.

Release Notes:

 2.0    -  19nov2019  initial release of code converted to Python 3.8.
 2.1    -  04feb2020  simplify logic for deinflectionMatching, clarify unit testing
                      clean up reading of text for unit tests in various modules
                      correct bug in patternTable dump 
                      minor extension of MARKING application vocabulary
                      adjust MARKING portion of integration testing
                      update documentation
 2.1.1  -  03jun2020  clean up MARKING grammar rules for documentation and reuse
                      minor extension of MARKING application vocabulary
                      update documentation
 2.1.2  -  22jun2020  fix missing error check for generative semantic subprocedures
                      clean up MARKING rules
                      define new MINIMARKING application for minimal text markup 
                      update documentation
 2.1.3  -  01jul2020  add check for missing semantic subprocedure in rule compilation
                      extend MINIMARKING application test
                      fix error in MARKING grammar rule
                      update documentation
 2.1.4  -  05jul2020  debug and extend checks fo undefined semantic subprocedures
                      extend MINIMARKING application test
                      pdate documentation
