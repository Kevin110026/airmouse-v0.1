import numpy

def try2change(a):
    a[0]=1

a=numpy.array([0,0,0])
print(a)
try2change(a)
print(a)