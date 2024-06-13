import os
from modules.sudoku import generateFullSample
from modules.utility import gridToArray, isInt
from modules.debug import printSudokuSample, sprintGrid2D_Line, printSudokuSample

import winsound # debug

datasetPath = "../../dataset/"; #""../dataset/";
evaluatePath = "./dataset_eval/";

nxtID = 0;
# Sudoku sample class
class SudokuSample:
    ID : int;
    puzzle : list[int];             # = [<int> (0 - 9)] * 81
    solution : list[int];           # = [<int> (1 - 9)] * 81
    clueCount : int;                # = <int> | None
    difficulty : float;             # = <float> | None

    def __init__(self, ID : int, puzzle : list, solution : list, clueCount : int, difficulty : float):
        self.ID = ID;
        if (len(puzzle) != 81 or len(solution) != 81 or not isInt(solution[0])):
            print("ERROR: Failed to create new SudokuSample."); return;
        self.puzzle = puzzle; self.solution = solution;
        self.clueCount = clueCount;
        self.difficulty = difficulty;
    def __hash__(self):
        return hash((self.puzzle, self.solution));
        
    def sprintPuzzle(self):
        s = "";
        for n in self.puzzle:
            if (n == 0 or n == None): s += '.';
            else: s += str(n);
        return s;
    def sprintSolution(self):
        s = "";
        for n in self.solution:
            s += str(n);
        return s;

## Parse sample text
def parseSample(dataLine : str) -> SudokuSample:
    data = dataLine.split(',');
    # Get ID
    ID = int(data[0]);
    # Get Puzzle
    puzzle = [0] * 81;
    try:
        for i in range(81):
            if (data[1][i] != '.'):
                puzzle[i] = int(data[1][i]);
    except ValueError:
        print("ERROR: Non-int value detected in given text for puzzle of sample."); return None;
    # Get Solution
    solution = [0] * 81;
    try:
        for i in range(81):
            solution[i] = int(data[2][i]);
    except ValueError:
        print("ERROR: Non-int value detected in given text for solution of sample."); return None;
    if (len(data) > 3):
        # Get clue count
        clueCount = int(data[3]);
    else: clueCount = None;
    if (len(data) > 4):
        # Get difficulty
        difficulty = float(data[4]);
    else: difficulty = None;
    return SudokuSample(ID, puzzle, solution, clueCount, difficulty);
def parseSampleBasic(puzzleLine : str, solutionLine : str, ID : int | None, clueCount : int | None) -> SudokuSample:
    # Get ID
    ID = int(ID);
    # Get Puzzle
    puzzle = [0] * 81;
    data = puzzleLine.split(',');
    for i in range(81):
        puzzle[i] = data[i];
    # Get Solution
    solution = [0] * 81;
    data = solutionLine.split(',');
    for i in range(81):
        solution[i] = data[i];
    # Get clue count
    if (clueCount != None): clueCount = int(clueCount);
    # No difficulty
    if (difficulty != None): difficulty = float(-1);
    return SudokuSample(ID, puzzle, solution, clueCount, difficulty);
##


### Dataset management
# Sort into categories
def sortIntoCats(dataset):
    clueCats = {};
    for sample in dataset:
        if sample.clueCount not in clueCats:
            clueCats[sample.clueCount] = [];
        clueCats[sample.clueCount].append(sample);
    return clueCats;
# Load all data from main file
def loadWholeDataset(path):
    dataset = []
    f = open(path, "r");
    f.readline();  # skip first line
    for line in f:
        dataset.append(parseSample(line.rstrip()));
    f.close();
    print("INFO: Dataset loaded.");
    return dataset;
def loadDataset_internal(path : str, amount : int = -1) -> tuple[list[SudokuSample] | None, int]:
    dataset = [];
    if (not os.path.isfile(path)):
        print("ERROR: Invalid path '" + str(path) + "'."); return None;
    f = open(path, "r");
    firstLineSplt = f.readline().rstrip().split(',');
    fileCC = -1;
    if (len(firstLineSplt) == 1): size = firstLineSplt[0];
    elif (len(firstLineSplt) == 2): 
        fileCC = firstLineSplt[0]; size = firstLineSplt[1];
        if (not fileCC.isdigit()):
            print("ERROR: First line clue count of file isn't digit/clue count."); return None;
        fileCC = int(fileCC);
    else: print("ERROR: First line wrong format."); return None;
    if (not size.isdigit()):
        print("ERROR: First line size of set of file isn't digit/clue count."); return None;
    size = int(size);
    f.readline();  # skip second line
    if (amount == -1):
        for line in f:
            dataset.append(parseSample(line.rstrip()));
    else:
        i = 0;
        for line in f:
            dataset.append(parseSample(line.rstrip()));
            i += 1;
            if (i >= amount):
                break;
    f.close();
    if (amount == -1 and size != len(dataset)):
        print("WARNING: Written size (" +
              str(size) + ") not equal to actual size(" + str(len(dataset)) + ").");
    return (dataset, fileCC);
