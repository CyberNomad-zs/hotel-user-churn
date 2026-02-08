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

warnings.filterwarnings("ignore")



input_train_filepath = sys.argv[1]  # 参数1：训练数据的CSV文件路径
model_save_path = sys.argv[2]       # 参数2：训练好模型的保存路径 (.pkl文件)
model_name = sys.argv[3]            # 参数3：要使用的模型名称 (如 xgb, rf, cnn)




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
    df = pd.read_csv(input_train_filepath)

    rawdf = df.copy()
    return rawdf  # 返回处理后的特征矩阵和目标变量

def preprocess_data(selected_features,rawdf):
    # 选择指定特征
    rawdf = rawdf[selected_features]
    
    # 分割特征和目标变量
    y = rawdf['label']
    x = rawdf.drop('label', axis=1)

    # 特征缩放
    scaler = RobustScaler()  #鲁棒缩放器
    scaler.fit(x)            #计算数据的统计量（这里是计算中位数和四分位距），这就好比是“制定标准”
    X = scaler.transform(x)  #利用刚才计算出的标准，把数据转换成缩放后的形式

    return X, y              #返回处理后的特征矩阵和目标变量


def train_evaluate_extra_trees(X_train, y_train, X_test, y_test,file_name):
    # 创建并训练Extra Trees分类器
    ET = ExtraTreesClassifier(n_estimators=100, random_state=42)
    ET.fit(X_train, y_train)
    
    # 预测结果
    y_prob = ET.predict_proba(X_test)[:, 1]  # 预测1类的概率
    y_ET_pred = ET.predict(X_test)  # 模型对测试集的预测结果
    
    # 计算准确率和AUC得分
    score_ET = metrics.accuracy_score(y_test, y_ET_pred)
    fpr_ET, tpr_ET, threshold_ET = metrics.roc_curve(y_test, y_prob)
    auc_ET = metrics.auc(fpr_ET, tpr_ET)

    write_results_to_file(score_ET, auc_ET, y_test,y_ET_pred, 'ET', file_name)
    return y_ET_pred,ET,fpr_ET, tpr_ET,score_ET,auc_ET



# ## 封装XGB方法


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

    # 获取真阳率、伪阳率、阈值
    fpr_xgb, tpr_xgb, threshold_xgb = roc_curve(y_test, y_prob)   
    auc_xgb = auc(fpr_xgb, tpr_xgb)    # AUC得分
    score_xgb = accuracy_score(y_test, y_pred)    # 模型准确率
    # print('=========================xgb-start===================================')
    # print('xgb模型准确率为:{0}, AUC得分为:{1}'.format(score_xgb, auc_xgb))
    # print('============================================================')
    # print(classification_report(y_test, y_pred, digits=2))
    # print('=========================xgb-END===================================')
    write_results_to_file(score_xgb, auc_xgb, y_test,y_pred, 'xgb', file_name)
    return y_pred,bst,fpr_xgb, tpr_xgb,score_xgb,auc_xgb


# ## 封装RF方法
def train_evaluate_random_forest(X_train, y_train, X_test, y_test,file_name):
    rfc = RandomForestClassifier()  # 建立随机森林分类器
    rfc.fit(X_train, y_train)  # 训练随机森林模型
    y_prob = rfc.predict_proba(X_test)[:, 1]  # 预测1类的概率
    y_rfc_pred = rfc.predict(X_test)  # 模型对测试集的预测结果
    fpr_rfc, tpr_rfc, threshold_rfc = metrics.roc_curve(y_test, y_prob)  # 获取真阳率、伪阳率、阈值
    auc_rfc = metrics.auc(fpr_rfc, tpr_rfc)  # AUC得分
    score_rfc = metrics.accuracy_score(y_test, y_rfc_pred)  # 模型准确率
    # print('=========================RF-start===================================')
    # print('模型准确率为:{0},AUC得分为:{1}'.format(score_rfc, auc_rfc))
    # print('============================================================')
    # print(classification_report(y_test, y_rfc_pred, labels=None, target_names=None, sample_weight=None, digits=2))
    print('=========================RF-end===================================')
    write_results_to_file(score_rfc, auc_rfc, y_test,y_rfc_pred, 'RF', file_name)
    # 返回预测结果
    return y_rfc_pred,rfc,fpr_rfc, tpr_rfc,score_rfc,auc_rfc



