# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 11:33:23 2018

@author: Yung-Yu Tsai

evaluate quantized testing result with custom Keras quantize layer 
"""

# setup

import keras
import numpy as np
import keras.backend as K


from models.model_library import quantized_lenet5, load_orginal_weights_on_quantized_model
from utils_tool.dataset_setup import dataset_setup
from metrics.topk_metrics import top2_acc

#%%

weight_name='something'

# model setup
model=quantized_lenet5()
model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy',top2_acc])
model=load_orginal_weights_on_quantized_model(model,weight_name)