# Load dataset with certain clue count
def loadDataset(clueCount : int, amount : int = -1) -> list[SudokuSample] | None:
    dataset = []
    global datasetPath;
    path = datasetPath + str(clueCount) + ".csv";
    if (not os.path.isfile(path)):
        print("ERROR: Dataset with clue count " + str(clueCount) + " not found."); return None;
    print("INFO: Loading dataset with " + str(clueCount) + " clues...");
    dataset, fileCC = loadDataset_internal(path, amount);
    if (fileCC > -1 and fileCC != clueCount):
            print("ERROR: File clue count not equal to file name clue count."); return None;
    if (dataset == None): return None;
    print("INFO: Dataset with " + str(clueCount) + " clues successfully loaded; size: " + str(len(dataset)));
    return dataset;
# OLD load
def loadDatasetOLD(missing : int, targetSize : int = -1) -> list[SudokuSample] | None:
    clueCount = 81 - missing
    dataset = []
    path = "../tests/" + str(missing);
    if (not os.path.isdir(path)):
        print("ERROR: OLD dataset with missing count " +
              str(missing) + " not found.");
        return None;
    print("INFO: Loading OLD dataset with " + str(missing) + " missing cells...");
    ID = int(0)
    for filename in os.listdir(path):
        file = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(file) and filename.startswith("test"):
            f = open(file, "r");
            # get header
            ccnt, size = f.readline().split(',')
            pzlLine = f.readline().rstrip();
            while pzlLine != "":
                solLine = f.readline().rstrip();
                newS = parseSampleBasic(pzlLine, solLine, ID, clueCount);
                dataset.append(newS);
                ID += 1;
                f.readline();
                pzlLine = f.readline().rstrip();
                if (targetSize > -1 and len(dataset) == targetSize):
                    break;
            f.close();
        if (targetSize > -1 and len(dataset) == targetSize):
            break;
    print("INFO: OLD dataset with " + str(missing) +
          " missing cells successfully loaded; size: " + str(len(dataset)));
    return dataset;
def loadEvalSet(clueCount : int, amount : int = -1) -> list[SudokuSample] | None:
    evalset = [];
    global evaluatePath;
    path = evaluatePath + str(clueCount) + ".csv";
    if (not os.path.isfile(path)):
        print("ERROR: Evalset with clue count " + str(clueCount) + " not found."); return None;
    print("INFO: Loading evalset with " + str(clueCount) + " clues...");
    evalset, fileCC = loadDataset_internal(path, amount);
    if (fileCC > -1 and fileCC != clueCount):
        print("ERROR: File clue count not equal to file name clue count."); return None;
    if (evalset == None): return None;
    print("INFO: Evalset with " + str(clueCount) + " clues successfully loaded; size: " + str(len(evalset)));
    return evalset;


# Write dataset to ../dataset/{clueCount}.csv
# 1     |{dataset_size}
# 2     |id,puzzle,solution,clues,difficulty
# 3 - n |{id : int},{puzzle : 81 ints (no spaces)},{solution : same as puzzle},{clues : int},{difficulty : int}
# -> dataset must be SudokuSample list
def saveWriteDataset(dataset : list[SudokuSample], clueCount : int, path : str = "", append : bool = False, force : bool = False):
    if (path == ""):
        print("ERROR: No path given."); return;
        #global datasetPath;
        #path = datasetPath;
    elif (path.endswith('\\')):
        path = path[:-1] + '/';
    elif (not path.endswith('/')):
        path += '/';
    path += str(clueCount) + ".csv";
    if (os.path.isfile(path) and not force and not append):
        print("WARNING: Dataset with " + str(clueCount) + " already exists");
        winsound.Beep(2000, 400);
        answer = input("Proceed with overwriting? y/n ");
        if answer.lower() not in ["y","yes"]:
            print("INFO: Cancelling overwriting."); return;
    dirs = path.rsplit('/', 1)[0]
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    clueCats = sortIntoCats(dataset);
    if (append):
        if (not os.path.isfile(path)):
            print("WARNING: Dataset with " + str(clueCount) + " doesn't exist, creating...");
            w = open(path, "w");
            w.write(str(clueCount) + ",0");
            w.close();
        with open(path, "r") as r:
            rLines = r.readlines();
            _, inFileCnt = rLines[0].rstrip().split(',');
            try: inFileCnt = int(inFileCnt);
            except ValueError:
                print("ERROR: Non-int size written in file '" + str(path) + "'"); os._exit(1);
            f = open(path, "w");
            total = inFileCnt + len(dataset);
            f.write(str(clueCount) + "," + str(total) + "\n");
            for i in range(1, len(rLines)):
                f.write(rLines[i]);
    else:
        f = open(path, "w");
        f.write(str(clueCount) + "," + str(len(dataset)) + "\n");
        f.write("id,puzzle,solution\n");
    for s in clueCats[clueCount]:
         f.write(str(s.ID) + ',' + s.sprintPuzzle() + ',' + s.sprintSolution() + "\n");
    f.close();
    print("INFO: " + ("Appended" if (append) else "Written") + " " + str(len(dataset)) + " samples from loaded dataset to " + str(clueCount) + " clue dataset.");
    return;
