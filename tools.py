import math
import numpy


def getVectorLength(vector: numpy.ndarray) -> float:
    return ((vector**2).sum())**0.5


def getDegree(vector_a: numpy.ndarray, vector_b: numpy.ndarray) -> float:
    cosTheta = (vector_a * vector_b).sum() / (getVectorLength(vector_a) *
                                              getVectorLength(vector_a))
    if (cosTheta > 1):
        cosTheta = 1
    elif (cosTheta < -1):
        cosTheta = -1
    theda = math.acos(cosTheta)
    return math.degrees(theda)
