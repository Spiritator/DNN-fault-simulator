# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 14:32:50 2018

@author: Yung-Yu Tsai

evaluate quantized testing result with custom Keras quantize layer 
"""

import keras
from keras.utils import multi_gpu_model,to_categorical
from models.resnet50 import QuantizedResNet50FusedBN,preprocess_input
from utils_tool.dataset_setup import dataset_setup
from metrics.topk_metrics import top5_acc
import time
from testing.fault_list import generate_model_stuck_fault
from testing.fault_core import generate_model_modulator
from metrics.FT_metrics import acc_loss, relative_acc, pred_miss, top5_pred_miss, conf_score_vary_10, conf_score_vary_50
from inference.evaluate import evaluate_FT

# dimensions of our images.
img_width, img_height = 224, 224

set_size=2
class_number=1000
batch_size=20
model_word_length=[16,16,16]
model_fractional_bit=[8,12,8]
rounding_method='nearest'
fault_rate=1e-7
if set_size in [50,'full',None]:
    validation_data_dir = '../../../dataset/imagenet_val_imagedatagenerator'
else:
    validation_data_dir = '../../../dataset/imagenet_val_imagedatagenerator_setsize_%d'%set_size


#%%
# fault generation

# model for get configuration
model = QuantizedResNet50FusedBN(weights='../../resnet50_weights_tf_dim_ordering_tf_kernels_fused_BN.h5', 
                                 nbits=model_word_length,
                                 fbits=model_fractional_bit, 
                                 rounding_method=rounding_method,
                                 batch_size=batch_size,
                                 quant_mode=None)

model_ifmap_fault_dict_list, model_ofmap_fault_dict_list, model_weight_fault_dict_list\
=generate_model_stuck_fault(model,
                            fault_rate,
                            batch_size,
                            model_word_length,
                            param_filter=[True,True,True],
                            fast_gen=True,
                            return_modulator=True,
                            bit_loc_distribution='uniform',
                            bit_loc_pois_lam=None,
                            fault_type='flip')

#model_ifmap_fault_dict_list, model_ofmap_fault_dict_list, model_weight_fault_dict_list\
#=generate_model_modulator(model,
#                          model_word_length,
#                          model_fractional_bit,
#                          model_ifmap_fault_dict_list, 
#                          model_ofmap_fault_dict_list, 
#                          model_weight_fault_dict_list,
#                          fast_gen=True)


#%%
# model setup

print('Building model...')

t = time.time()

model = QuantizedResNet50FusedBN(weights='../../resnet50_weights_tf_dim_ordering_tf_kernels_fused_BN.h5', 
                                 nbits=model_word_length,
                                 fbits=model_fractional_bit, 
                                 rounding_method=rounding_method,
                                 batch_size=batch_size,
                                 quant_mode='hybrid',
                                 ifmap_fault_dict_list=model_ifmap_fault_dict_list,
                                 ofmap_fault_dict_list=model_ofmap_fault_dict_list,
                                 weight_fault_dict_list=model_weight_fault_dict_list)

#model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', top5_acc])

t = time.time()-t

model.summary()

print('model build time: %f s'%t)

# multi GPU model

#print('Building multi GPU model...')
#
#t = time.time()
#parallel_model = multi_gpu_model(model, gpus=2)
#parallel_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy', top5_acc])
#
#parallel_model.summary()
#
#t = time.time()-t
#
#print('multi GPU model build time: %f s'%t)

#%%
#dataset setup

print('preparing dataset...')
x_train, x_test, y_train, y_test, class_indices, datagen, input_shape = dataset_setup('ImageDataGenerator', img_rows = img_width, img_cols = img_height, batch_size = batch_size, data_augmentation = False, data_dir = validation_data_dir, preprocessing_function = preprocess_input)
print('dataset ready')


#%%
# test

t = time.time()
print('evaluating...')

from keras.losses import categorical_crossentropy
#prediction = parallel_model.predict_generator(datagen, verbose=1, steps=len(datagen))
prediction = model.predict_generator(datagen, verbose=1, steps=len(datagen))
test_result = evaluate_FT('resnet',prediction=prediction,test_label=to_categorical(datagen.classes,1000),loss_function=categorical_crossentropy,metrics=['accuracy',top5_acc,acc_loss,relative_acc,pred_miss,top5_pred_miss,conf_score_vary_10,conf_score_vary_50],fuseBN=True,setsize=set_size)

t = time.time()-t
print('\nruntime: %f s'%t)
for key in test_result.keys():
    print('Test %s\t:'%key, test_result[key])

#%%
# draw confusion matrix

#print('\n')
#prediction = model.predict_generator(datagen, verbose=1, steps=len(datagen))
#prediction = np.argmax(prediction, axis=1)
#
#show_confusion_matrix(datagen.classes,prediction,datagen.class_indices.keys(),'Confusion Matrix',figsize=(10,8),normalize=False,big_matrix=True)

