import random
from time import *
 
def zero(m,n):
    # Create zero matrix
    new_matrix = [[0 for row in range(n)] for col in range(m)]
    return new_matrix
 
def rand(m,n):
    # Create random matrix
    new_matrix = [[random.random() for row in range(n)] for col in range(m)]
    return new_matrix
 
def show(matrix):
    # Print out matrix
    for col in matrix:
        print col 

def matrixAdd(matrix1, matrix2):
    if len(matrix1[0]) != len(matrix2[0]) or len(matrix1) != len(matrix2):
        print 'invalid matrix add'
        return None
    else:
        new_matrix = zero(len(matrix1),len(matrix1[0]))
        for i in range(len(matrix1)):
            for j in range(len(matrix1[0])):
                new_matrix[i][j] = matrix1[i][j] + matrix2[i][j]
        return new_matrix

        
 
def mult(matrix1,matrix2):
    # Matrix multiplication
    if len(matrix1[0]) != len(matrix2):
        # Check matrix dimensions
        print 'Matrices must be m*n and n*p to multiply!'
    else:
        # Multiply if correct dimensions
        new_matrix = zero(len(matrix1),len(matrix2[0]))
        for i in range(len(matrix1)):
            for j in range(len(matrix2[0])):
                for k in range(len(matrix2)):
                    new_matrix[i][j] += matrix1[i][k]*matrix2[k][j]
        return new_matrix

def getLocalLink(M, L):
    internal_matrix = zero(len(L),len(L[0]))
    external_matrix = zero(len(L),len(L[0]))
    for i in range(len(L)):
        for j in range(len(L[i])):
            isInternal = 0
            for k in range(len(M[0])):
                if M[i][k] == 1 and M[j][k] == 1 :
                    isInternal = 1
            if isInternal == 1:
                internal_matrix[i][j] = L[i][j]
            else:
                external_matrix[i][j] = L[i][j] * -1;
    return (internal_matrix, external_matrix)


def invertedMatrix(M):
    new_matrix = zero(len(M), len(M[0]))
    for i in range(len(M)):
        for j in range(len(M[0])):
            if M[i][j] != 0:
                for k in range(len(M[0])):
                    new_matrix[i][k] = M[i][j]
                new_matrix[i][j] = 0
    return new_matrix


M = [[0, 1, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
L = [[0, 0, 1, 0, 0], [0, 0, 1, 0, 1], [1, 1, 0, 1, 0], [0, 0, 1, 0, 0], [0, 1, 0, 0, 0]]

(internal_matrix, external_matrix) = getLocalLink(M, L)
IP = mult(internal_matrix, M)
EP = mult(external_matrix, M)
IIP = invertedMatrix(IP)
D = matrixAdd(IIP, EP)

print "internal_matrix"
show(internal_matrix)
print "external_matrix"
show(external_matrix)
print "M"
show(M)
print "IP"
show(IP)
print "inverted IP"
show(IIP)
print "EP"
show(EP)
print "D"
show(D)
