# Standard library
import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1';
from tkinter import font as tkFont
import tkinter as tk
from tkinter import simpledialog
from random import randint
from time import time as time_time
from functools import partial

# Custom
from modules.bot import prepareSample, prepareSampleArr, createModel, loadModel, solveTest
from modules.dataset import loadEvalSet
from modules.sudoku import generateFullSample, solveGrid, isSudokuValid
from modules.sudoku_window import openSample, colorCells
from modules.utility import floatGridToIntGrid, findInvalidCells, gridToIndeces, getExclusion, arrToGrid

# => ((button, button, label), (inputGrid, solGrid, invalid list) = 'test', name)
testLogs = [];
openTemp = [];
valPzlCnt = 0;
valCellCnt = 0;
count = 0;

missing = 44;

## Globals loaded:
# model

## StringVars:
modelNames = ["blank"];
modelNames += [name for name in os.listdir("./models/final/") if name.isdigit()];
# modelChosen       - chosen clue count for trained model
diffList = [i for i in range(20, 81)];
# diffChosen        - chosen clue count for puzzle
# testCountInput
# loadFromDSVar

def showStartInfo(val):
    global openInfoLbl;
    if (val == True):
        openInfoLbl.config(state=tk.NORMAL);
        openInfoLbl.grid(columnspan=2);
    else:
        openInfoLbl.config(state=tk.DISABLED);
        openInfoLbl.grid_forget();
def showProgLbl(val):
    global progLbl;
    if (val == True):
        progLbl.grid(row=(len(testLogs) + 2), column=1, columnspan=2);
    else:
        progLbl.grid_forget();
def showStats(val):
    global statsLbl;
    if (val == True):
        statsLbl.config(state=tk.NORMAL);
        statsLbl.grid(row=len(testLogs) + 1, column=1, columnspan=3);
    else:
        statsLbl.config(state=tk.DISABLED);
        statsLbl.grid_forget();
def updateStats():
    global valPzlCnt; global valCellCnt; global count;
    statsLbl.config(text=("- " * 17) + " overall accuracy " + (" -" * 17) + "\n" +
                    ("{}  {:6.2f}% {:52s}".format("puzzles", ((valPzlCnt / len(testLogs)) * 100),
                     str("(" + str(valPzlCnt) + "/" + str(len(testLogs)) + ")"))) + "\n" +
                    ("{}  {:6.2f}% {:52s}".format("cells  ", ((valCellCnt / count) * 100),
                     str("(" + str(valCellCnt) + "/" + str(count) + ")"))));
def refresh():
    global testLogs;
    # hide/show info and stats label
    global openInfoLbl;
    global statsLbl;
    if (len(testLogs) > 0):
        if (openInfoLbl["state"] == tk.NORMAL): showStartInfo(False);
        #if (statsLbl["state"] == tk.DISABLED): showStats(True);
    elif (len(testLogs) == 0):
        if (openInfoLbl["state"] == tk.DISABLED): showStartInfo(True);
        if (statsLbl["state"] == tk.NORMAL): showStats(False);
    # stats update
    if (count > 0):
        updateStats();
    # win update
    global mainCnv;
    mainCnv.configure(scrollregion=mainCnv.bbox("all"));
    win.update();
    return;

def openTest(index):
    global openTemp;
    (sudokuGrid, photo) = openSample(testLogs[index][1][0],
                                     testLogs[index][2] + "Test #" + str(index + 1), "gray");
    openTemp.append((sudokuGrid, photo));
    return;
def openResult(index):
    global openTemp;
    (sudokuGrid, photo) = openSample(testLogs[index][1][1],
                                     testLogs[index][2] + "Result #" + str(index + 1), "black");
    colorCells(sudokuGrid, testLogs[index][1][2], "red");
    colorCells(sudokuGrid, gridToIndeces(testLogs[index][1][0]), "gray");
    openTemp.append((sudokuGrid, photo));
    return;

def clearLog():
    global testLogs;
    for i in range(len(testLogs)):
        for j in range(3):
            testLogs[i][0][j].destroy();
    testLogs = [];
    global valPzlCnt; global valCellCnt; global count;
    valPzlCnt = 0;
    valCellCnt = 0;
    count = 0;
    refresh();
    return;

