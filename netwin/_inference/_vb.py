""" Scipt containing functions to implement variational inference using 
multivariate normal distribution and gamma distribution
"""

def time_step(theta): 
    """Control time stepping interval proportional to the parameter magnitiude. 

    args: 
    theta:: float 
    """

    delta = theta * 1e-5

    if delta < 0:
            delta = -delta
    if delta < 1e-10:
            delta = 1e-10
    
    return delta

def central_difference(f, i, theta, delta, t):
    """ Calculate the derivate using a first order central difference approximation

    args:
        d : function 
            function on which to compute central difference 
        i : int 
            parameter index
    theta : np.array float 
            array of paramters for function, f
    delta : float 
            time-step for central difference
        t : np.array float
            time steps to evaluate at
    returns: 
        df : np.array, float 
             first order approximation, df, for time steps, t
    """
    dtheta = np.array(theta), np.array(theta)

    dtheta[0][i] += delta
    dtheta[1][i] -= delta
    df = (f(dtheta[0], t) - f(dtheta[1], t)) / (2 * delta)
    return df

def Jacobian(f, theta, t):
    """Compute the Jacobian for globally defined function, f, with parameter set Theta 

    args:
    theta : np.array, float
            parameters of global function, f
        t : np.array, float 
            time steps to evaluate at

    returns: 
        J : np.array, float
            Jacobian vector/matrix evaluated at theta, t. 
    """
    J = None
    #f_n = len(f)
    p_n = len(theta)

    for i in range(p_n):
        delta = time_step(theta[i])
        if J is None:
                J = np.zeros([len(t), len(theta)], dtype=np.float32)
        J[:,i] = central_difference(f, i, theta, delta, t)
    
    return J

def parameter_update(error, params, priors, J):
    """ Update forward model function parameters theta in accordance with the update equations above
    
    args: 
        error : array, float
                vector of the difference between observations and model prediction 
       params : tuple
                parameters values
       priors : tuple 
                priors values
            J : array, float 
                array of Jacbian values from the model given parameter updates (calculated above)
    returns: 
       params : tuple
                updated parameters values
    """
    m, p, s, c = params
    m0, p0, _, _ = priors

    p_new = s*c*np.dot(J.transpose(), J) + p0
    c_new = np.linalg.inv(p_new)
    m_new = np.dot(c_new, (s * c * np.dot(J.transpose(), (error +    np.dot(J, m))) + np.dot(p0, m0)))
    
    params[0][:], params[1][:] = m_new, p_new

    return params

def noise_update(error, params, priors, J):
    """ Update forward model function parameters phi in accordance with the update equations above
    
    args: 
        error : array, float
                vector of the difference between observations and model prediction 
       params : tuple
                parameters values
       priors : tuple 
                priors values
            J : array, float 
                array of Jacbian values from the model given parameter updates (calculated above)
    returns: 
       params : tuple
                updated parameters values
    """
    _, p, _, _ = params 
    _, _, s0, c0 = priors

    N = len(data)

    c = np.linalg.inv(p)
    c_new = N/2 + c0
    s_new = 1/(1/s0 + 1/2 * np.dot(error.transpose(), error) + 1/2 * np.trace(np.dot(c, np.dot(J.transpose(), J))))
    
    params[2][:], params[3][:] = c_new, s_new

    return params

def error_update(y, f, theta, t):
    """Calculate difference between data and model with updated parameters

    args:
        y : array, float 
            vector of noisy data (observations)
    theta : array, float
            vector of parameter values for model, f
        t : array, float 
            vector of time steps at which to evaluate model 
    
    returns:
    error : array, float 
            vector of difference between noisy data and updated model
    """


    error = y - f(theta[:2], t)
    
    return error

def fit(f, data, params, priors, t, n): 
    
    theta = np.zeros((n, len(params[0])))
    for i in range(n):
        theta[i,:] = params[0]
        error = error_update(data, f, theta[i,:], t)
        
        J = Jacobian(f, theta[i,:], t)
        params = parameter_update(error, params, priors, J)
        params = noise_update(error, params, priors, J)
        print(params)

    return params, theta