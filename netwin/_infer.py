"""script containing classe/functions for inference methods
"""
from netwin._inference import * 
import numpy as np
from ._model import Model

class InferenceProblem(object):
    """Class for setting Inference Problems 
    Presently implemented for VB only. 
    Will return a structured object that can be passed into 'fit' to perform variational inference
    For VB, the required arguments are: 
        model : class implementing forward model 
        data  : data one wishes to perform inference against
        t     : time steps at which to evaluate forward model 
    init means: initial guess for the means of each free parameter
    
    In addition to the input variables, the __init__ will return initial distribution
    parameter values and prior distribution parameter values
    """
    def __init__(self, inference:str, model=None, data=None, t=None, init_means=None, priors=None):
        if inference == 'VB': 
            self.which_inference = 'VB'

            if not isinstance(model, Model):
                raise TypeError('Change this Model class, motherfucker.')

            self.model = model #check model is instance of model class
            self.data = data 
            self.t = t
            self.init_means = init_means
            self.params, self.priors = self.__vbinferenceproblem(init_means)
            self.n_params = len(init_means) - len(model.L)

    def __vbinferenceproblem(self, init_means, priors=None): 
        if priors == None:
            priors = self.__vbsetpriors(init_means)
    
        m = init_means
        p = np.linalg.inv(np.diag(np.ones_like(m)))
        #c = np.array([priors[2]])
        #s = np.array([priors[3]])
        c = np.array([1e-8])
        s = np.array([50.0])
        params = m, p, c, s
        
        return params, priors

    def __vbsetpriors(self, init_means):

        m0 = np.zeros_like(init_means)
        p0 = np.linalg.inv(np.diag(np.ones_like(m0) * 1e5))

        beta_mean0 = 1.0
        beta_var0  = 1000.0

        c0 = beta_var0 / beta_mean0
        s0 = beta_mean0**2 / beta_var0

        priors = m0, p0, c0, s0

        return priors