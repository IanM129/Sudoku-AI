## Sudoku 2D grid
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
def sprintGrid2D_Line(target):
    r = "[";
    first = True;
    for y in range(9):
        for x in range(9):
            if (not first): r += ",";
            else: first = False;
            if (target[y][x] == None): r += "/";
            else: r += str(target[y][x]);
    r += "]";
    return r;

# Sudoku array
def sprintGrid1D(target):
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

# SudokuSample
def printSudokuSample(sample):
    print(str(sample.ID) + " (" +
          str(sample.clueCount) + " : " + str(sample.difficulty) + ")");
    print(sample.sprintPuzzle());
    print(sample.sprintSolution(), end = ";\n");
    #print(str(sample.clueCount) + " : ", end = '');
    #print(str(sample.difficulty));


# Training samples and batches
def sprintTestSample(x, y):
    r = "- sample:\n";
    x_cur = x.numpy();
    y_cur = y;
    # print input grid
    for yi in range(9):
        r += "[";
        first = True;
        for xi in range(9):
            #print("(", yi, ", ", xi, ") = ", x_cur[yi][xi]);
            if (not first): r += " ";
            else: first = False;
            if (x_cur[yi][xi][0] == 0): r += "/";
            else: r += str(x_cur[yi][xi][0]);
        r += "]  ->  [";
        first = True;
        for xi in range(9):
            if (not first): r += " ";
            else: first = False;
            r += str(y_cur[9*yi + xi][0]);
        r += "]";
        if (yi < 8): r += "\n";
    #r += "\n";
    #r += "-> [";
    #first = True;
    #for i in y[0].numpy():
    #    if (not first): r += " ";
    #    else: first = False;
    #    r += str(i[0]);
    #r += "]\n";
    return r;
def sprintBatch(x, y, size, card = -1):
    r = "train batch"
    if (card > -1):
        r += " #" + str(card);
    r += ":\n";
    for b in range(size):
        r += "#" + str(b) + "\n";
        x_cur = x[b].numpy();
        y_cur = y[b];
        # print input grid
        for yi in range(9):
            r += "[";
            for xi in range(9):
                #print("(", yi, ", ", xi, ") = ", x_cur[yi][xi]);
                r += " ";
                if (x_cur[yi][xi] == -1): r += "/";
                else: r += str(x_cur[yi][xi]);
            r += "]    [";
            for xi in range(9):
                r += " ";
                r += str(y_cur[9*yi + xi]);
            r += "]\n";
        #r += "\n";
    return r;


# Evaluating
def sprintEvalResult(puzzle, result, accGrid):
    r = "";
    for y in range(9):
        r += "[";
        for x in range(9):
            if (x > 0): r += " ";
            r += str(puzzle[y][x]);
        r += "]  [";
        for x in range(9):
            if (x > 0): r += " ";
            r += str(int(result[y][x]));
        r += "]  =>  [";
        for x in range(9):
            if (x > 0): r += " ";
            r += str(accGrid[y][x]);
        r += "]";
        if (y < 8): r += "\n";
    return r;