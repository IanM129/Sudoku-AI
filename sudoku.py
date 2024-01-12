from math import floor
import tkinter as tk
from tkinter import font as tkFont
from functools import partial
import random as rand
import time

## {cell item/element, value in cell (INT)}
class SudokuGrid:
    grid = [None] * 81;
    def getElement(self, x, y):
        return self.grid[9*y + x][0];
    def getVal(self, x, y):
        return self.grid[9*y + x][1];
    def setVal(self, x, y, val):
        self.grid[9*y + x][1] = val;

## UTILITY
def sprintGrid(target):
    r = "";
    for y in range(9):
        r += "[";
        first = True;
        for x in range(9):
            if (not first): r += ", ";
            else: first = False;
            if (target[9*y + x] == None): r += "/";
            else: r += str(target[9*y + x]);
        r += "]";
        if (y != 8): r += "\n";
    return r;
def sprintGrid2D(target):
    r = "";
    for y in range(9):
        r += "[";
        first = True;
        for x in range(9):
            if (not first): r += ", ";
            else: first = False;
            if (target[y][x] == None): r += "/";
            else: r += str(target[y][x]);
        r += "]";
        if (y != 8): r += "\n";
    return r;


#### FUNCTIONS
## Check validity
# (x, y) = [0, 2]
def subGridValid(x, y, grid, retCnt = False):
    nums = [False for i in range(9)]
    count = 0;
    # check nums in subGrid
    bx = x * 3;
    by = y * 3;
    for i in range(3):
        for j in range(3):
            val = int(grid[by + i][bx + j]);
            if (nums[val - 1] == True):
                if (not retCnt): return False;
                count += 1;
            nums[val - 1] = True;
    if (retCnt): return count;
    return True;
def rowValid(y, grid, retCnt = False):
    nums = [False for i in range(9)];
    count = 0;
    # check nums in row
    for i in range(9):
        val = int(grid[y][i]);
        if (nums[val - 1] == True):
            if (not retCnt): return False;
            count += 1;
        nums[val - 1] = True;
    if (retCnt): return count;
    return True;
def columnValid(x, grid, retCnt = False):
    nums = [False for i in range(9)];
    count = 0;
    # check nums in row
    for i in range(9):
        val = int(grid[i][x]);
        if (nums[val - 1] == True):
            if (not retCnt): return False;
            count += 1;
        nums[val - 1] = True;
    if (retCnt): return count;
    return True;
def isSudokuValid(grid, retCnt = False):
    count = 0;
    # check all subgrids
    for y in range(3):
        for x in range(3):
            curCnt = subGridValid(x, y, grid, True);
            if (curCnt > 0):
                #print("Subgrid #(" + str(y + 1) + ", " + str(x + 1) + ") is invalid.");
                if (not retCnt): return False;
                count += curCnt;
    if (count > 0):
        return (81 - count);
    # check all rows and columns
    for i in range(9):
        curCnt = rowValid(i, grid, True);
        if (curCnt > 0):
            #print("Row #" + str(i + 1) + " is invalid.");
            if (not retCnt): return False;
            count += curCnt;
        curCnt = columnValid(i, grid, True);
        if (curCnt > 0):
            #print("Column #" + str(i + 1) + " is invalid.");
            if (not retCnt): return False;
            count += curCnt;
    if (retCnt): return (81 - count);
    return True;
## Create grid and puzzle
def getEmptyGrid():
    grid = [];
    for i in range(9):
        grid.append([None] * 9);
    return grid;
def generateSubGrid(parent, x=3, y=3):
    frame = tk.Frame(parent);
    photos = [];
    start = 1;
    for i in range(y):
        for j in range(x):
            pi = tk.PhotoImage(width=1,height=1);
            photos.append(pi);
            btn = tk.Button(frame,text=start,image=pi,compound="c",width=cellSize,height=cellSize);
            btn.grid(row=i,column=j,sticky=tk.W,padx=1,pady=1);
            btn["font"] = helv36;
            start += 1;
    return photos, frame;
def getValidNums(x, y, grid):
    # bool list
    valid = [];
    for i in range(1, 10):
        valid.append(True);
    # get nums in subGrid
    bx = x - (x % 3);
    by = y - (y % 3);
    for i in range(3):
        for j in range(3):
            if ((bx + j) != x or (by + i) != y):
                val = grid[by + i][bx + j];
                if (val != None):
                    valid[val - 1] = False;
    # get nums in row
    for i in range(9):
        if (i != y):
            val = grid[i][x];
            if (val != None):
                valid[val - 1] = False;
    # get nums in column
    for i in range(9):
        if (i != x):
            val = grid[y][i];
            if (val != None):
                valid[val - 1] = False;
    # result
    result = [];
    debug = [];
    for i in range(1, 10):
        if (valid[i - 1]):
            result.append(i);
        else:
            debug.append(i);
    #print(" X -> ", debug);
    return result;


