import pandas as pd

# 读取两个CSV文件
refund_df = pd.read_csv('refund_order_processed.csv')
total_df = pd.read_csv('total_order_no_duplicates.csv')

# 创建一个字典来存储退货产品统计
product_counts = {}

# 遍历退货订单
for prefix in refund_df['order_id_prefix']:
    # 在总订单中查找匹配的订单
    matched_order = total_df[total_df['*订单编号'] == prefix]
    
    if not matched_order.empty:
        # 获取对应的商品名称
        product_name = matched_order.iloc[0]['商品名称']
        
        # 统计商品出现次数
        if product_name in product_counts:
            product_counts[product_name] += 1
        else:
            product_counts[product_name] = 1

# 将统计结果转换为DataFrame
result_df = pd.DataFrame(list(product_counts.items()), columns=['商品名称', '退货数量'])

# 计算总退货订单数
total_refunds = len(refund_df)

# 计算每个商品的退货比例
result_df['退货比例'] = result_df['退货数量'] / total_refunds * 100

# 按退货数量降序排序
result_df = result_df.sort_values('退货数量', ascending=False)

# 添加总计行
total_row = pd.DataFrame({
    '商品名称': ['总计'],
    '退货数量': [total_refunds],
    '退货比例': [100.0]
})
result_df = pd.concat([result_df, total_row])

# 格式化退货比例为百分比形式（保留2位小数）
result_df['退货比例'] = result_df['退货比例'].apply(lambda x: f'{x:.2f}%')

# 保存结果到新的CSV文件
result_df.to_csv('refund_product_analysis.csv', index=False, encoding='utf-8-sig')
