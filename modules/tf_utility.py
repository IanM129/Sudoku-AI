import numpy as np
import tensorflow as tf

def gridToTensor(source : list[list[int]]) -> tf.Tensor:
    result = np.copy(source);
    for y in range(9):
        for x in range(9):
            if (result[y][x] == None):
                result[y][x] = 0;
    return tf.constant(result.tolist());
def arrToTensor(source : list[int]) -> tf.Tensor:
    return tf.constant(source);
