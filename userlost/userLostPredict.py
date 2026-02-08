#!/usr/bin/env python
# coding: utf-8

#导入基础包
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.impute import KNNImputer
from sklearn.discriminant_analysis import StandardScaler
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.utils import compute_class_weight
from keras.regularizers import l1,l2
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
# import lightgbm as lgb
from geneticalgorithm import geneticalgorithm as ga
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import RobustScaler
import warnings
from sklearn.ensemble import ExtraTreesClassifier
from sklearn import tree
import xgboost as xgb
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import roc_curve, auc, accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from catboost import CatBoostClassifier
from sklearn.ensemble import AdaBoostClassifier
import datetime
import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from sklearn import metrics
import random
import datetime
from sklearn.impute import KNNImputer
from sklearn.discriminant_analysis import StandardScaler
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.utils import compute_class_weight
from keras.regularizers import l1,l2
from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical
from geneticalgorithm import geneticalgorithm as ga
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import RobustScaler
import warnings
from sklearn.metrics import accuracy_score
from sklearn.ensemble import ExtraTreesClassifier
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import joblib
import json

warnings.filterwarnings("ignore")


predict_file_path = sys.argv[1]
output_predict_file_name = sys.argv[2]


def write_results_to_file(score, auc, y_test,y_ET_pred, start_param, file_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = r'D:\log\userlost'  # 指定输出目录路径
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # 如果路径不存在，则创建目录
    output_file = os.path.join(output_dir, f"{file_name}.log")
    
    print('\n========{0}-start:{1}===================\n'.format(start_param, timestamp))
    print('accucy: {0}, AUC: {1}\n'.format(score, auc))
    print('\n============================================================\n')
    print(classification_report(y_test, y_ET_pred, labels=None, target_names=None, sample_weight=None, digits=3))
    print('\n========================={0}-end===============================\n'.format(start_param))

    #写文件
    with open(output_file, 'a') as f:
        f.write('\n\n\n========{0}-start:{1}===================\n'.format(start_param, timestamp))
        f.write('accucy: {0}, AUC: {1}\n'.format(score, auc))
        f.write('\n\n\n============================================================\n')
        f.write(classification_report(y_test, y_ET_pred, labels=None, target_names=None, sample_weight=None, digits=2))
        f.write('\n\n\n========================={0}-end===============================\n'.format(start_param))
        f.write('\n*******************************************************************\n')


def read_data():
    # 解决中文乱码问题
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

    # 显示全部特征
    pd.set_option('display.max_columns', None)
    #多重插补填充5.9.csv  45个字段
    # 读取数据
    df = pd.read_csv(predict_file_path)

    rawdf = df.copy()
    return rawdf  # 返回处理后的特征矩阵和目标变量


def preprocess_data(selected_features,rawdf):
    # 选择指定特征
    rawdf = rawdf[selected_features]
    
    # 分割特征和目标变量
    y = rawdf['label']
    x = rawdf.drop('label', axis=1)

    # 特征缩放
    scaler = RobustScaler()
    scaler.fit(x)
    X = scaler.transform(x)

    return X, y  # 返回处理后的特征矩阵和目标变量


# 封装XGB方法
def train_predict_and_evaluate_xgb(X_train, y_train, X_test, y_test,file_name):
    # 读取训练集和测试集
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dtest = xgb.DMatrix(X_test, label=y_test)

    # 设置xgboost建模参数
    params={'booster':'gbtree','objective': 'binary:logistic','eval_metric': 'auc',
        'max_depth':8,'gamma':0,'lambda':2,'subsample':0.7,'colsample_bytree':0.8,
        'min_child_weight':3,'eta': 0.2,'nthread':8,'silent':1}

    # 训练模型
    watchlist = [(dtrain,'train'), (dtest, 'test')]  # 添加测试集到watchlist
    bst = xgb.train(params, dtrain, num_boost_round=500, evals=watchlist)

    #  输入预测为正确的概率
    y_prob = bst.predict(dtest)
    # 设置阈值为0.5，得到测试集的测试结果
    y_pred = (y_prob >= 0.5).astype(int)

    # 打印预测结果
    print("Predictions:", y_pred)

    result = {}
    for i, pred in enumerate(y_pred):
        result[str(i)] = int(pred)

    # 将结果写入 JSON 文件
    with open(output_predict_file_name, 'w') as f:
        json.dump(result, f)

    print(f"Predictions saved to {output_predict_file_name}")

    # 获取真阳率、伪阳率、阈值
    fpr_xgb, tpr_xgb, threshold_xgb = roc_curve(y_test, y_prob)
    auc_xgb = auc(fpr_xgb, tpr_xgb)    # AUC得分
    score_xgb = accuracy_score(y_test, y_pred)    # 模型准确率

    write_results_to_file(score_xgb, auc_xgb, y_test,y_pred, 'xgb', file_name)
    return y_pred,bst,fpr_xgb, tpr_xgb,score_xgb,auc_xgb



rawdf = read_data()


all_features = ['label', 'iforderpv_24h', 'historyvisit_totalordernum', 'hotelcr',
       'ordercanceledprecent', 'landhalfhours', 'ordercanncelednum',
       'commentnums', 'starprefer', 'novoters', 'consuming_capacity',
       'cancelrate', 'delta_price1', 'price_sensitive', 'hoteluv',
       'ordernum_oneyear', 'cr_pre', 'avgprice', 'lowestprice',
       'customereval_pre2', 'delta_price2', 'commentnums_pre',
       'customer_value_profit', 'commentnums_pre2', 'cancelrate_pre',
       'novoters_pre2', 'novoters_pre', 'ctrip_profits', 'deltaprice_pre2_t1',
       'lowestprice_pre', 'uv_pre', 'uv_pre2', 'lowestprice_pre2',
       'lasthtlordergap', 'businessrate_pre2', 'cityuvs', 'cityorders',
       'lastpvgap', 'cr', 'sid', 'visitnum_oneyear', 'h', 'day_advanced',
       'arrival_weekday', 'is_arrival_weekend']

X, y = preprocess_data( all_features,rawdf)
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size= 0.05,random_state=420)
predicted_values_xgb,xgb,fpr_xgb, tpr_xgb ,score_xgb,auc_xgb = train_predict_and_evaluate_xgb(X_train, y_train, X_test, y_test,'rusult')