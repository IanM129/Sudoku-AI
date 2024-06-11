import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np
from time import time as time_time
from dataset import loadDataset
from sudoku import isSudokuValid, generateFullSample
from utility import gridToArray, minusOne
from tf_utility import gridToTensor, arrToTensor
from debug import sprintGrid2D, sprintTestSample, sprintEvalResult 

model = None;

######  Create model  ######
def createModel():
    model = keras.Sequential(
        [
            layers.Conv2D(64, kernel_size=(3,3), activation="relu", padding="same", input_shape=(9, 9, 1)),
            layers.BatchNormalization(),
            layers.Conv2D(64, kernel_size=(3,3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.Conv2D(128, kernel_size=(1,1), activation='relu', padding='same'),
            layers.Flatten(),
            layers.Dense(81 * 9),
            layers.Reshape((-1, 9)),
            layers.Activation("softmax")
        ]
    );
    model.compile(loss=keras.losses.SparseCategoricalCrossentropy(), #'sparse_categorical_crossentropy',
                  optimizer=keras.optimizers.Adam(learning_rate=0.001),
                  metrics=[keras.metrics.SparseCategoricalAccuracy()]); #['accuracy']);
    model.summary();
    return model;
######

############  TRAINING  ############
######  Utility  ######
def prepareSample(inputGrid : list[list[int]], solGrid : list[list[int]]) -> tuple[tf.Tensor, list[int]]:
    inputTensor = gridToTensor(minusOne(inputGrid, True));
    solution = tf.constant(minusOne(gridToArray(solGrid), False), dtype=tf.int32);
    return inputTensor, solution;
def prepareSampleArr(inputArr : list[int], solArr : list[int]) -> tuple[tf.Tensor, list[int]]:
    inputTensor = arrToTensor(minusOne(inputArr, False));
    solution = tf.constant(minusOne(solArr, False), dtype=tf.int32);
    return inputTensor, solution;
def generateTrainSample(missing = 44, debug = True):
    # create new puzzle
    (pzlGrid, solGrid, removed) = generateFullSample(missing);
    if (debug): print("starting full grid:"); print(sprintGrid2D(solGrid)); print("puzzle:"); print(sprintGrid2D(pzlGrid));
    # convert to tensors for inputting into model
    inputTensor, solution = prepareSample(pzlGrid, solGrid);
    if (debug): print("input tensor generated:"); print(inputTensor); print("solution final:"); print(solution);
    return inputTensor, solution;
def generateBatch(batchSize, missing = 44, debug = True):
    # create new batch
    feature = [None] * batchSize;
    label = [None] * batchSize;
    #feature = tf.zeros([batchSize, 9, 9, 1]);
    #label = tf.zeros([batchSize, 9, 9, 1]);
    for i in range(batchSize):
        #print("> ", i, ":");
        (feature[i], label[i]) = generateTrainSample(missing, debug);
        #print("> train #", i, ":\n", train[i], "\n> result #", i, ":\n", result[i]);
    return feature, label;
######
###### Save  ######
def saveModel(model, clueCount : int, amount : int, valRatio : int):
    path = "./models/final/" + str(clueCount) + "/";
    model.save_weights(path + str(clueCount));
    f = open(path + "/info.txt", "w");
    f.write("""
    clue count:                 {0}
    samples used:               {1}
    validation amount ratio:    1 // {2}  ({3:2.3}%)
            
    detailed sample use amount:
            testing:            {4:5}  ({5:2.3}%)
            validation:         {6:5}  ({7:2.3}%)
    """.format(clueCount, amount, valRatio, 1 / float(valRatio), 
               (amount - (amount // valRatio)), ((amount - (amount // valRatio))) / amount, 
               amount // valRatio, (amount // valRatio) / amount));
    f.close();
    return;
######
######  Main training  ######
# valuation data size in dataset = (1/valRatio) * dataset
def trainModel(model, clueCount : int, amount : int = -1, batchSize : int = 50, valRatio : int = 10) -> None:
    # check batchSize|amount
    if (amount != -1):
        if (batchSize > amount):
            print("WARNING: Given dataset size (" + str(amount) + ") is less than batch size (" + str(batchSize) + ").");
    # get dataset with given clue count
    dataset = loadDataset(clueCount, amount);
    if (amount == -1):
        amount = len(dataset);
        if (batchSize > amount):
            print("WARNING: Loaded dataset size (" + str(amount) + ") is less than batch size (" + str(batchSize) + ").");
    # seperate puzzles (features) and solutions (labels)
    feats = [];
    labels = [];
    for sample in dataset:
        feats.append(arrToTensor(sample.puzzle));   # -> tensor (9, 9)
        labels.append(sample.solution);             # -> [(1 - 9)] * 81
    print("Dataset size = " + str(len(feats)));
    print("Transforming for training...");
    # seperate to training and validation
    valCnt = len(feats) - (len(feats) // valRatio);
    train = (feats[:valCnt], labels[:valCnt]);
    val = (feats[valCnt:], labels[valCnt:]);
    train = ((tf.reshape(train[0], [len(train[0]), 9, 9, 1]) / 9) - 0.5,
                tf.reshape(train[1], [len(train[1]), 81, 1]) - 1);
    val = ((tf.reshape(val[0], [len(val[0]), 9, 9, 1]) / 9) - 0.5,
            tf.reshape(val[1], [len(val[1]), 81, 1]) - 1);
    print("Train set size = (" + str(len(train[0])) + ", " + str(len(train[1])) + "); validation set size = (" + str(len(val[0])) + ", " + str(len(val[1])) + ")");
    # train
    print("Training...");
    model.fit(train[0], train[1],
            validation_data=(val[0], val[1]),
            batch_size=batchSize, epochs=5, verbose=2);
    return amount;
def createSaveFullModel(clueCount : int, amount : int = -1, batchSize : int = 50, valRatio : int = 10):
    model = createModel();
    amount = trainModel(model, clueCount, amount, batchSize, valRatio);
    saveModel(model, clueCount, amount, valRatio);
    return model;
######
############

############  LOADING AND EVAL  ############
######  Utility  ######
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
######
######  Load model  ######
def loadModel(clueCount : int):
    global model;
    # Restore the weights
    model = createModel();
    model.load_weights('./models/final/' + str(clueCount) + "/" + str(clueCount)).expect_partial();
    return model;
"""
def loadModelOLD():
    global model;
    # Restore the weights
    model = createModel();
    model.load_weights('./models/base/44');
"""
######
######  Evaluate  ######
def solveTest(inputTensor, solution, debug = 2, altModel = None):
    global model;
    if (altModel != None):
        lastModel = model;
        model = altModel;
    elif (model == None): print("! WARNING: Calling solveTest() with no model loaded!"); loadModel();
    
    if (debug == 2): print("------ Solving test:");
    
    inputTensor = tf.reshape(inputTensor, [1, 9, 9, 1]);
    solution = tf.reshape(solution, [1, 81, 1]);

    if (debug == 2): print(sprintTestSample(inputTensor[0], solution[0].numpy()));
    if (debug == 2): print("Solving...  ", end="");

    # predict
    success = False;
    initial_board = np.array(inputTensor).reshape([9, 9, 1]);
    initial_board = ((initial_board) / 9) - 0.5;
    # start timer
    start = time_time();
    # main solving loop
    for i in range(162):
        predictions = model.predict(initial_board.reshape([1, 9, 9, 1]), verbose=0).squeeze();

        pred = np.argmax(predictions, axis=1).reshape([9, 9]) + 1;
        prob = np.around(np.max(predictions, axis=1).reshape([9, 9]), 2);

        initial_board = ((initial_board + 0.5) * 9).reshape([9, 9]);
        mask = (initial_board == 0);

        if (mask.sum() == 0):
            #if (debug == 2): print("All missing values chosen.");
            success = True;
            break;
    
        prob_new = prob * mask;
 
        ind = np.argmax(prob_new);
        y, x = (ind // 9), (ind % 9);
 
        val = pred[y][x];
        initial_board[y][x] = val;
        initial_board = (initial_board / 9) - 0.5;
    # end timer
    end = time_time();
    duration = end - start;
    # finish
    if (not success):
        if (debug == 2): print("Error");
    puzzle = tf.reshape(inputTensor, [9, 9]).numpy();
    solution_grid = tf.reshape(solution, [9, 9]).numpy();
    if (debug > 0):
        correct, size, accGrid = calculateAccuracy(puzzle, solution_grid, initial_board);
        valid = isSudokuValid(initial_board, True);
        print("- accuracy (label):      %.2f" % ((correct / size) * 100), end="");
        print("% (" + str(correct) + " / " + str(size) + ");");
        print("           (validity):   %.2f" % ((valid / 81) * 100), end="");
        print("% (" + str(valid) + " / 81);");
        if (debug == 2):
            print("- result:\n" + sprintEvalResult(solution_grid, initial_board, accGrid));
            print("------");
        if (valid == 81):
            print("Sudoku valid.");
    # retrieve actual model
    if (altModel != None): model = lastModel;
    return initial_board, success, duration;
######
############











######  Run  ######
if __name__ == "__main__":
    print("TensorFlow version:", tf.version);
    
    train = False;
    test = False;

    # train model
    if (train):
        createSaveFullModel(clueCount=30);
    # test model
    if (test):
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
            (inputTensor, solution) = generateTrainSample(missing, False);
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
