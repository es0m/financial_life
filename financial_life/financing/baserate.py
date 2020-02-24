import numpy as np

# a crude central bank baserate simulator

# exponential random walk over decrease, stay put or increase by the given change. 
def generate_positive_random_walk(start, n, change):
    r = np.random.randint(3, size=n-1)
    dr = (r-1)*change
    cr = np.insert(dr, 0, start, axis=0)
    cr = np.cumsum(cr)
    cr = np.exp(cr)/np.exp(1)
    return cr

# creates multiple random walks
def generate_set_of_walks(start, n, size, change): 
    a = np.zeros((n, size), dtype=np.float)
    for i in range(size):
        cr = generate_positive_random_walk(start, n, change)
        a[:,i] = cr.T
    return a
    
# gets the average of the percentile ranges given. 
# example: get_percentile(generate_set_of_walks(1.0, 100, 80, 0.0175), [0.25, 0.45, 0.55, 0.75])
#             returns a matrix of length 100 with three layers, average of 0.25-0.45 values, average of 0.45 to 0.55, and 0.55 to 0.75
def get_percentiles(A, percentiles):
    sz = A.shape[0]
    layers = np.empty((sz, len(percentiles)-1))
    p = np.asarray(percentiles)
    pcts = np.floor(p*(A.shape[1]-1))
    pcts = pcts.astype(np.int)
    for i in range(sz) : 
        _sorted = np.sort(A[i,:])
        cs = np.cumsum(_sorted)#/_sorted.shape[0]
        dcs = cs[pcts[1:]]-cs[pcts[0:-1]]
        dn = pcts[1:]-pcts[0:-1]
        layers[i, :] = np.divide(dcs, dn)#cs[pcts],pcts)#_sorted[pcts]
        #layers[i, :] = _sorted[pcts]
    return layers


def baserate_example():
    import matplotlib.pyplot as plt
    A = generate_set_of_walks(1.0, 40*4, 80)
    #percentiles = [0.25, 0.45, 0.55, 0.75]
    #percentiles = [0.0, 1.00]
    percentiles = [0.0, 0.45, 0.55, 1.00]
    layers = get_percentiles(A, percentiles)
    avg = np.mean(A, axis=1)
    colors = ["red", "green", "red"]
    for i in range(len(percentiles)-1) :
        plt.plot(np.arange(A.shape[0])/4, layers[:, i], color=colors[i])
    plt.plot(np.arange(A.shape[0])/4, avg, color="blue")
    plt.show()
    
