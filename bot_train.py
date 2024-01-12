import tensorflow as tf
from tensorflow import sparse as tfSparse
from tensorflow import keras
from keras import layers
import numpy as np
import os
import random
from datetime import datetime
from sudoku import generateRandomGrid, generatePuzzle, sprintGrid, sprintGrid2D
from utility import gridToTensor, gridToArray, minusOne

## DEBUG
def sprintSample(x, y):
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

## CREATE MODEL
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

## CONVERT
# puzzle = (grid, solution)
def puzzleToText(puzzle):
    # write grid
    txt = "";
    grid = puzzle[0].numpy();
    first = True;
    for row in grid:
        for n in row:
            if (not first): txt += ",";
            else: first = False;
            txt += str(n);
    txt += "\n";
    # write solution
    sol = puzzle[1].numpy();
    first = True;
    for n in sol:
        if (not first): txt += ",";
        else: first = False;
        txt += str(n);
    txt += "\n";
    return txt;
def textToPuzzle(gridTxt, solTxt):
    # grid
    gridArr = gridTxt.split(',');
    grid = [];
    for y in range(9):
        grid.append([]);
        for x in range(9):
            grid[y].append(int(gridArr[9*y + x]));
    inputTensor = tf.constant(grid);
    # solution
    solArr = solTxt.split(',');
    solution = [];
    for i in range(81):
        solution.append(int(solArr[i]));
    return inputTensor, solution;

## UTILITY
def newTrainSample(missing = 44, debug = True):
    # create new puzzle
    newGrid = generateRandomGrid();
    if (debug):
        print("starting full grid:");
        print(sprintGrid2D(newGrid));
    # create solution tensor
    solution = tf.constant(minusOne(gridToArray(newGrid), False), dtype=tf.int32);
    # create puzzle
    (newGrid, removed) = generatePuzzle(newGrid, missing);
    # create input tensor
    #inputTensor = newGrid.copy();
    inputTensor = gridToTensor(minusOne(newGrid, True));
    if (debug):
        print("input tensor generated:");
        print(inputTensor);
        print("solution final:");
        print(solution);
    return inputTensor, solution;
def newTrainBatch(batchSize, missing = 44, debug = True):
    # create new batch
    train = [None] * batchSize;
    result = [None] * batchSize;
    #train = tf.zeros([batchSize, 9, 9, 1]);
    #result = tf.zeros([batchSize, 9, 9, 1]);
    for i in range(batchSize):
        #print("> ", i, ":");
        (train[i], result[i]) = newTrainSample(missing, debug);
        #print("> train #", i, ":\n", train[i], "\n> result #", i, ":\n", result[i]);
    return train, result;

#### MAIN
# test = batch
def saveTests(path, tests, missing, debug = True):
    # load info
    nxtId = 0;
    infoPath = path + "/info.txt";
    if (os.path.isfile(infoPath)):
        info = open(infoPath, "r");
        nxtId = int(info.readline());
        #nxtId += 1;
        info.close();
    # save
    savePath = path + "/";
    firstId = nxtId;
    for i in range(len(tests)):
        f = open(savePath + "test_" + str(nxtId) + ".csv", "w");
        nxtId += 1;
        f.write(str(missing) + "," + str(len(tests[i])) + "\n");
        for p in tests[i]:
            r = puzzleToText(p);
            f.write(r + "\n");
        f.close();
    # save debug grid showcase
    if (debug):
        for i in range(len(tests)):
            f = open(savePath + "test_" + str(firstId + i) + ".csv", "a");
            f.write("\n\n-- user friendly:\n");
            for p in range(len(tests[i])):
                f.write("#" + str(p + 1) + "\n");
                f.write(sprintGrid(tests[i][p][1].numpy()) + "\n\n");
            f.close();
    # write in info
    lines = [];
    if (os.path.isfile(infoPath)):
        info_r = open(infoPath, "r");
        lines = info_r.readlines();
        info_r.close();
    info = open(infoPath, "w");
    info.write(str(nxtId));
    info.write("\n");
    for i in range(1, len(lines)):
        info.write(lines[i]);
    info.write("\n");
    now = datetime.now();
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S");
    info.write("(" + dt_string + "): tests " + str(firstId) + " -> " + str(nxtId - 1) +
               " (" + str(len(tests)) + ")\n");
    info.close();
    return;
