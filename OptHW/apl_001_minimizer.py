"""=================================================================="""
"""Minimize an objective function using SciPy."""

"""
 reference: https://docs.scipy.org/doc/scipy/reference/optimize.html
 reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html
 https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html

 in depth:  http://www.scipy-lectures.org/advanced/mathematical_optimization/

 method: Sequential Least SQuares Programming  (SLSQP): see above reference
 various methods are discussed in the scipy.optimize.minimize page above.
"""
"""=================================================================="""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as spo

def f(X): 
	"""Given a scalar X, return some value (a real number)."""
	Y = (X - 1.5)**2 + 0.5  # parabola X = 1.5  Y = 0.5
	print( "X = {}, Y = {}".format(X,Y)) # for code tracing 
	return Y

def g(X): 
    """Given a scalar X, return some value (a real number)."""
    Y = (X - 7.5)**2 + -(X - 3.5)**2+4.5  # parabola X = 1.5  Y = 0.5
    Y=X+X+X
    Y+=(X - 7.5)**2
    print( "X = {}, Y = {}".format(X,Y)) # for code tracing 
    return Y

## https://docs.scipy.org/doc/numpy/reference/generated/numpy.linspace.html
def plot_it(min_result):
        """Given a scalar X, return some value (a real number)."""

         # Plot function values, mark minima
        Xplot = np.linspace(0.5, 2.5, 21)	# generates X values
					        #  21  evenly spaced over [0.5,2.5]
					
        Yplot = f(Xplot)			# generates Y values - calls 
						# the function again for each X.
        plt.plot(Xplot, Yplot)
        plt.plot(min_result.x, min_result.fun, 'ro')
        plt.title("Minima of an objective function")
        plt.show()

# gradient descent method
'''
def min_df(valuedf):
    for row in valuedf:
        alloc=row[0]
        avg=row[1]
        std=row[2]
        rfr=row[3]
def create_function(name, paramdf):
    def funct(dfx):
        y=0
        for i in range(len(dfx)):    
            y=dfx[i]*(paramdf[i][1]-paramdf[i][3])/(paramdf[i][2]-paramdf[i][3])
        return y
    dfx = paramdf.column(paramdf[0])
    min_result = spo.minimize(funct, dfx, method = 'SLSQP', options = {'disp':True})
    print('minima found at')
    print(min_result.x, min_result.fun)
    
    return min_result
    #plot_it(min_result)

    #def inner_function(average, stdev, rfr):
    #    return (average-rfr)/(stdev-rfr)
    #functlist = []
    #functvars = []
    #for i in range(len(paramdf)):
    #    functlist.append[inner_function(paramdf[1], paramdf[2], paramdf[3])]
    #    functvars.append('x'+i)
'''
def srmaxtwo(paramdf):
    srlist = []
    for i in range(len(paramdf)):
        srparam = paramdf.iloc[i]
        print(srparam)
        temprfr = paramdf.iat[i, 3]
        print('temprfr is', temprfr)
        srlist.append((paramdf.iat[i, 1]-temprfr)/(paramdf.iat[i, 2]-temprfr))
    print('srlist is', srlist)
    high = srlist.index(max(srlist))
    sechigh = srlist.index(max(srlist[:high]+srlist[high+1:]))
#    if sechigh>=high:
#        sechigh += 1
    return high, sechigh