###


### Console functions
def generateSamplesFast(clueCount : int, amount : int, ID : int = 0) -> list[SudokuSample]:
    sampleset = [];
    missing = 81 - clueCount;
    for i in range(amount):
        (puzzle, grid, removed) = generateFullSample(missing);
        sample = SudokuSample(ID + i, gridToArray(puzzle), gridToArray(grid), clueCount, -1.0);
        sampleset.append(sample);
    return sampleset;
def readDatasetSize(clueCount : int) -> int:
    global datasetPath;
    path = datasetPath + str(clueCount) + ".csv";
    if (not os.path.isfile(path)):
        return 0;
    f = open(path, "r");
    fileClueCount, fileSize = f.readline().rstrip().split(',');
    f.close();
    try:
        fileSize = int(fileSize);
        return fileSize;
    except ValueError:
        print("ERROR: Non-int size written in file '" + str(path) + "'"); os._exit(1);
###








######  Console  ######
usage = {"help":    "WIP: HELP",
         "load":    "Usage: load <dataset_clue_count> [<size_to_load>] [-o/-old]",
         "prnt":    "Usage: print [max_number] [-s/-size]\n\t-size: prints only dataset size.",
         "gen":     "Usage: generate <dataset_clue_count> <size_to_generate> [-o/-old] [-id:<int>] [-v/-verbose:<int>] [-p/-print] [(-m/-mark):<int>]" +
                    "\n\t-ID:      starting ID, default is from 0." +
                    "\n\t          '-id:read' reads existing data size as starting ID." +
                    "\n\t-verbose:\n\t\t0: nothing\n\t\t1: dots. \t\t(default)\n\t\t2: line counter.\n\t\t3: dots + line counter." + 
                    "\n\t-mark:    default is 10.",
        "save":     "Usage: save [-path:<str>] [-e/-eval] [-a/-append] [-f/-force] [-c/-clear]" +
                    "\n\t-eval:     save in the evaluation database. (overriden by '-path')"};