#######
def getFirstEmpty(grid):
    for x in range(0,9):
        for y in range(0,9):
            if grid[y][x] == None:
                return (x, y);
    return False;
def checkGrid(grid):
    for x in range(0,9):
        for y in range(0,9):
            if grid[y][x] == None:
                return False
    return True
##
def generateRest(grid):
    if checkGrid(grid):
        return grid;
    for y in range(9):
        for x in range(9):
            if grid[y][x] == None:
                vals = getValidNums(x, y, grid);
                if (len(vals) > 0):
                    for val in vals:
                        grid[y][x] = val;
                        if (solveGrid(grid)):
                            return generateRest(grid);
                        grid[y][x] = None;
    return False;
def generateRandomGrid():
    grid = getEmptyGrid();
    nums = list(range(1, 10));
    for y in range(3):
        for x in range(3):
            n = rand.choice(nums);
            grid[y][x] = n;
            nums.remove(n);
    nums = list(range(1, 10));
    for y in range(3, 6):
        for x in range(3, 6):
            n = rand.choice(nums);
            grid[y][x] = n;
            nums.remove(n);
    nums = list(range(1, 10));
    for y in range(6, 9):
        for x in range(6, 9):
            n = rand.choice(nums);
            grid[y][x] = n;
            nums.remove(n);
    #gridToSystem(grid);
    return generateRest(grid);

## Grid solving algorithm
def solveGridCount(grid):
    solutions = 0;
    maxSolsFound = 0;
    # get all empty
    empty = getEmpty(grid);
    # check if grid filled
    if (not empty):
        return 1;
    # iterate through empty
    for (x, y) in empty:
        vals = getValidNums(x, y, grid);
        ## debug
        #gridToSystem(grid);
        #print("valid for (", x, ", ", y, "): ", vals);
        #input("paused");
        ##
        if (len(vals) > 0):
            rand.shuffle(vals);
            for val in vals:
                grid[y][x] = val;
                newSols = solveGridCount(grid);
                solutions += newSols;
                grid[y][x] = None;
        if (solutions > maxSolsFound):
            maxSolsFound = solutions;
        solutions = 0;
    return maxSolsFound;
def solveGrid(grid):
    # get first empty
    empty = getFirstEmpty(grid);
    # check if grid filled
    if (not empty):
        return True;
    # iterate through possible values to put in empty
    x = empty[0];
    y = empty[1];
    vals = getValidNums(x, y, grid);
    if (len(vals) > 0):
        rand.shuffle(vals);
        for val in vals:
            grid[y][x] = val;
            if (solveGrid(grid)):
                return True;
            grid[y][x] = None;
    return False;

## Main puzzle generation
def generatePuzzle(grid, missingClues):
    attempts = 1;
    cells = list(range(0, 80));
    rand.shuffle(cells);
    removedCells = [None] * 81;
    for n in range(missingClues):
        if (len(cells) == 0):
            print("IMPOSSIBLE COMBO"); return grid;
        val = cells.pop();
        # select a random cell that is not already empty
        x = val % 9;
        y = floor(val / 9);
        if (grid[y][x] == None):
            continue;
        # remember its cell value in case we need to put it back  
        backup = grid[y][x];
        grid[y][x] = None;
        # take a full copy of the grid
        copyGrid = [];
        for i in range(9):
            copyGrid.append([]);
            for j in range(9):
                copyGrid[i].append(grid[i][j]);
        #gridToSystem(grid);
        # solutions
        #sols = solveGridCount(copyGrid);
        #if sols == 0:
        if not solveGrid(copyGrid):
            grid[y][x] = backup;
            i -= 1;
        else:
            removedCells[9*y + x] = backup;
            #print("removed ", n + 1, "; removed cells: ", removedCells); -> debug
        #gridToSystem(grid);
    return (grid, removedCells);
######

## EXPORT
def generateFullSample(missing):
    # create grid
    solGrid = generateRandomGrid();
    # create puzzle
    (inputGrid, removed) = generatePuzzle(solGrid, missing);
    return inputGrid, solGrid, removed;
