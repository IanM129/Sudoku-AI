from tkinter import font as tkFont
import tkinter as tk
from tkinter import simpledialog
from functools import partial
from bot_train import createModel
from bot_load import prepareSample, solveTest
from sudoku import generateFullSample
from sudoku_window import openSample, colorCells
from utility import floatGridToIntGrid, findInvalidCells, gridToIndeces, getExclusion

# => ((button, button, label), (inputGrid, solGrid, invalid list) = 'test', name)
testLogs = [];
openTemp = [];
valPzlCnt = 0;
valCellCnt = 0;
count = 0;

missing = 44;

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
    statsLbl.config(text=("- " * 14) + " overall accuracy " + (" -" * 14) + "\n" +
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

def addTest(test, testName, doRefresh = True):
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
    tbtn.config(text=(testName + "Test #" + str(row)), compound="c", font=("Helvetica", 12, "bold"));
    tbtn.grid(row=row, column=1, padx=(0, 20), pady=2);
    # result button
    rbtn = tk.Button(frame, image=pixelPic, command=partial(openResult, row - 1));
    rbtn.config(width=winWid * 0.3, height=25);
    rbtn.config(text=(testName + "Result #" + str(row)), compound="c", font=("Helvetica", 12, "bold"));
    rbtn.grid(row=row, column=2, padx=(0, 20), pady=2);
    # label frame
    lblFrm = tk.Frame(frame);
    lblFrm.grid(row=row, column=3);
    lblFrm.grid_columnconfigure(1, weight=10, minsize=100)
    lblFrm.grid_columnconfigure(2, weight=1, minsize=80)
    # validity label
    testInfoFont = tkFont.Font(family='Helvetica', size=12);
    vLbl = tk.Label(lblFrm, font=testInfoFont);
    if (len(test[2]) == 0):
        vLbl.config(text="valid",fg="green");
    else:
        vLbl.config(text="invalid",fg="red");
    vLbl.grid(row=1,column=1);
    # rest of the text label
    tLbl = tk.Label(lblFrm, font=testInfoFont,
                    text=(str(missing - len(test[2])) + " / " + str(missing)));
    tLbl.grid(row=1,column=2);
    # add to count
    global valPzlCnt;  global valCellCnt; global count;
    if (len(test[2]) == 0): valPzlCnt += 1;
    valCellCnt += missing - len(test[2]);
    count += missing;
    # add to log
    testLogs.append(((tbtn, rbtn, lblFrm), test, testName));
    if (doRefresh): refresh();
    return;

def runTest(model = None):
    showStats(False);
    # generate test
    (inputGrid, solGrid, removedCells) = generateFullSample(missing);
    (inputTensor, solTensor) = prepareSample(inputGrid, solGrid);
    # run test
    (board, success, corCnt, valid) = solveTest(inputTensor, solTensor, 0, model);
    board = floatGridToIntGrid(board);
    #global tempSudoku;
    #valid = isSudokuValid(board, True);
    invalid = findInvalidCells(board);
    invalid = getExclusion(invalid, gridToIndeces(inputGrid));
    return (inputGrid, board, invalid);
def runTests(count):
    # progress label
    showStartInfo(False);
    showStats(False);
    showProgLbl(True);
    #curRow = len(testLogs) + 1;
    #progLbl.grid(row=curRow, column=1, columnspan=2);
    win.update();
    # run tests
    for i in range(count):
        win.title("Sudoku AI evaluation (*working* " + str(i + 1) + "/" + str(count) + ")");
        test = runTest();
        #curRow += 1;
        showProgLbl(True); #progLbl.grid(row=curRow, column=1, columnspan=2);
        addTest(test, "");
    win.title("Sudoku AI evaluation");
    showProgLbl(False); #progLbl.destroy();
    #updateStats();
    showStats(True);
    return;
def runTestsCustom():
    win.withdraw();
    # input dialog
    num = simpledialog.askinteger(title="Run custom...", prompt="Number of tests:");
    win.deiconify();
    if (num > 0): runTests(num);
    return;

## Special
def runTestBlankModel():
    showStats(False);
    showProgLbl(True);
    win.update();
    model = createModel();
    test = runTest(model);
    addTest(test, "(Blank)");
    showProgLbl(False);
    showStats(True);
    refresh();
    
def newWindow():
    global win;
    win = tk.Tk();
    win.geometry("800x800");
    win.title("Sudoku AI evaluation");
    # outer frame
    outerFrm = tk.Frame(win)
    outerFrm.pack(fill=tk.BOTH, expand=1);
    # main canvas
    global mainCnv;
    mainCnv = tk.Canvas(outerFrm);
    mainCnv.pack(side=tk.LEFT, fill=tk.BOTH, expand=1);
    # scrollbar
    scrlBar = tk.Scrollbar(outerFrm, orient=tk.VERTICAL, command=mainCnv.yview);
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
    frame.columnconfigure(3, weight=1);
    mainCnv.create_window((0, 0), window=frame, anchor="nw");
    #toolbar
    toolbar = tk.Menu(win, tearoff=0);
    win.config(menu=toolbar);
    runmenu = tk.Menu(toolbar, tearoff=0)
    runmenu.add_command(label="Run 1", command=partial(runTests, 1));
    runmenu.add_command(label="Run 5", command=partial(runTests, 5));
    runmenu.add_command(label="Run 10", command=partial(runTests, 10));
    runmenu.add_command(label="Run 100", command=partial(runTests, 100));
    runmenu.add_separator();
    runmenu.add_command(label="Run custom...", command=runTestsCustom);
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
                        text=("- " * 80) + "\noverall accuracy: 0%");
    #statsLbl.grid(row=1,column=1,columnspan=2);
    # constants
    global pixelPic;
    pixelPic = tk.PhotoImage(width=1, height=1);
    refresh();


if __name__ == "__main__":
    newWindow();
    win.mainloop();