def loadTest(path, Id):
    f = open(path + "/" + "test_" + str(Id) + ".csv", "r");
    (missing, size) = f.readline().split(',');
    test_x = [];
    test_y = [];
    for t in range(int(size)):
        gridTxt = f.readline();
        solTxt = f.readline();
        (inputTensor, solution) = textToPuzzle(gridTxt, solTxt);
        test_x.append(inputTensor);
        test_y.append(solution);
        f.readline();
    return test_x, test_y;
def loadAllTests(path, limit = -1):
    # load info
    size = 0;
    infoPath = path + "/info.txt";
    if (os.path.isfile(infoPath)):
        info = open(infoPath, "r");
        size = int(info.readline());
        info.close();
    tests_x = [];
    tests_y = [];
    for i in range(size):
        if (limit > -1):
            if (i == limit): break;
        test_x, test_y = loadTest(path, i);
        tests_x.append(test_x);
        tests_y.append(test_y);
    return tests_x, tests_y;
def createTestBatch(size, missing = 44):
    data = [];
    (train, solution) = newTrainBatch(batchSize, missing, False);
    for b in range(size):
        data.append((train[b], solution[b]));
        #print("-> #" + str(i) + "," + str(b) + ";");
        #print("train:\n", data[i * batchSize + b][0]); #X_train[i][j]);
        #print("> solution:\n", data[i * batchSize + b][1]); #Y_train[i][j]);
    # shuffle tests
    tests = [];
    order = [i for i in range(batchSize)];
    random.shuffle(order);
    for i in order:
        tests.append(data[i]);
    #print("tests:", tests);
    return tests;
def trainSingleSample(model, test, validate, debug = False):
    # train
    x_train = test[0];
    y_train = test[1];
    if (debug):
        print(sprintSample(x_train, y_train));
    x_train = (tf.reshape(x_train, [1, 9, 9, 1]) / 9) - 0.5;
    y_train = tf.reshape(y_train, [1, 81, 1]) - 1;
    # validate
    x_val = (tf.reshape(validate[0], [1, 9, 9, 1]) / 9) - 0.5;
    y_val = tf.reshape(validate[1], [1, 81, 1]) - 1;
    model.fit(x_train, y_train,
              validation_data=(x_val, y_val),
              epochs=5, verbose=1);
    return model;
def trainSingleBatch(model, test, validate, batchSize = -1, debug = False):
    # train
    batch_X = [];
    batch_Y = [];
    size = len(test);
    for i in range(size):
        batch_X.append(test[i][0]);
        batch_Y.append(test[i][1]);
    if (debug):
        print(sprintBatch(batch_X, batch_Y, size));
    x_train = (tf.reshape(batch_X, [size, 9, 9, 1]) / 9) - 0.5;
    y_train = tf.reshape(batch_Y, [size, 81, 1]) - 1;
    # validate
    batch_X = [];
    batch_Y = [];
    size = len(validate);
    for i in range(size):
        batch_X.append(validate[i][0]);
        batch_Y.append(validate[i][1]);
    x_val = (tf.reshape(batch_X, [size, 9, 9, 1]) / 9) - 0.5;
    y_val = tf.reshape(batch_Y, [size, 81, 1]) - 1;
    if (batchSize == -1): batchSize = len(test);
    model.fit(x_train, y_train,
              validation_data=(x_val, y_val),
              batch_size=batchSize, epochs=5, verbose=1);
    return model;