def mainconsole(commands = None):
    dataset = None;
    clueCount = -1;
    cc = -1 if commands == None else 0
    if (commands != None):
        print("------ AUTOMATED CONSOLE ------");
    while (True):
        if (cc == -1):
            inp = input("> ").split(' ');
        else:
            inp = commands[cc].split(' ');
            print("{0:3}".format(cc) + " > " + commands[cc]);
        # help
        if (inp[0].lower() in ["h", "help"]):
            if (len(inp) == 1):
                print("WIP: HELP");
            else:
                if (inp[1].lower() in ["l", "load"]):
                    print(usage["load"]);
                elif (inp[1].lower() in ["p", "print"]):
                    print(usage["prnt"]);
                elif (inp[1].lower() in ["g", "gen"]):
                    print(usage["gen"]);
                elif (inp[1].lower() in ["s", "save"]):
                    print(usage["save"]);
        # quit
        elif (inp[0].lower() in ["q", "quit"]):
            break;
        # load
        elif (inp[0].lower() in ["l", "load"]):
            if (len(inp) == 1 or not inp[1].isdigit()):
                print(usage["load"]);
            else:
                old = "-old" in inp or "-o" in inp;
                targetSize = (int(inp[2])) if (len(inp) > 2 and inp[2].isdigit()) else -1
                if (old):
                    dataset = loadDatasetOLD(81 - int(inp[1]), targetSize);
                else:
                    dataset = loadDataset(int(inp[1]), targetSize);
                if (dataset == None):
                    print("Operation failed.");
                else:
                    clueCount = int(inp[1]);
        # print current dataset
        elif (inp[0].lower() in ["p", "print"]):
            amount = -1;
            if (len(inp) > 1 and isInt(inp[1])):
                amount = int(inp[1]);
            sizeOnly = "-size" in inp or "-s" in inp;
            if (sizeOnly):
                print(0 if dataset == None else len(dataset));
            else:
                if (dataset == None):
                    print("No samples loaded.");
                else:
                    print("Dataset" + (("[:" + str(amount) + "]" if amount > 0 else "")) + ":");
                    if (amount > 0):
                        for i in range(amount): print("--  ",end=""); printSudokuSample(dataset[i]);
                    else:
                        for sample in dataset: print("--  ",end=""); printSudokuSample(sample);
        # save/write current dataset
        elif (inp[0].lower() in ["s", "save"]):
            evalSet = "-eval" in inp or "-e" in inp;
            path = (evaluatePath if evalSet else datasetPath);
            for i in inp:
                if (i.startswith("-path:")):
                    path = i[6:];
                    print("INFO: Saving inside " + path);
                elif (i.startswith("-p:")):
                    path = i[3:];
                    print("INFO: Saving inside " + path);
            append = "-append" in inp or "-a" in inp;
            force = "-force" in inp or "-f" in inp;
            clear = "-clear" in inp or "-c" in inp;
            if (dataset != None and clueCount != -1):
                saveWriteDataset(dataset, clueCount, path, append, force);
            if (clear):
                dataset = None; clueCount = -1;
                print("INFO: Cleared loaded dataset.");
        # clear
        elif (inp[0].lower() in ["c", "clear"]):
            dataset = None; clueCount = -1;
            print("INFO: Cleared loaded dataset.");
        # generate new dataset
        elif (inp[0].lower() in ["g", "generate", "gen"]):
            if (len(inp) < 3 or not inp[1].isdigit() or not inp[2].isdigit()):
                print(usage["gen"]);
            else:
                stop = False;
                # params
                clueCountInp = int(inp[1])
                # check if different clue count
                if (clueCount > -1 and clueCountInp != clueCount):
                    print("WARNING: Trying to generate samples of different clue count (" + str(clueCountInp) + " != " + str(clueCount) + "), aborting.");
                    stop = True;
                amount = int(inp[2])
                old = "-old" in inp or "-o" in inp;
                prnt = "-print" in inp or "-p" in inp;
                # print modes (verbose)
                v = 1;
                for i in inp:
                    if (i.startswith("-verbose:")):
                        v = i[9:];
                    elif (i.startswith("-v:")):
                        v = i[3:];
                if (v != 1):
                    try: v = int(v);
                    except ValueError: print("ERROR: Invalid verbose mode input (parsing)."); stop = True;
                    if (v < 0 or v > 3): print("ERROR: Invalid verbose mode input (OOR)."); stop = True;
                # id
                sID = -1
                for i in inp:
                    if (i.startswith("-id:")):
                        sID = i[4:];
                if (sID in ["read", "get"]):
                    # get from existing data, if it exists
                    sID = readDatasetSize(clueCountInp);
                if (sID != -1):
                    try: sID = int(sID);
                    except ValueError: print("ERROR: Invalid ID input (parsing)."); stop = True;
                else:
                    if (sID == -1): sID = 0 if (dataset == None or len(dataset) == 0 or dataset[-1].ID == -1) else (dataset[-1].ID + 1);
                # mark
                mark = 10
                for i in inp:
                    if (i.startswith("-mark:")):
                        mark = i[6:];
                    elif (i.startswith("-m:")):
                        mark = i[3:];
                if (mark != 10):
                    try: mark = int(mark);
                    except ValueError: print("ERROR: Invalid mark input."); stop = True;
                if (not stop):
                    # generation
                    if (dataset == None): dataset = [];
                    print("Generating " + str(amount) + " samples with " + str(clueCountInp) + " clues" + ((" (mark = " + str(mark) + "):\n" + ("   0 " if v > 1 else "")) if v > 0 else ":"), end="");
                    if (v == 0):
                        samples = generateSamplesFast(clueCountInp, amount, sID);
                        dataset.extend(samples);
                    else:
                        mi = 0;
                        for i in range(amount):
                            (puzzle, grid, removed) = generateFullSample(81 - clueCountInp);
                            if (prnt):
                                print("grid:   " + sprintGrid2D_Line(grid));
                                print("puzzle: " + sprintGrid2D_Line(puzzle));
                            sample = SudokuSample(sID + i, gridToArray(puzzle), gridToArray(grid), clueCountInp, -1.0)
                            dataset.append(sample);
                            if (v > 0):
                                if (i % mark == 0 and i > 0):
                                    if (v == 1): print("\n", end="");
                                    else: mi += 1; print("\n{0:4d} ".format(mi), end="");
                                if (v % 2 == 1): print('.', end="");
                    clueCount = clueCountInp;
                    print("\nDone.");
        # finish
        if (cc == -1):
            winsound.Beep(2500, 500)
        if (cc > -1):
            cc += 1;
            if (cc == len(commands)):
                print("------ CONSOLE DONE ------");
                winsound.Beep(4000, 500);
                break;
    return;

# console #
#if __name__ == "__main__":
#    global evaluatePath;
#    evaluatePath = "../dataset_eval/";
#    mainconsole();
#    os._exit(0);
