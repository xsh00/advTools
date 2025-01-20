import os
import csv
import random
from openpyxl import Workbook
from datetime import datetime, timedelta
import names


def web(product, country, total_num):
    Comment = generate_comment(total_num)

    local_file_path = 'res/comment.csv'
    file_path = f'res/{product}_comment.xlsx'
    # 创建并写入新的 CSV 文件
    with open(local_file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        header = [
            "商品Handle(必须)", "姓名(必须)", "评分(必须,分值为1-5)",
            "日期(格式：YYYY/MM/DD)", "国家", "内容",
            "点赞数", "图片链接地址[用英文,分割]"
        ]

        # 写入表头
        writer.writerow(header)

        # 写入数据，内容列填入内容列表中的数据
        for content in Comment:
            row = [
                product,  # 商品Handle(必须)
                names.get_full_name(),  # 姓名(必须)
                random.randint(4, 5),  # 评分(必须,分值为1-5)
                generate_random_dates('2024-01-01', '2024-6-5', 1),  # 日期(格式：YYYY/MM/DD)
                country,  # 国家
                content,  # 内容
                random.randint(45, 105),  # 点赞数
                ""  # 图片链接地址[用英文,分割]
            ]
            writer.writerow(row)

    def write_data_to_xlsx(xlsx_file):
        # 创建一个工作簿对象
        wb = Workbook()
        ws = wb.active

        # 写入表头
        ws.append(header)

        # 写入数据
        for i in Comment:
            r = [
                product,  # 商品Handle(必须)
                names.get_full_name(),  # 姓名(必须)
                random.randint(4, 5),  # 评分(必须,分值为1-5)
                generate_random_dates('2024-01-01', '2024-9-19', 1),  # 日期(格式：YYYY/MM/DD)
                country,  # 国家
                i,  # 内容
                random.randint(45, 105),  # 点赞数
                ""  # 图片链接地址[用英文,分割]
            ]
            ws.append(r)

        # 保存工作簿为XLSX文件
        wb.save(xlsx_file)

    write_data_to_xlsx(file_path)
    current_directory = os.path.dirname(os.path.abspath(__file__))
    abs_file_path = os.path.join(current_directory, file_path)

    return abs_file_path



def generate_random_dates(start, end, count, date_format='%Y/%m/%d'):
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    random_date = ''
    for _ in range(count):
        random_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        random_date = (random_date.strftime(date_format))

    return random_date

def generate_comment(total_num):
    Comment = []

    # 读取Template.txt文件内容
    with open('Template.txt', 'r', encoding='utf-8') as file:
        templates = [line.strip() for line in file if line.strip()]
    
    # 确保模板数量足够
    if len(templates) < 5:
        raise ValueError("模板数量不足，至少需要5个不同的模板")

    # 使用集合来跟踪最近使用的评论
    recent_comments = set()

    # 随机选择并添加内容到Comment列表
    for _ in range(total_num):
        available_templates = [t for t in templates if t not in recent_comments]
        
        if not available_templates:
            # 如果所有模板都被使用过，重置最近使用的评论集合
            recent_comments.clear()
            available_templates = templates

        random_comment = random.choice(available_templates)
        Comment.append(random_comment)

        # 更新最近使用的评论集合
        recent_comments.add(random_comment)
        if len(recent_comments) > 5:
            recent_comments.pop()

    return Comment

