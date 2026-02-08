#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#导入基础包
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")
# 解决中文乱码问题
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
#显示全部特征
pd.set_option('display.max_columns', None)


input_train_filepath = sys.argv[1]



#读取数据
df = pd.read_csv(input_train_filepath)





# 由直方图可以看出绝大部分不符合正态分布

# 访问时间和到达时间的表格
# 
# 分别按照访问时间、到达时间统计个数
# 
# 按照时间做链接

# In[ ]:


# copy一份数据保存
cdf = df.copy()




# 上述的表格可视化
# 

# In[ ]:


# 获取字段



# 由图看出，520前预定人数和入住人数逐渐攀升，在520当天达到峰值，过了521，入住人数断崖式下降，随后酒店入住人数较为稳定，后面的两个下波峰是由于周末的原因。

# ### 2.3.3 访问时间段

# In[ ]:


plt.figure(figsize=(15,6))
plt.hist(cdf.h.dropna(), bins=48, align='mid')  # 由于是24h，所以分箱48，使得中间有间隔。
plt.title('访问时间段',fontsize=20);
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
plt.xlabel('访问时间',fontsize=14); 
plt.ylabel('人数',fontsize=14);


# 由访问时间段可以看出，在 凌晨四五点的时候访问人数最少，此时大多数人在睡觉，因此这符合人的作息。随后访问人数在白天总体呈上升趋势，在17点-19点时稍微回落，因为此时是人的下班通勤时间或者晚饭时间，过了这段时间访问人数又开始逐渐上升，在22时达到峰值。
# 
# ### 2.3.4 客户价值

# In[ ]:


plt.figure(figsize=(12, 4))
plt.style.use('bmh')

# 看看customer_value_profit 和 ctrip_profits 两者分布
plt.subplot(121)
plt.plot(cdf.index, cdf.customer_value_profit,linewidth=0.5)
plt.title('客户近1年价值')

plt.subplot(122)
plt.plot(df.index,df.ctrip_profits,linewidth=0.5)
plt.title('客户价值')




# 客户近一年的价值图和客户价值图大体上很相似，大多数人分布在0~100的范围内。另外，由于两个特征分布上非常接近，后面可以对customer_value_profit和ctrip_profits进行相关性分析验证，如果相关系数很大，可以考虑进行PCA降维。
# 
# 不排除有些客户价值非常大，峰值达到了600，这些客户都可以在之后的分析中重点观察，因为他们是非常有“价值”的。但是这些峰值过大的客户，数据可能存在极值点过大的情况，因此需要对数据进一步处理。
# 
# 另外，可以看出，两个字段都存在部分数据的客户价值为负，这些是异常值，需要处理。
# 

# ### 2.3.5 消费能力指数

# In[ ]:


plt.figure(figsize=(12, 4))
#统计每个区间内数据出现的频率（或者数量）
plt.hist(df.consuming_capacity,bins=50,edgecolor='k')
plt.xlabel('消费能力指数')
plt.ylabel('人数')
plt.title('消费能力指数图')



# 我们可以看到，消费能力指数的值范围是0-100。消费能力指数值基本呈现一个右偏的正态分布，平均消费能力在30附近，我们也能看到消费能力达到近100的人数也特别多，达到了21000多人，从这一点上，我们可以看到，酒店的入住客户中仍然存在较大群体的富裕人士。
# 
# ### 2.3.6 价格敏感指数分布

# In[ ]:


plt.figure(figsize=(12, 6))
plt.hist(df['price_sensitive'].dropna(),bins = 50, edgecolor = 'k')
plt.xlabel('价格敏感指数') 
plt.ylabel('人数') 
plt.title('价格敏感指数分布')

plt.show()


# 在价格敏感指数图中，出现两头存在极值现象，中间的分布也总体上呈现一个右偏正态分布，大部分人对价格并不敏感，对于这些用户来说，价格不是考虑的最重要因素。当然，我们也会发现，价格敏感指数为100时的人数也并不少，针对这一部分客户，我们可以考虑用一些打折优惠的方式吸引消费
# 
# 2.3.6 入住酒店平均价格

# In[ ]:


plt.figure(figsize=(12, 4))
plt.subplot(121)
plt.hist(df.avgprice.dropna(),bins=50,edgecolor = 'k')
plt.xlabel('酒店价格')
plt.ylabel('偏好人数')
plt.title('酒店价格偏好')


# 由于酒店价格主要在2000以内，因此针对这个区间进行进一步可视化查看
plt.subplot(122)
plt.hist(df[df.avgprice<2000]['avgprice'].dropna(), bins = 50, edgecolor = 'k')
plt.xlabel('酒店价格')
plt.ylabel('偏好人数')
plt.title('2000元以内酒店偏好')




# 看出酒店价格偏好呈现一个正太分布微左偏态的分布，大多数人的价值偏好在150~600元之间，，在1500过后就没有什么人了。平均价格在250左右。
# 
# 2.3.7 酒店星级偏好

# In[ ]:


plt.figure(figsize=(10, 4))
plt.hist(df.starprefer.dropna(), bins = 50, edgecolor = 'k')
plt.xlabel('星级偏好程度')
plt.ylabel('选择人数')
plt.title('酒店星级偏好')



# 存在大量的用户订单取消率为0的情况，说明大多数用户订了酒店后就会入住。而同时也存在部分极端用户，订单取消率为1的情况。订单取消率为0.5的用户第三多。
# 
# ### 2.3.9 用户年订单数分布

# In[ ]:


plt.figure(figsize=(12, 6))
plt.hist(df[df["ordernum_oneyear"]<100]["ordernum_oneyear"].dropna(),bins = 50, edgecolor = 'k')
plt.xlabel('用户年订单数') 
plt.ylabel('数量') 
plt.title('用户年订单数100内的分布')

plt.show()





# 新老客户，可以由sid来判断。流失与否，用label来判断
# 计算新老用户流失率
s_table = cdf[['label','sid']]
s_table['sid'] = np.where(s_table['sid']==1, 1, 0)  # 将sid处理为0和1两种情况，对应新客户和老客户
s_table['flag'] = 1  # 
s = s_table.groupby('sid').sum().reset_index()  # 按照新老用户区分，label是流失和没流失的人数，flag是新、老用户数
print(s.head(10))
s['rate'] = s['label'] / s['flag']  # 新老用户流失率

print(s_table.head(10))
# 画图
# 新老客户占比
plt.figure(figsize=(12, 5))
plt.subplot(121)
percent=[s['flag'][0]/s['flag'].sum(), s['flag'][1]/s['flag'].sum()]
# color=['steelblue','lightskyblue']
label=['老客','新客']
plt.pie(percent,autopct='%.2f%%',labels=label)
plt.title('新老客户占比')

# 流失率
plt.subplot(122)
plt.bar(s.sid, s.rate,align='center',tick_label=label,edgecolor = 'k')
plt.ylabel('流失率')
plt.title('新老客户中的客户流失率');

