# Authors: David Whitlock <alovedalongthe@gmail.com>, Bryan Helmig
# Crossword generator that outputs the grid and clues as a pdf file and/or
# the grid in png/svg format with a text file containing the words and clues.
# Copyright (C) 2010-2011 Bryan Helmig
# Copyright (C) 2011-2020 David Whitlock
#
# Genxword is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Genxword is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with genxword.  If not, see <http://www.gnu.org/licenses/gpl.html>.

import os
import sys
import gettext
import random
import calculate
import complexstring
from calculate import Crossword
from complexstring import ComplexString

class Genxword(object):
    def __init__(self, auto=True):
        self.auto = auto
        self.isBZH = False
        self.wordFont = None
        self.wordSize = 16

    def checkIsBZH(self, wordlist):
        if wordlist[0][0].upper()=="ISBZH" :
            if wordlist[0][-1].upper()=="TRUE" :
                self.isBZH = True
                wordlist.pop(0)
        elif wordlist[1][0].upper()=="ISBZH" :
            if wordlist[1][-1].upper()=="TRUE" :
                self.isBZH = True
                wordlist.pop(1)
        elif wordlist[2][0].upper()=="ISBZH" :
            if wordlist[2][-1].upper()=="TRUE" :
                self.isBZH = True
                wordlist.pop(2)

    def checkFont(self, wordlist):
        if wordlist[0][0].upper()=="WORDFONT" :
            self.wordFont = wordlist[0][-1]
            wordlist.pop(0)
        elif wordlist[1][0].upper()=="WORDFONT" :
            self.wordFont = wordlist[1][-1]
            wordlist.pop(1)
        elif wordlist[2][0].upper()=="WORDFONT" :
            self.wordFont = wordlist[2][-1]
            wordlist.pop(2)

    def checkFontSize(self, wordlist):
        if wordlist[0][0].upper()=="WORDSIZE" :
            self.wordSize = wordlist[0][-1]
            wordlist.pop(0)
        elif wordlist[1][0].upper()=="WORDSIZE" :
            self.wordSize = wordlist[1][-1]
            wordlist.pop(1)
        elif wordlist[2][0].upper()=="WORDSIZE" :
            self.wordSize = wordlist[2][-1]
            wordlist.pop(2)

    def wlist(self, words):
        """Create a list of words and clues."""
        wordlist = [line.strip().split('=', 1) for line in words if line.strip()]
        self.checkIsBZH(wordlist)
        self.checkFont(wordlist)
        self.checkFontSize(wordlist)

        #if len(wordlist) > nwords:
        #    wordlist = random.sample(wordlist, nwords)

        self.wordlist = []
        for line in wordlist :
            if self.isBZH :
                self.wordlist.append([ComplexString(ComplexString._check_bzh(line[0].upper())), line[0], line[-1]])
            else:
                self.wordlist.append([ComplexString(line[0].upper()), line[0], line[-1]])
        self.wordlist.sort(key=lambda i: len(i[0]), reverse=True)


    def grid_size(self, inputGridSize=0):
        """Calculate the default grid size."""
        if len(self.wordlist) <= 20:
            self.nrow = self.ncol = 17
        elif len(self.wordlist) <= 100:
            self.nrow = self.ncol = int((round((len(self.wordlist) - 20) / 8.0) * 2) + 19)
        else:
            self.nrow = self.ncol = 41
        if min(self.nrow, self.ncol) <= len(self.wordlist[0][0]):
            self.nrow = self.ncol = len(self.wordlist[0][0]) + 2
        if not self.auto:
            gsize = str(self.nrow) + ', ' + str(self.ncol)
            grid_size = inputGridSize
            if grid_size:
                self.check_grid_size(grid_size)

    def check_grid_size(self, grid_size):
        try:
            nrow, ncol = int(grid_size.split(',')[0]), int(grid_size.split(',')[1])
        except:
            pass
        else:
            if len(self.wordlist[0][0]) < min(nrow, ncol):
                self.nrow, self.ncol = nrow, ncol

    def gengrid(self, inputOksol, inputIncrSize):
        i = 0
        while 1:
            calc = Crossword(self.nrow, self.ncol, self.wordlist)
            computed = calc.compute_crossword()

            if self.auto:
                if float(len(calc.best_wordlist))/len(self.wordlist) < 0.9 and i < 5:
                    self.nrow += 2; self.ncol += 2
                    i += 1
                else:
                    break
            else:
                if inputOksol(computed) == True :
                    break

                if inputIncrSize() == True :
                    self.nrow += 2;self.ncol += 2
        return calc