# ## 分装DF
def train_predict_and_evaluate_dtc(X_train, y_train, X_test, y_test,file_name):
    dtc = tree.DecisionTreeClassifier()  # 建立决策树模型
    dtc.fit(X_train, y_train)  # 训练模型
    y_prob = dtc.predict_proba(X_test)[:, 1]  # 预测1类的概率
    y_df_pred = dtc.predict(X_test)  # 模型对测试集的预测结果
    fpr_dtc, tpr_dtc, threshod_dtc = metrics.roc_curve(y_test, y_prob)  # 获取真阳率、伪阳率、阈值
    score_dtc = metrics.accuracy_score(y_test, y_df_pred)
    auc_dtc = metrics.auc(fpr_dtc, tpr_dtc)
    # print('==========================DF-start==================================')
    # print('模型准确率为:{0}, AUC得分为:{1}'.format(score_dtc, auc_dtc))
    # print('============================================================')
    # print(classification_report(y_test, y_df_pred, labels=None, target_names=None, sample_weight=None, digits=2))
    
    write_results_to_file(score_dtc, auc_dtc, y_test,y_df_pred, 'DF', file_name)
    return y_df_pred,dtc,fpr_dtc, tpr_dtc,score_dtc,auc_dtc


# ## 分装DF
def get_dtc_accuracy_score(X_train, y_train, X_test, y_test):
    dtc = tree.DecisionTreeClassifier()  # 建立决策树模型
    dtc.fit(X_train, y_train)  # 训练模型
    y_df_pred = dtc.predict(X_test)  # 模型对测试集的预测结果
    return metrics.accuracy_score(y_test, y_df_pred)



# ## 封装CatBoostClassifier

def train_predict_and_evaluate_clf(X_train, y_train, X_test, y_test,file_name):
    # 初始化 CatBoost 分类器
    clf = CatBoostClassifier(iterations=1000, learning_rate=0.1, depth=6, loss_function='Logloss')
    # 训练模型
    clf.fit(X_train, y_train)
    y_prob = clf.predict_proba(X_test)[:, 1]  # 预测1类的概率
    y_clf_pred = clf.predict(X_test)  # 模型对测试集的预测结果
    fpr_clf, tpr_clf, threshod_clf = metrics.roc_curve(y_test, y_prob)  # 获取真阳率、伪阳率、阈值
    score_clf = metrics.accuracy_score(y_test, y_clf_pred)
    auc_clf = metrics.auc(fpr_clf, tpr_clf)
    # print('==========================clf-start==================================')
    # print('模型准确率为:{0}, AUC得分为:{1}'.format(score_clf, auc_clf))
    # print('============================================================')
    # print(classification_report(y_test, y_clf_pred, labels=None, target_names=None, sample_weight=None, digits=2))
    
    write_results_to_file(score_clf, auc_clf, y_test,y_clf_pred, 'CatBoost', file_name)
    return y_clf_pred,clf,fpr_clf, tpr_clf,score_clf,auc_clf



###  AdaBoost方法

def train_and_evaluate_adaboost(X_train, y_train, X_test, y_test,file_name):
    # 初始化 AdaBoostClassifier 模型
    adaboost = AdaBoostClassifier()
    adaboost.fit(X_train, y_train)
    
    # 预测概率和分类结果
    y_prob = adaboost.predict_proba(X_test)[:,1]
    y_pred = adaboost.predict(X_test)
    
    # 计算真阳率、伪阳率、AUC
    fpr_adaboost, tpr_adaboost, threshold_adaboost = metrics.roc_curve(y_test, y_prob)
    auc_adaboost = metrics.auc(fpr_adaboost, tpr_adaboost)
    
    # 计算准确率
    score_adaboost = metrics.accuracy_score(y_test, y_pred)
    
    # 打印结果
    # print('模型准确率为:{0},AUC得分为:{1}'.format(score_adaboost, auc_adaboost))
   
    # print(classification_report(y_test, y_pred, labels=None, target_names=None, sample_weight=None, digits=2))

    write_results_to_file(score_adaboost, auc_adaboost, y_test,y_pred, 'AdaBoost', file_name)

    return y_pred,adaboost,fpr_adaboost, tpr_adaboost,score_adaboost,auc_adaboost



## 封装的逻辑回归

