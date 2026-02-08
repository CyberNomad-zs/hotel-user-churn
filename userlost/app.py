from flask import Flask, jsonify
import pandas as pd
from flask_cors import CORS  # 导入 CORS 类
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

app = Flask(__name__)
CORS(app)  # 对应用启用 CORS，允许所有来源的跨域请求



@app.route('/')
def index():
    return "Welcome to the traffic prediction system API!"

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 返回无内容响应

@app.route('/api/visit_arrival_data')
def visit_arrival_data():
    # 读取并处理数据
    df = pd.read_csv('./data/userlostprob_train.csv')  # 根据实际路径调整
    cdf = df.copy()

    # 统计 d 和 arrival 的频次并明确列名
    cdf_d = cdf['d'].value_counts().reset_index()
    cdf_d.columns = ['index', 'd']
    cdf_arrival = cdf['arrival'].value_counts().reset_index()
    cdf_arrival.columns = ['index', 'arrival']

    # 合并
    time_table = pd.merge(cdf_d, cdf_arrival, how='outer', on='index')
    time_table.fillna(0, inplace=True)

    # 尝试把 index 转为 datetime，如果可行则按时间排序
    try:
        time_table['index'] = pd.to_datetime(time_table['index'])
        time_table.sort_values('index', inplace=True)
        # 将 datetime 转为字符串（ISO 格式）以便 JSON 序列化，前端可再解析为 Date
        x = time_table['index'].dt.strftime('%Y-%m-%dT%H:%M:%S').tolist()
    except Exception:
        # 不是时间格式则按字符串排序
        time_table.sort_values('index', inplace=True)
        x = time_table['index'].astype(str).tolist()

    # 转为整数列表
    y1 = time_table['arrival'].astype(int).tolist()
    y2 = time_table['d'].astype(int).tolist()

    return jsonify({'x': x, 'arrival': y1, 'd': y2})




if __name__ == '__main__':
    app.run(debug=True)