def createTrainSession(model, train, val, batchSize = 10, debug = False):
    # train
    x_train = []; y_train = []; size = len(train);
    for i in range(size):
        x_train.append(train[i][0]);
        y_train.append(train[i][1]);
    if (debug):
        print(sprintBatch(x_train, y_train, size));
    x_train = (tf.reshape(x_train, [size, 9, 9, 1]) / 9) - 0.5;
    y_train = tf.reshape(y_train, [size, 81, 1]) - 1;
    # validate
    x_val = []; y_val = []; size = len(val);
    for i in range(size):
        x_val.append(val[i][0]);
        y_val.append(val[i][1]);
    x_val = (tf.reshape(x_val, [size, 9, 9, 1]) / 9) - 0.5;
    y_val = tf.reshape(y_val, [size, 81, 1]) - 1;
    return (x_train, y_train, (len(train) // batchSize)), (x_val, y_val, (len(val) // batchSize));

load = True; # if False then it creates, otherwise loads saved
saveTrain = False;
train = True;
saveModel = False;
missing = 44;
if __name__ == "__main__":
    random.seed(int(datetime.now().timestamp()));
    print("TensorFlow version:", tf.version);
    if (load):
        print("Loading tests...");
        tests_x, tests_y = loadAllTests("tests");
        print("Loaded " + str(len(tests_x)) + " tests with each ? samples.");
    else:
        # create tests
        # tests = [test index][batch index][0 = train; 1 = label]
        tests = [];
        iterations = 2000;
        testSize = 10;
        batchSize = 50;
        print("Generating test grids...");
        for i in range(iterations):
            for t in range(testSize):
                tests.append(createTestBatch(batchSize, 44));
                print(".", end="");
            # save tests
            if (saveTrain):
                saveTests("tests", tests, missing);
            print("");
            tests = [];
            #print("\n" + str(testSize) + " tests with each " + str(batchSize) + " batches generated.");
    # create model
    model = createModel();
    # training session
    if (train):
        batchSize = 50;
        if (load):
            # put all into test (remove from batches)
            dataset_x = [];
            dataset_y = [];
            size = 0;
            for i in range(len(tests_x)):
                for b in range(len(tests_x[i])):
                    dataset_x.append(tests_x[i][b]);
                    dataset_y.append(tests_y[i][b]);
                    if (i == 0): size += 1;
            print("Dataset size = " + str(len(dataset_x)) + ", " + str(size));
            print("Transforming for training...");
            # seperate train and validation sets
            valRatio = (len(dataset_x) - (len(dataset_x) // 10));
            #x_train = (tf.reshape(x_train, [size, 9, 9, 1]) / 9) - 0.5;
            #y_train = tf.reshape(y_train, [size, 81, 1]) - 1;
            train = (dataset_x[:valRatio], dataset_y[:valRatio]);
            val = (dataset_x[valRatio:], dataset_y[valRatio:]);
            train = ((tf.reshape(train[0], [len(train[0]), 9, 9, 1]) / 9) - 0.5,
                     tf.reshape(train[1], [len(train[1]), 81, 1]) - 1);
            val = ((tf.reshape(val[0], [len(val[0]), 9, 9, 1]) / 9) - 0.5,
                   tf.reshape(val[1], [len(val[1]), 81, 1]) - 1);
            print(valRatio, ": ", len(train[0]), "<->", len(val[0]));
            # train
            print("Training...");
            model.fit(train[0], train[1],
                    validation_data=(val[0], val[1]),
                    batch_size=batchSize, epochs=5, verbose=2);
        else:
            # put all into test (remove from batches)
            dataset = [];
            for t in tests:
                size = 0;
                for b in t:
                    dataset.append(b);
                    size += 1;
            print("dataset size = " + str(len(dataset)) + ", " + str(size));
            # seperate train and validation sets
            valRatio = (len(dataset) - (len(dataset) // 10));
            train = dataset[:valRatio];
            validate = dataset[valRatio:];
            print(valRatio, ": ", len(train), "<->", len(validate));
            train, val = createTrainSession(model, train, validate, batchSize, True);
            # train
            print("training...");
            model.fit(train[0], train[1],
                    validation_data=(val[0], val[1]),
                    batch_size=batchSize, epochs=5, verbose=2);
    # save
    if (saveModel and train):
        model.save_weights("./models/first/first");
    print("Finished", end="");
    if (saveModel): print(" and saved.");
    else: print("");