def train_and_evaluate_lr(X_train, y_train, X_test, y_test,file_name):
    # 初始化 Logistic Regression 模型
    lr = LogisticRegression()
    lr.fit(X_train, y_train)
    
    # 预测概率和分类结果
    y_prob = lr.predict_proba(X_test)[:, 1]  
    y_pred = lr.predict(X_test)  
    
    # 计算真阳率、伪阳率、AUC
    fpr_lr, tpr_lr, threshold_lr = metrics.roc_curve(y_test, y_prob)  
    auc_lr = metrics.auc(fpr_lr, tpr_lr)
    
    # 计算准确率
    score_lr = metrics.accuracy_score(y_test, y_pred)

    # 打印结果
    # print('模型准确率为:{0}, AUC得分为:{1}'.format(score_lr, auc_lr))
    # print(classification_report(y_test, y_pred))
 
    write_results_to_file(score_lr, auc_lr, y_test,y_pred, 'lr', file_name)

    return y_pred,lr,fpr_lr, tpr_lr,score_lr,auc_lr


### 贝叶斯
def train_and_evaluate_gnb(X_train, y_train, X_test, y_test,file_name):
    # 初始化 Gaussian Naive Bayes 模型
    gnb = GaussianNB()
    gnb.fit(X_train,y_train)          
    
    # 预测概率和分类结果
    y_prob = gnb.predict_proba(X_test)[:,1]                           
    y_pred = gnb.predict(X_test)                                     
    
    # 计算真阳率、伪阳率、AUC
    fpr_gnb,tpr_gnb,threshold_gnb = metrics.roc_curve(y_test,y_prob)
    auc_gnb = metrics.auc(fpr_gnb,tpr_gnb)                            

    # 计算准确率
    score_gnb = metrics.accuracy_score(y_test,y_pred)                 

    # 打印结果
    # print('模型准确率为:{0},AUC得分为:{1}'.format(score_gnb,auc_gnb))
    # print('============================================================')
    # print(classification_report(y_test, y_pred, labels=None, target_names=None, sample_weight=None, digits=2))
   
    write_results_to_file(score_gnb,auc_gnb, y_test,y_pred, 'gnb', file_name)
    return y_pred,gnb,fpr_gnb,tpr_gnb,score_gnb,auc_gnb


import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, roc_curve, auc
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, roc_curve, auc

def train_evaluate_mlp(X_train, y_train, X_test, y_test, file_name):
    # 1. 转换为PyTorch张量
    X_train = torch.FloatTensor(X_train)
    y_train = torch.LongTensor(y_train)
    X_test = torch.FloatTensor(X_test)

    # 2. 定义MLP模型（3层全连接）
    model = nn.Sequential(
        nn.Linear(X_train.shape[1], 64),  # 输入层
        nn.ReLU(),
        nn.Linear(64, 32),                # 隐藏层
        nn.ReLU(),
        nn.Linear(32, 2)                 # 输出层
    )

    # 3. 训练配置
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # 4. 训练循环（10个epoch）
    for epoch in range(10):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

    # 5. 预测评估
    with torch.no_grad():
        y_prob = torch.softmax(model(X_test), dim=1)[:, 1].numpy()
        y_pred = model(X_test).argmax(dim=1).numpy()

    score = accuracy_score(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc_score = auc(fpr, tpr)
    write_results_to_file(score,auc_score, y_test,y_pred, 'mlp', file_name)
    return y_pred, model, fpr, tpr, score, auc_score


def train_evaluate_dnn(X_train, y_train, X_test, y_test, file_name):
    # 1. 转换为PyTorch张量
    X_train = torch.FloatTensor(X_train)
    y_train = torch.LongTensor(y_train)
    X_test = torch.FloatTensor(X_test)

    # 2. 直接构建Sequential模型（无需类定义）
    model = nn.Sequential(
        nn.Linear(X_train.shape[1], 64),
        nn.ReLU(),
        nn.Linear(64, 2)
    )

    # 3. 训练配置
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())

    # 4. 训练循环
    for epoch in range(10):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

    # 5. 预测评估
    with torch.no_grad():
        y_prob = torch.softmax(model(X_test), dim=1)[:, 1].numpy()
        y_pred = model(X_test).argmax(dim=1).numpy()

    score = accuracy_score(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc_score = auc(fpr, tpr)
    write_results_to_file(score,auc_score, y_test,y_pred, 'dnn', file_name)

    return y_pred, model, fpr, tpr, score, auc_score


def train_evaluate_cnn(X_train, y_train, X_test, y_test, file_name):
    # 1. 转换为PyTorch张量并reshape为CNN输入格式 (样本数, 通道数, 特征长度)
    X_train = torch.FloatTensor(X_train).unsqueeze(1)  # 添加通道维度
    y_train = torch.LongTensor(y_train)
    X_test = torch.FloatTensor(X_test).unsqueeze(1)

    # 2. 极简CNN模型 (1D卷积适用于表格数据)
    model = nn.Sequential(
        nn.Conv1d(1, 16, kernel_size=3, padding=1),  # 16个卷积核
        nn.ReLU(),
        nn.MaxPool1d(2),
        nn.Flatten(),
        nn.Linear(16 * (X_train.shape[2]//2), 2)     # 自动计算全连接层输入大小
    )

    # 3. 训练配置
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters())

    # 4. 训练循环
    for epoch in range(10):
        optimizer.zero_grad()
        outputs = model(X_train)
        loss = criterion(outputs, y_train)
        loss.backward()
        optimizer.step()

    # 5. 预测评估
    with torch.no_grad():
        y_prob = torch.softmax(model(X_test), dim=1)[:, 1].numpy()
        y_pred = model(X_test).argmax(dim=1).numpy()

    score = accuracy_score(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc_score = auc(fpr, tpr)
    write_results_to_file(score,auc_score, y_test,y_pred, 'cnn', file_name)
    return y_pred, model, fpr, tpr, score, auc_score



## SVC支持向量机
def train_and_evaluate_svc(X_train, y_train, X_test, y_test,file_name):
    # 初始化 Support Vector Classifier (SVC) 模型
    svc = SVC(kernel='rbf', C=1, max_iter=100)
    svc.fit(X_train, y_train)
    
    # 预测概率和分类结果
    y_prob = svc.decision_function(X_test)
    y_pred = svc.predict(X_test)
    
    # 计算真阳率、伪阳率、AUC
    fpr_svc, tpr_svc, threshold_svc = metrics.roc_curve(y_test, y_prob)
    auc_svc = metrics.auc(fpr_svc, tpr_svc)
    
    # 计算准确率
    score_svc = metrics.accuracy_score(y_test, y_pred)

    write_results_to_file(score_svc,auc_svc, y_test,y_pred, 'svc', file_name)
    return y_pred,svc,fpr_svc, tpr_svc,score_svc,auc_svc

    import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve

# 定义绘制学习曲线的函数
def plot_learning_curve(estimator, title, X, y, ylim=None, cv=None,
                        n_jobs=None, train_sizes=np.linspace(.1, 1.0, 5)):
    plt.figure()
    plt.title(title)
    if ylim is not None:
        plt.ylim(*ylim)
    plt.xlabel("Training examples")
    plt.ylabel("Score")
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=n_jobs, train_sizes=train_sizes)
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std,
                     train_scores_mean + train_scores_std, alpha=0.1,
                     color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std,
                     test_scores_mean + test_scores_std, alpha=0.1, color="g")
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r",
             label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g",
             label="Cross-validation score")

    plt.legend(loc="best")
    return plt



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
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size= 0.2,random_state=420)



