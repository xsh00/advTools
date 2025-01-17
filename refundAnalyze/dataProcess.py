import pandas as pd

# 读取 Excel 文件
refund_df = pd.read_excel('data/XSH12月退款.xlsx')
order_df = pd.read_excel('data/12月退款周期总订单.xlsx')


# 将 Excel 转换为 CSV
refund_df.to_csv('data/refund_order.csv', index=False, encoding='utf-8-sig')
order_df.to_csv('data/total_order.csv', index=False, encoding='utf-8-sig')


# 假设订单编号列名为'order_id'
# 将订单编号拆分为两列：前半部分和后10位
refund_df['order_id_prefix'] = refund_df['对应订单编号'].str[:-10]  # 提取除了最后10位的部分
refund_df['order_id_suffix'] = refund_df['对应订单编号'].str[-10:]  # 提取最后10位

# 假设订单序号列名为 'order_id'，保留第一次出现的行
df_no_duplicates = order_df.drop_duplicates(subset=['*订单编号'], keep='first')


# 保存处理后的结果
df_no_duplicates.to_csv('data/total_order_no_duplicates.csv', index=False, encoding='utf-8-sig')

# 保存处理后的结果
refund_df.to_csv('data/refund_order_processed.csv', index=False)