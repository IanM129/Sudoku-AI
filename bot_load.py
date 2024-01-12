import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
from bot_train import newTrainSample, createModel, sprintSample
from sudoku import isSudokuValid
from utility import gridToTensor, gridToArray, minusOne

model = None;

## DEBUG
def sprintResult(puzzle, result, accGrid):
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

## UTILITY
def calculateAccuracy(puzzle, solution, result):
    grid = [];
    count = 0;
    correct = 0;
    for y in range(9):
        grid.append([]);
        for x in range(9):
            if (puzzle[y][x] != 0):                         # known
                grid[y].append(".");
            else:                                           # calculated
                delta = solution[y][x] - int(result[y][x]);
                if (delta == 0):                            # correct
                    grid[y].append("O");
                    correct += 1;
                else:                                       # incorrect
                    #if (delta < 0): delta = -delta;
                    grid[y].append(int(result[y][x]));
                count += 1;
    return correct, count, grid;

def prepareSample(inputGrid, solGrid):
    inputTensor = gridToTensor(minusOne(inputGrid, True));
    solution = tf.constant(minusOne(gridToArray(solGrid), False), dtype=tf.int32);
    return inputTensor, solution;


## MAIN
def loadModel():
    global model;
    # Restore the weights
    model = createModel();
    model.load_weights('./models/first/first');
def solveTest(inputTensor, solution, debug = 2, altModel = None):
    global model;
    if (altModel != None):
        lastModel = model;
        model = altModel;
    elif (model == None): loadModel();
    
    if (debug == 2): print("------ Solving test:");
    
    inputTensor = tf.reshape(inputTensor, [1, 9, 9, 1]);
    solution = tf.reshape(solution, [1, 81, 1]);

    if (debug == 2): print(sprintSample(inputTensor[0], solution[0].numpy()));
    if (debug == 2): print("Solving...  ", end="");

    # predict
    success = False;
    initial_board = np.array(inputTensor).reshape([9, 9, 1]);
    initial_board = ((initial_board) / 9) - 0.5;
    #print(initial_board);
    for i in range(100):
        predictions = model.predict(initial_board.reshape([1, 9, 9, 1]), verbose=0).squeeze();

        pred = np.argmax(predictions, axis=1).reshape([9, 9]) + 1;
        prob = np.around(np.max(predictions, axis=1).reshape([9, 9]), 2);

        initial_board = ((initial_board + 0.5) * 9).reshape([9, 9]);
        mask = (initial_board == 0);

        if (mask.sum() == 0):
            if (debug == 2): print("All missing values chosen.");
            success = True;
            break;
    
        prob_new = prob * mask;
 
        ind = np.argmax(prob_new);
        y, x = (ind // 9), (ind % 9);
 
        val = pred[y][x];
        initial_board[y][x] = val;
        #print(initial_board);
        initial_board = (initial_board / 9) - 0.5;

    #print(initial_board);
    #tf.reshape(initial_board, [9, 9]);
    if (not success):
        if (debug == 2): print("Error");
    puzzle = tf.reshape(inputTensor, [9, 9]).numpy();
    solution_grid = tf.reshape(solution, [9, 9]).numpy();
    correct, size, accGrid = calculateAccuracy(puzzle, solution_grid, initial_board);
    valid = isSudokuValid(initial_board, True);
    if (debug > 0):
        print("- accuracy (label):      %.2f" % ((correct / size) * 100), end="");
        print("% (" + str(correct) + " / " + str(size) + ");");
        print("           (validity):   %.2f" % ((valid / 81) * 100), end="");
        print("% (" + str(valid) + " / 81);");
    if (debug == 2):
        print("- result:\n" + sprintResult(solution_grid, initial_board, accGrid));
        print("------");
    if (debug > 0 and valid == 81):
        print("Sudoku valid.");
    # retrieve actual model
    if (altModel != None):
        model = lastModel;
    return initial_board, success, correct, valid;



if __name__ == "__main__":
    print("TensorFlow version:", tf.version);
    
    # Restore the weights
    loadModel();
    
    missing = 44;
    testCount = 10;
    corCells = 0;
    validPzls = 0;
    debug = 2;      # 0 - none, 1 - accuracy, 2 - full
    evalType = 1;   # 0 - bool, 1 - valid count
    for i in range(testCount):
        print(str(i + 1) + "/" + str(testCount));
        (inputTensor, solution) = newTrainSample(missing, False);
        (result, success, corCnt, valid) = solveTest(inputTensor, solution, debug);
        if (evalType == 0): corCells += corCnt;
        elif (evalType == 1): corCells += valid;
        if ((evalType == 0 and valid) or (valid == 81)): validPzls += 1;
        if (debug > 0): print("");
    if (evalType == 0):
        corCellsPc = (corCells / (missing * testCount)) * 100;
    elif (evalType == 1):
        corCellsPc = (corCells / (81 * testCount)) * 100;
    print(("\nAll tests done, overall accuracy: cells %.2f" %
          corCellsPc) + "% (" + str(corCells) + " / ", end="");
    if (evalType == 0):
        print(str(missing * testCount) + ")");
    elif (evalType == 1):
        print(str(81 * testCount) + ")");
    print("                                  puzzles %.2f" %
          ((validPzls / testCount) * 100), end="");
    print("% (" + str(validPzls) + " / " + str(testCount) + ")");