MODEL_FUNCTIONS = {
    "adaboost": train_and_evaluate_adaboost,
    "clf": train_predict_and_evaluate_clf,
    "dtc": train_predict_and_evaluate_dtc,
    "xgb": train_predict_and_evaluate_xgb,
    "et": train_evaluate_extra_trees,      # 可选别名
    "random_forest": train_evaluate_random_forest,
    "rf": train_evaluate_random_forest,    # 别名
    "lr": train_and_evaluate_lr,
    "gnb": train_and_evaluate_gnb,
    "svm": train_and_evaluate_svc,
    "dnn": train_evaluate_dnn,
    "cnn": train_evaluate_cnn,
    "mlp": train_evaluate_mlp,
}

def run_model_by_name(model_name, X_train, y_train, X_test, y_test, tag='result'):
    key = model_name.lower()
    if key not in MODEL_FUNCTIONS:
        available = ", ".join(sorted(MODEL_FUNCTIONS.keys()))
        raise ValueError(f"未知模型名 '{model_name}'. 可用模型：{available}")
    func = MODEL_FUNCTIONS[key]
    # 调用对应函数并返回其结果
    return func(X_train, y_train, X_test, y_test, tag)



def run_single_model(model_name, X_train, y_train, X_test, y_test, tag='result'):

    key = model_name.strip().lower()
    if key not in MODEL_FUNCTIONS:
        available = ", ".join(sorted(MODEL_FUNCTIONS.keys()))
        raise ValueError(f"not find  '{model_name}'. model_lists:{available}")
    func = MODEL_FUNCTIONS[key]
    return func(X_train, y_train, X_test, y_test, tag)


try:
    pred, model_obj, fpr, tpr, score, auc = run_single_model(
        model_name, X_train, y_train, X_test, y_test, tag='result'
    )

    joblib.dump(model_obj, model_save_path)
    print(f"model {model_name} finish score={score}, auc={auc:.4f}")
except ValueError as e:
    print(e)