def addTest(test, clueCount : int, testName : str, Id : int = -1, doRefresh : bool = True) -> None:
    global frame;
    global testLogs;
    testName += " ";
    # create tkinter element
    winWid = win.winfo_width();
    row = len(testLogs) + 1;
    # test button
    global pixelPic;
    tbtn = tk.Button(frame, image=pixelPic, command=partial(openTest, row - 1));
    tbtn.config(width=winWid * 0.3, height=25);
    global modelChosen;
    fullName = testName + "Test #" + str(row) + " (" + ("/" if modelChosen.get() == "blank" else str(modelChosen.get())) + " : " + str(clueCount) + ((" [" + str(Id) + "]" if Id != -1 else "")) + ")";
    tbtn.config(text=fullName, compound="c", font=("Helvetica", 12, "bold"));
    tbtn.grid(row=row, column=1, padx=(10, 10), pady=2);
    # result button
    rbtn = tk.Button(frame, image=pixelPic, command=partial(openResult, row - 1));
    rbtn.config(width=winWid * 0.3, height=25);
    rbtn.config(text=(testName + "Result #" + str(row)), compound="c", font=("Helvetica", 12, "bold"));
    rbtn.grid(row=row, column=2, padx=(0, 10), pady=2);
    # label frame
    lblFrm = tk.Frame(frame);
    lblFrm.grid(row=row, column=3);
    lblFrm.grid_columnconfigure(1, weight=8, minsize=60)    # validity
    lblFrm.grid_columnconfigure(2, weight=8, minsize=80)    # accuracy
    lblFrm.grid_columnconfigure(3, weight=10, minsize=80)   # time
    lblFrm.grid_columnconfigure(4, weight=10, minsize=80)   # run alg / alg time
    # validity label
    testInfoFont = tkFont.Font(family='Helvetica', size=12);
    vLbl = tk.Label(lblFrm, font=testInfoFont);
    if (len(test[2]) == 0):
        vLbl.config(text="valid",fg="green");
    else:
        vLbl.config(text="invalid",fg="red");
    vLbl.grid(row=1,column=1);
    # full accuracy label
    missing = 81 - clueCount;
    aLbl = tk.Label(lblFrm, font=testInfoFont,
                    text=(str(missing - len(test[2])) + " / " + str(missing)));
    aLbl.grid(row=1,column=2);
    # timer label
    tLbl = tk.Label(lblFrm, font=testInfoFont,
                    text="{:.2f} ms".format(test[3] * 1000));
    tLbl.grid(row=1,column=3);
    # run algorithm button
    testInd = len(testLogs);
    solveEl = tk.Button(lblFrm, text="Run alg.", command= lambda: solveWithAlgorithm(testInd));
    solveEl.grid(row=1,column=4);
    # add to count
    global valPzlCnt; global valCellCnt; global count;
    if (len(test[2]) == 0): valPzlCnt += 1;
    valCellCnt += missing - len(test[2]);
    count += missing;
    # add to log
    testLogs.append(((tbtn, rbtn, lblFrm, solveEl), test, testName));
    if (doRefresh): refresh();
    return;

def runTest(clueCount, load : list[int] = [0], model = None):
    showStats(False);
    if (load[0]):
        # load test
        evalset = loadEvalSet(clueCount);
        r = randint(0, len(evalset) - 1);
        sample = evalset[r];
        load[0] = r;
        inputGrid = arrToGrid(sample.puzzle);
        inputTensor, solTensor = prepareSampleArr(sample.puzzle, sample.solution);
    else:
        # generate test
        (inputGrid, solGrid, removedCells) = generateFullSample(81 - clueCount);
        (inputTensor, solTensor) = prepareSample(inputGrid, solGrid);
    # run test
    (board, success, duration) = solveTest(inputTensor, solTensor, 0, model);
    board = floatGridToIntGrid(board);
    #global tempSudoku;
    #valid = isSudokuValid(board, True);
    invalid = findInvalidCells(board);
    invalid = getExclusion(invalid, gridToIndeces(inputGrid));
    return (inputGrid, board, invalid, duration);
def runTests(clueCount, count, load = False):
    # progress label
    showStartInfo(False);
    showStats(False);
    showProgLbl(True);
    win.update();
    # run tests
    for i in range(count):
        win.title("Sudoku AI evaluation (*working* " + str(i + 1) + "/" + str(count) + ")");
        id = [1] if load else [0];
        test = runTest(clueCount, id);
        showProgLbl(True);
        addTest(test, clueCount, "", id[0] if load else -1);
    win.title("Sudoku AI evaluation");
    showProgLbl(False);
    showStats(True);
    return;
def runTestsCustom():
    win.withdraw();
    # input dialog
    num = simpledialog.askinteger(title="Run custom...", prompt="Number of tests:");
    win.deiconify();
    if (num > 0): runTests(num);
    return;
def getCurrentParams():
    global testCountInput;
    testCnt = int(testCountInput.get());
    global diffChosen;
    numOfClues = int(diffChosen.get());
    global loadFromDSVar;
    load = loadFromDSVar.get() and genLoadCb["state"] != "disabled";
    return (testCnt, numOfClues, load);

