#!/bin/sh

rm data/train.cache data/data.model

vw -b 27 --passes 50 --cache_file data/train.cache -f data/data.model -d data/vw_train.dat --loss_function logistic

vw -t  -i data/data.model -d data/vw_test.dat -p data/vw_test.pred --loss_function logistic
