from math import floor
import random as rand
from time import time as time_time
from datetime import datetime
from debug import sprintGrid1D, sprintGrid2D

rand.seed(int(datetime.now().timestamp()));

####### Structures  #######
## {cell item/element, value in cell (int)}
class SudokuGrid:
    grid = [None] * 81;
    def getElement(self, x, y):
        return self.grid[9*y + x][0];
    def getVal(self, x, y):
        return self.grid[9*y + x][1];
    def setVal(self, x, y, val):
        self.grid[9*y + x][1] = val;
#######


#######  Utility functions  #######
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
def isSudokuValid(grid : list[list[int]], retCnt : bool = False) -> bool:
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
def emptyGrid():
    grid = [];
    for i in range(9):
        grid.append([None] * 9);
    return grid;
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

#######  Generate random grid  #######
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
## Main
def generateRest(grid : list[list[int]]) -> list[list[int]]:
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
def generateRandomGrid() -> list[list[int]]:
    grid = emptyGrid();
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
#######

#######  Grid solving algorithm(s)  #######
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
def solveGrid(grid, start = False):
    if start == True:
        start_timer = time_time();
    # get first empty
    empty = getFirstEmpty(grid);
    # check if grid filled
    if (not empty):
        if (start):
            print("not empty??");
            print(grid);
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
                if (start == True):
                    print("done; duration: " + str(time_time() - start_timer));
                return True;
            grid[y][x] = None;
    return False;
#######

#######  Generate puzzle  #######
# solGrid must be 2D [9][9] grid
def generatePuzzle(solGrid : list[list[int]], missingClues : int) -> tuple[list[list[int]], list[int]]:
    pzlGrid = [];
    # copy solGrid to not modify it
    for i in range(9):
            pzlGrid.append([]);
            for j in range(9):
                pzlGrid[i].append(solGrid[i][j]);
    #attempts = 1;
    cells = list(range(0, 80));
    rand.shuffle(cells);
    removedCells = [None] * 81;
    for n in range(missingClues):
        if (len(cells) == 0):
            print("IMPOSSIBLE COMBO"); return None;
        val = cells.pop();
        # select a random cell that is not already empty
        x = val % 9;
        y = floor(val / 9);
        if (solGrid[y][x] == None): continue;
        # remember its cell value in case we need to put it back  
        backup = pzlGrid[y][x];
        pzlGrid[y][x] = None;
        # take a full copy of the grid
        copyGrid = [];
        for i in range(9):
            copyGrid.append([]);
            for j in range(9):
                copyGrid[i].append(pzlGrid[i][j]);
        #gridToSystem(grid);
        # solutions
        #sols = solveGridCount(copyGrid);
        #if sols == 0:
        if not solveGrid(copyGrid):
            pzlGrid[y][x] = backup;
            i -= 1;
        else:
            removedCells[9*y + x] = backup;
            #print("removed ", n + 1, "; removed cells: ", removedCells); -> debug
    return (pzlGrid, removedCells);
#######


#######  EXPORT  #######
def generateFullSample(missing : int) -> tuple[list[list[int]], list[list[int]], list[int]]:
    # create grid
    solGrid = generateRandomGrid();
    # create puzzle
    (inputGrid, removed) = generatePuzzle(solGrid, missing);
    return inputGrid, solGrid, removed;
#######