## Special
def runTestBlankModel():
    showStats(False);
    showProgLbl(True);
    win.update();
    model = createModel();
    modelChosen.set("blank");
    _, numOfClues, load = getCurrentParams();
    id = [1] if load else [0];
    test = runTest(numOfClues, id, model);
    addTest(test, numOfClues, "(Blank)", id[0] if load else -1);
    showProgLbl(False);
    showStats(True);
    refresh();
    return;
def solveWithAlgorithm(testInd : int):
    global testLogs;
    testLog = testLogs[testInd];
    valid = False;
    for i in range(10):
        grid = [];
        for y in range(9):
            grid.append([None] * 9);
            for x in range(9):
                if (testLog[1][0][y][x] != 0): grid[y][x] = testLog[1][0][y][x];
        start = time_time();
        solved = solveGrid(grid, True);
        end = time_time();
        valid = isSudokuValid(grid);
        if (valid == True): break;
    duration = end - start;
    #((tbtn, rbtn, lblFrm, solveEl), test, testName)
    # Update UI element
    uiEl = testLog[0][3];
    uiEl.grid_forget();
    testInfoFont = tkFont.Font(family='Helvetica', size=12);
    uiEl = tk.Label(testLog[0][2],font=testInfoFont, text=("{:.2f} ms".format(duration * 1000) if valid else "ERR"));
    uiEl.grid(row=1,column=4);
    return;





### INTERFACE
def toggle(target):
    if target['state'] == "active":
        target['state'] = "normal";
    else:        
        target['state'] = "active";
    return
def modelSel(value):
    if (value == "blank"):
        global model;
        model = createModel();
    else: loadModel(int(value));
    return;
def inputCntVal(input):
    if (not input.isdigit() or input == ""):
        return False;
    return int(input) > -1 and int(input) < 1001;
def clueCountSelected(value, diffSelFrm):
    global genLoadCb;
    genLoadCb.destroy();
    if (os.path.isfile("./dataset_eval/" + str(value) + ".csv")):
        global loadFromDSVar;
        genLoadCb = tk.Checkbutton(diffSelFrm, text="Load", indicatoron=True, variable=loadFromDSVar);
        genLoadCb.pack(anchor="s", side=tk.RIGHT);
    else:
        genLoadCb = tk.Checkbutton(diffSelFrm, text="No dataset", state="disabled");
        genLoadCb.pack(anchor="s", side=tk.RIGHT);   
    return
def runBtnCmnd():
    if (modelChosen.get() == "blank"): runTestBlankModel();
    else:
        testCnt, numOfClues, load = getCurrentParams();
        runTests(numOfClues, testCnt, load);
    return;
