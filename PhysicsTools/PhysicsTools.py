
import numpy as np



# A simple class to support simple physics calculations.
class PhysicsTools:
    '''
    **Description**: 
    A simple class to support simple physics calculations.
    '''

    #     
    def __init__(self):
        '''
        **Description**: 
        Define constants.
        '''
    
        self.constants = { \
            'gravity' : 6.67430e-11, # N / m2 / kg2
            'permittivity' : 8.854188e-12,  # F/m = A2 s4 / kg / m3 
            'electron charge' : 1.60217663e-19, # Coulomb
            'speed of light' : 2.99792458e+8 # m / s
        }
            

        self.CoulombForceConstant = 1 / (4 * np.pi * self.constants ['permittivity'] )
    
    
    #
    def getInverseSquareValue (self, mass1 = 1, mass2 = 1, r = [1,1,1], phenomenon = 'gravity', constant = None):
        '''
        
        **Description**:
        '''
        
        
        if phenomenon == 'gravity' and not constant:
        
            constant = self.constants ['gravity'] 


        if phenomenon == 'electricity' and not constant:
        
            constant =  self.CoulombForceConstant


        distanceSquare = r [0] * r [0]  +  r [1] * r [1]  +  r [2] * r [2]
        
        return constant * mass1 * mass2 / distanceSquare
        
        
    

    