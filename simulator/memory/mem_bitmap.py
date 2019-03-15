# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 11:54:08 2019

@author: Yung-Yu Tsai

Memory bitmap setting for memory fault mapping
"""

import numpy as np
    
class bitmap:
    """
    The bitmap of a buffer for memory fault tolerance analysis.
    
    """

    def __init__(self, row, col, wl=None):
        """
        # Arguments
            row: Integer. Number of rows in memory.
            col: Integer. Number of columns in memory.
            wl: Integer. The word length of memory
            fault_num: Integer. Number of faults in memory.
            fault_dict: Dictionary. The fault information {location : fault type}
    
        """
        self.row=row
        self.col=col
        self.wl=wl
        self.fault_num=None
        self.fault_dict=dict()

    def fault_num_gen_mem(self, fault_rate):
        """
        Genenerate the number of fault
        """
        self.fault_num=int(self.row * self.col * fault_rate)
    
        
    def addr_gen_mem(self,distribution='uniform',poisson_lam=None):
        """Genenerate the fault location in a memory

        # Arguments
            distribution: String. The distribution type of locaton in memory. Must be one of 'uniform', 'poisson', 'normal'.
            poisson_lam: Integer. The lambda of poisson distribution.
    
        # Returns
            The location index Tuple(Integer).
        """
        if distribution=='uniform':
            row_tmp=np.random.randint(self.row)
            col_tmp=np.random.randint(self.col)
        elif distribution=='poisson':
            if not isinstance(poisson_lam,tuple) or len(poisson_lam)!=2:
                raise TypeError('Poisson distribution lambda setting must be a tuple has length of 2 (row, col).')
            
            if isinstance(poisson_lam[0],int) and poisson_lam[0]>=0 and poisson_lam[0]<self.row:
                row_tmp=np.random.poisson(poisson_lam[0])
                while row_tmp>=self.row:
                    row_tmp=np.random.poisson(poisson_lam[0])
            else:
                raise ValueError('Poisson distribution Lambda must within feature map shape. Feature map shape %s but got lambda input %s'%(str((self.row,self.col)),str(poisson_lam)))
            
            if isinstance(poisson_lam[1],int) and poisson_lam[1]>=0 and poisson_lam[1]<self.col:
                col_tmp=np.random.poisson(poisson_lam[1])
                while col_tmp>=self.col:
                    col_tmp=np.random.poisson(poisson_lam[1])
            else:
                raise ValueError('Poisson distribution Lambda must within feature map shape. Feature map shape %s but got lambda input %s'%(str((self.row,self.col)),str(poisson_lam)))
    
        elif distribution=='normal':
            pass 
            '''TO BE DONE'''   
        else:
            raise NameError('Invalid type of random generation distribution. Please choose between uniform, poisson, normal.')
        
        return (row_tmp,col_tmp)
    
    def gen_bitmap_SA_fault_dict(self,fault_rate,addr_distribution='uniform',addr_pois_lam=None,fault_type='flip',**kwargs):
        """Generate the fault dictionary of memory base on its shape and with specific distibution type.

        # Arguments
            fault_rate: Float. The probability of fault occurance in memory.
            addr_distribution: String. The distribution type of address in memory. Must be one of 'uniform', 'poisson', 'normal'.
            addr_pois_lam: Integer. The lambda of poisson distribution of memory address.
            fault_type: String. The type of fault.
    
        # Returns
            The fault information Dictionary. The number of fault generated Integer.
        """
        
        fault_count=0        
        fault_dict=dict()
        self.fault_num_gen_mem(fault_rate)
                
        while fault_count<self.fault_num:
            addr=self.addr_gen_mem(distribution=addr_distribution,poisson_lam=addr_pois_lam,**kwargs)
            
            if addr in fault_dict.keys():
                continue
            else:
                fault_dict[addr]=fault_type
                fault_count += 1
            
        self.fault_dict=fault_dict
        
        return fault_dict,self.fault_num