def newWindow():
    global win;
    win = tk.Tk();
    win.geometry("900x900");
    win.title("Sudoku AI evaluation");
    win.resizable(True, False);
    
    #win.grid_rowconfigure(0, weight = 2);
    #win.grid_rowconfigure(1, weight = 1);
    #win.grid_rowconfigure(2, weight = 50);
    #win.grid_columnconfigure(0, weight = 1);
    
    # outer frame
    #outerFrm = tk.Frame(win)
    #outerFrm.pack(fill=tk.BOTH, expand=1);
    # test setup menu frame (top)
    upperFrm = tk.Frame(win, height=60)
    upperFrm.pack(side=tk.TOP, fill=tk.X, expand=False);#grid(row=0, column=0, sticky='nesw');

    upperFrm.grid_rowconfigure(0, weight = 1);
    #upperFrm.grid_rowconfigure(1, weight = 1);
    upperFrm.grid_columnconfigure(0, weight = 1);
    upperFrm.grid_columnconfigure(1, weight = 1);
    upperFrm.grid_columnconfigure(2, weight = 1);
    upperFrm.grid_columnconfigure(3, weight = 1);
    
    # model selection dropdown
    modelSelFrm = tk.Frame(upperFrm);
    modelSelFrm.grid(row=0, column=0);
    modelSelLbl = tk.Label(modelSelFrm, text="Model:");
    modelSelLbl.pack(side=tk.TOP);
    global modelNames;
    global modelChosen;
    modelChosen = tk.StringVar(upperFrm);
    modelChosen.set(modelNames[0]);
    modelSelDd = tk.OptionMenu(modelSelFrm, modelChosen, *modelNames, command=modelSel);
    modelSel(modelChosen.get());
    modelSelDd.pack(side=tk.BOTTOM);
    # difficulty selection dropdown
    diffSelFrm = tk.Frame(upperFrm);
    diffSelFrm.grid(row=0, column=1);
    diffSelLbl = tk.Label(diffSelFrm, text="Number of clues:");
    diffSelLbl.pack();
    global diffList;
    global diffChosen;
    diffChosen = tk.StringVar(upperFrm);
    diffChosen.set("50");
    #diffSelFrm = tk.Frame(upperFrm);
    #diffSelFrm.grid(row=1, column=1);
    global genLoadCb;
    global loadFromDSVar;
    loadFromDSVar = tk.BooleanVar();
    genLoadCb = tk.Checkbutton(diffSelFrm, text="Load", variable=loadFromDSVar);
    diffSelDd = tk.OptionMenu(diffSelFrm, diffChosen, *diffList,
                              command= lambda e: clueCountSelected(diffChosen.get(), diffSelFrm));
    clueCountSelected(diffChosen.get(), diffSelFrm);
    diffSelDd.pack(anchor="s", side=tk.LEFT);
    genLoadCb.pack(anchor="s", side=tk.RIGHT);
    # amount
    runAmFrm = tk.Frame(upperFrm);
    runAmFrm.grid(row=0, column=2);
    runAmLbl = tk.Label(runAmFrm, text="Number of tests:");
    runAmLbl.pack(side=tk.TOP);
    regVal=win.register(inputCntVal);
    global testCountInput;
    testCountInput = tk.StringVar();
    testCountInput.set("1");
    runAmInp = tk.Entry(runAmFrm, textvariable=testCountInput);
    runAmInp.config(validate="key", validatecommand=(regVal, '%P'));
    runAmInp.pack(side=tk.BOTTOM);
    # run button
    runBtn = tk.Button(upperFrm, text="  Run  ", command=runBtnCmnd);
    runBtn.grid(row=0, column=3);

    # seperator
    midFrm = tk.Frame(win, bg="black", height=4);
    midFrm.pack(fill=tk.X, expand=False); #grid(row=1, column=0, sticky='nesw');
    # done tests frame (bottom)
    bottomFrm = tk.Frame(win);
    bottomFrm.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True); #grid(row=2, column=0, sticky='nesw');
    # main canvas
    global mainCnv;
    mainCnv = tk.Canvas(bottomFrm);
    mainCnv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1);
    # scrollbar
    scrlBar = tk.Scrollbar(bottomFrm, orient=tk.VERTICAL, command=mainCnv.yview);
    scrlBar.pack(side=tk.RIGHT, fill=tk.Y);
    # connect
    mainCnv.config(yscrollcommand = scrlBar.set);
    mainCnv.bind(
        '<Configure>', lambda e: mainCnv.configure(scrollregion=mainCnv.bbox("all")));
    # main frame (inside canvas)
    global frame;
    frame = tk.Frame(mainCnv);
    frame.columnconfigure(1, weight=1);
    frame.columnconfigure(2, weight=1);
    frame.columnconfigure(3, weight=2);
    mainCnv.create_window((0, 0), window=frame, anchor="nw");
    #toolbar
    toolbar = tk.Menu(win, tearoff=0);
    win.config(menu=toolbar);
    # model selection option menu
    #modelmenu = tk.OptionMenu(toolbar, tearoff=0);
    # run menu
    runmenu = tk.Menu(toolbar, tearoff=0)
    runmenu.add_command(label="Run 1", command=partial(runTests, 1));
    runmenu.add_command(label="Run 5", command=partial(runTests, 5));
    runmenu.add_command(label="Run 10", command=partial(runTests, 10));
    runmenu.add_command(label="Run 100", command=partial(runTests, 100));
    runmenu.add_separator();
    runmenu.add_command(label="Run custom...", command=runTestsCustom);
    # add to toolbar
    toolbar.add_cascade(label="Run", underline=0, menu=runmenu);
    toolbar.add_command(label="Run blank test", command=runTestBlankModel);
    toolbar.add_command(label="Clear log", command=clearLog);
    toolbar.add_command(label="Exit", command=win.destroy);
    # info
    infoFont = tkFont.Font(family='Helvetica', size=24, weight='bold');
    global openInfoLbl;
    openInfoLbl = tk.Label(frame, text="Run a test from the toolbar to start.", font=infoFont);
    openInfoLbl.grid(row=1,column=1,columnspan=2);
    # prog label
    global progLbl;
    progLbl = tk.Label(frame, text="...", font=("Helvetica", 12, "bold"));
    # stats
    global statsLbl;
    statsLbl = tk.Label(frame, font=("Lucida Sans Typewriter", 12, "bold"),
                        text=("- " * 90) + "\noverall accuracy: 0%");
    #statsLbl.grid(row=1,column=1,columnspan=2);
    # constants
    global pixelPic;
    pixelPic = tk.PhotoImage(width=1, height=1);
    refresh();


if __name__ == "__main__":
    newWindow();
    win.mainloop();
