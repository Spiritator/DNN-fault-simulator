# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 16:46:08 2019

@author: Yung-Yu Tsai

An example of using inference scheme to arange analysis and save result.
"""

from inference.scheme import inference_scheme
from models.model_library import quantized_lenet5
from metrics.topk_metrics import top2_acc,top5_acc
from memory.mem_bitmap import bitmap
from memory.tile import tile, tile_FC, generate_layer_memory_mapping


#%%
# setting parameter

result_save_file='../../test_result/mnist_lenet5_mem_fault.csv'
weight_name='../../mnist_lenet5_weight.h5'
model_word_length=8
model_factorial_bit=4
batch_size=20
# memory fault simulation parameter
fault_rate=0.0001
row=80
col=20
word=4
model_wl=model_word_length

memory_column_priority=['Tm','Tc','Tr','Tn']
memory_row_priority=['Tr','Tm','Tc','Tn']


#%%
# fault generation

# model for get configuration
ref_model=quantized_lenet5(nbits=model_word_length,
                       fbits=model_factorial_bit,
                       batch_size=batch_size,
                       quant_mode=None)

# memory mapping
GLB_wght=bitmap(row, col*word*model_wl, wl=model_wl)
GLB_ifmap=bitmap(row, col*word*model_wl, wl=model_wl)
GLB_ofmap=bitmap(row, col*word*model_wl, wl=model_wl)

# conv1
ofmap_tile_conv1=tile((1,28,28,8),is_fmap=True,wl=model_wl,row_prior=memory_row_priority,col_prior=memory_column_priority)
ifmap_tile_conv1=tile((1,28,28,1),is_fmap=True,wl=model_wl,row_prior=memory_row_priority,col_prior=memory_column_priority)
wght_tile_conv1 =tile((5,5,1,8),is_fmap=False,wl=model_wl,row_prior=memory_row_priority,col_prior=memory_column_priority)

# conv2
ofmap_tile_conv2=tile((1,14,14,12),is_fmap=True,wl=model_wl,row_prior=memory_row_priority,col_prior=memory_column_priority)
ifmap_tile_conv2=tile((1,14,14,16),is_fmap=True,wl=model_wl,row_prior=memory_row_priority,col_prior=memory_column_priority)
wght_tile_conv2 =tile((5,5,16,12),is_fmap=False,wl=model_wl,row_prior=memory_row_priority,col_prior=memory_column_priority)

# FC1
ofmap_tile_fc1=tile_FC((1,3),is_fmap=True,wl=model_wl)
ifmap_tile_fc1=tile_FC((1,1764),is_fmap=True,wl=model_wl)
wght_tile_fc1 =tile_FC((1764,3),is_fmap=False,wl=model_wl)

# FC2
ofmap_tile_fc2=tile_FC((1,10),is_fmap=True,wl=model_wl)
ifmap_tile_fc2=tile_FC((1,128),is_fmap=True,wl=model_wl)
wght_tile_fc2 =tile_FC((128,10),is_fmap=False,wl=model_wl)


def gen_model_mem_fault_dict():
    model_ifmap_fault_dict_list=[None for i in range(8)]
    model_ofmap_fault_dict_list=[None for i in range(8)] 
    model_weight_fault_dict_list=[[None,None] for i in range(8)]

    # clear fault dictionary every iteration
    GLB_wght.clear()
    GLB_ifmap.clear()
    GLB_ofmap.clear()
    ofmap_tile_conv1.clear()
    ifmap_tile_conv1.clear()
    wght_tile_conv1.clear()
    ofmap_tile_conv2.clear()
    ifmap_tile_conv2.clear()
    wght_tile_conv2.clear()
    ofmap_tile_fc1.clear()
    ifmap_tile_fc1.clear()
    wght_tile_fc1.clear()
    ofmap_tile_fc2.clear()
    ifmap_tile_fc2.clear()
    wght_tile_fc2.clear()
    
    # assign fault dictionary
    GLB_wght.gen_bitmap_SA_fault_dict(fault_rate)
    GLB_ifmap.gen_bitmap_SA_fault_dict(fault_rate)
    GLB_ofmap.gen_bitmap_SA_fault_dict(fault_rate)
        
    # generate fault dictionary
    model_ifmap_fault_dict_list[1],model_ofmap_fault_dict_list[1],model_weight_fault_dict_list[1]\
    =generate_layer_memory_mapping(ref_model.layers[1],
                                   GLB_ifmap,GLB_wght,GLB_ofmap,
                                   ifmap_tile_conv1,wght_tile_conv1,ofmap_tile_conv1)
    
    model_ifmap_fault_dict_list[3],model_ofmap_fault_dict_list[3],model_weight_fault_dict_list[3]\
    =generate_layer_memory_mapping(ref_model.layers[3],
                                   GLB_ifmap,GLB_wght,GLB_ofmap,
                                   ifmap_tile_conv2,wght_tile_conv2,ofmap_tile_conv2)
    
    model_ifmap_fault_dict_list[6],model_ofmap_fault_dict_list[6],model_weight_fault_dict_list[6]\
    =generate_layer_memory_mapping(ref_model.layers[6],
                                   GLB_ifmap,GLB_wght,GLB_ofmap,
                                   ifmap_tile_fc1,wght_tile_fc1,ofmap_tile_fc1)
    
    model_ifmap_fault_dict_list[7],model_ofmap_fault_dict_list[7],model_weight_fault_dict_list[7]\
    =generate_layer_memory_mapping(ref_model.layers[7],
                                   GLB_ifmap,GLB_wght,GLB_ofmap,
                                   ifmap_tile_fc2,wght_tile_fc2,ofmap_tile_fc2)
    
    return model_ifmap_fault_dict_list,model_ofmap_fault_dict_list,model_weight_fault_dict_list

#%%
# test

model_augment=list()

for i in range(100):
    model_ifmap_fdl,model_ofmap_fdl,model_weight_fdl=gen_model_mem_fault_dict()
    model_augment.append({'nbits':8,'fbits':3,'rounding_method':'nearest','batch_size':batch_size,'quant_mode':'hybrid',
                          'ifmap_fault_dict_list':model_ifmap_fdl,
                          'ofmap_fault_dict_list':model_ofmap_fdl,
                          'weight_fault_dict_list':model_weight_fdl})

compile_augment={'loss':'categorical_crossentropy','optimizer':'adam','metrics':['accuracy',top2_acc]}

dataset_augment={'dataset':'mnist'}


inference_scheme(quantized_lenet5, model_augment, compile_augment, dataset_augment, result_save_file, weight_load=True, weight_name=weight_name)


