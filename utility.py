import numpy as np

def gridToArray(source : list[list[int]]) -> list[int]:
    result = [];
    for y in range(9):
        for x in range(9):
            result.append(source[y][x]);
    return result;
def floatGridToIntGrid(fBoard):
    iBoard = [];
    for y in range(9):
        iBoard.append([]);
        for x in range(9):
            iBoard[y].append(int(fBoard[y][x]));
    return iBoard;

def arrToGrid(source : list[int]) -> list[list[int]]:
    result = [];
    for y in range(9):
        result.append([]);
        for x in range(9):
            result[y].append(source[9*y + x]);
    return result;

def removeDuplicates(arr):
    result = [];
    for e in arr:
        add = True;
        for re in result:
            if (re == e):
                add = False; break;
        if (add):
            result.append(e);
    return result;


def findInvalidCells(grid):
    cells = [];
    # check all subgrids
    for y in range(3):
        for x in range(3):
            nums = [None for i in range(9)]
            # check nums in sub-grid
            bx = x * 3;
            by = y * 3;
            for i in range(3):
                for j in range(3):
                    val = int(grid[by + i][bx + j]);
                    if (nums[val - 1] != None):
                        cells.append((by + i, bx + j));
                        cells.append(nums[val - 1]);
                    nums[val - 1] = (by + i, bx + j);
    # check all rows and columns
    for i in range(9):
        row = [0 for n in range(9)];
        column = [0 for n in range(9)];
        # check nums in row
        for j in range(9):
            val = int(grid[i][j]);
            if (row[val - 1] > 0):
                cells.append((i, j));
                cells.append((i, row[val - 1]));
            row[val - 1] = j;
        # check nums in column
        for j in range(9):
            val = int(grid[j][i]);
            if (column[val - 1] > 0):
                cells.append((j, i));
                cells.append((column[val - 1], i));
            column[val - 1] = j;
    return removeDuplicates(cells);


def gridToIndeces(grid):
    arr = [];
    for y in range(9):
        for x in range(9):
            if (grid[y][x] != None and grid[y][x] != 0):
                arr.append((y, x));
    return arr;


def getExclusion(source, exclude):
    arr = [];
    for e in source:
        if (e not in exclude):
            arr.append(e);
    return arr;


def minusOne(source : list[int] | list[list[int]], twoDim : bool = True) -> list[int] | list[list[int]]:
    for y in range(9):
        for x in range(9):
            if (twoDim):
                if (source[y][x] == None):
                    source[y][x] = 0;
                #else: source[y][x] -= 1;
            else:
                if (source[9*y + x] == None):
                    source[9*y + x] = 0;
                #else: source[9*y + x] -= 1;
    return source;
    


def isInt(val):
    try:
        int(val); return True;
    except ValueError:
        return False;