def create_function(xdf):
    def funct(x):
        y=0
        for i in range(len(xdf)):
            sr = (xdf.iat[i, 1]-xdf.iat[i, 3])/(xdf.iat[i, 2]-xdf.iat[i, 3])
            #if i<len(xdf)-1:
            y+=x[i]*sr
            #else:
            #y+=(1-sum(x))*sr
        #only includes minimization, answer is flipped to negative
        return -y
    #dfx = paramdf.column(paramdf[0])
    allocdf=xdf.iloc[:, 0] #this is what will be modified
    #xi=np.array([xi])
    #negative creates the minimum of the function
    #bndparams = [[1, 1] for _ in range(len(xdf))]
    #bndparams = [[1 for _ in range(len(xdf))], [1 for _ in range(len(xdf))]]
    #ci = [0 for _ in range(len(xdf))]
    #ce = [1 for _ in range(len(xdf))]
    
    #ci = [-np.inf for _ in range(len(xdf))]
    #ce = [np.inf for _ in range(len(xdf))]
    #bndparams[1][1] = 0.5
    cnsts = ({ 'type':   'eq', 'fun': lambda allocdf: 1.0 - np.sum(allocdf) })
    #cnsts = spo.LinearConstraint(bndparams, ci, ce)
    #print(bndparams)
    bnds = ((0, 1),)*len(allocdf)
    #test =funct(x)

    display = False
            
    min_result = spo.minimize(funct, allocdf, method = 'SLSQP',  constraints = cnsts, \
                              bounds = bnds, options = {'disp':display}) #, 
    
    return min_result

def create_function_duo(x1df, x2df):
    def funct(xi):
        y=0
        
        y+=xi*(x1df.iat[1]-x1df.iat[3])/(x1df.iat[2]-x1df.iat[3])
        y+=(1-xi)*(x2df.iat[1]-x2df.iat[3])/(x2df.iat[2]-x2df.iat[3])
        #only includes minimization, answer is flipped to negative
        return -y
    #dfx = paramdf.column(paramdf[0])
    xi=x1df.iat[0].item()
    #xi=np.array([xi])
    #negative creates the minimum of the function
    bi = (0,None)
    be = (1,None)
    bnds = ((0, 1),)
    
    display = False
    min_result = spo.minimize(funct, xi, method = 'SLSQP',  bounds = bnds, options = {'disp':display}) #, 
    
    return min_result
    
def sharpeminima(paramdf):
    #paramdf = pd.concat([pd.concat([pd.concat([allocs, averages], axis=1), stdevs], axis=1), rfrs], axis=1)
    #paramdf = allocs.concat(averages).concat(stdevs).concat(rfrs)
    high, sechigh = srmaxtwo(paramdf)
    highx = create_function_duo(paramdf.iloc[high], paramdf.iloc[sechigh])
    return high, sechigh, highx

def test_run2():
    Xguess = .5
    paramdf = pd.DataFrame([[0.2, 0.000957, 0.01652, 0.], [0.6, 0.000957, 0.01651, 0.]], index=['test1', 'test2'], columns = ['alloc', 'mean', 'stdev', 'rfr'])
    print(paramdf)
    # optimize with constraints - gradient method
    # Sequential least square programming: equality and inequality constraints:
    print(type(Xguess))
    
    high, sechigh, highx = sharpeminima(paramdf)
    funct_result = create_function(paramdf)
    #print('the function results')
    #print(funct_result)
    #print(funct_result.x)
    #sys.exit(0)
#   
#    min_result = spo.minimize(g, Xguess, method='SLSQP', bounds = ((1, None), (0, None)), options = {'disp':True})
    #min_result = spo.minimize(f, Xguess, method='SLSQP', options = {'disp':True})
	#min_result = spo.minimize_scalar(f)  # Brent's method
	# disp-true -> prints convergence messages.

    print( "Minima found at:")
    print("X = {}".format(highx))
    #plot_it(min_result)

def test_run():
    Xguess = 2.0

    # optimize with constraints - gradient method
    # Sequential least square programming: equality and inequality constraints:
    print(type(Xguess))
    min_result = spo.minimize(g, Xguess, method='SLSQP', bounds = ((1, None), (0, None)), options = {'disp':True})
    #min_result = spo.minimize(f, Xguess, method='SLSQP', options = {'disp':True})
	#min_result = spo.minimize_scalar(f)  # Brent's method
	# disp-true -> prints convergence messages.

    print( "Minima found at:")
    print("X = {}, Y = {}".format(min_result.x, min_result.fun))
    plot_it(min_result)
	
if __name__ == "__main__":
	test_run2()

