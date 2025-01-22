import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ROIanalysis import analyze_commission
from ROIfunction import calculate_commission

def main():
    # 设置页面标题
    st.title('销售提成优化分析系统')
    
    # 添加说明文字
    st.write('请输入当前GMV和ROI值，系统将为您分析最优化路径。')
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    # 在左列添加GMV输入
    with col1:
        current_gmv = st.number_input(
            'GMV (万美元)',
            min_value=0.5,
            max_value=60.0,
            value=20.0,
            step=0.5,
            help='请输入当前GMV值（单位：万美元）'
        )
    
    # 在右列添加ROI输入
    with col2:
        current_roi = st.number_input(
            'ROI值',
            min_value=1.0,
            max_value=3.5,
            value=2.0,
            step=0.1,
            help='请输入当前ROI值'
        )
        target_gmv = st.number_input(
            'GMV目标值 (万美元)',
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
            help='请输入当月GMV目标值（单位：万美元），如无目标可保持为0'
        )
    
    # 添加当前提成计算结果显示
    st.write('### 当前提成计算结果')
    usd_commission, cny_commission, bonus = calculate_commission(current_gmv, current_roi, target_gmv)
    total_income = cny_commission + bonus
    
    # 使用列布局显示计算结果
    result_col1, result_col2, result_col3 = st.columns(3)
    with result_col1:
        st.metric(
            label="美元提成", 
            value=f"{usd_commission:.2f}万美元"
        )
    with result_col2:
        st.metric(
            label="人民币提成", 
            value=f"{cny_commission:.2f}万元"
        )
    with result_col3:
        st.metric(
            label="任务量奖励", 
            value=f"{bonus:.2f}万元"
        )
    
    # 显示总收入
    st.metric(
        label="总收入",
        value=f"{total_income:.2f}万元"
    )
    
    # 如果设置了目标值，显示完成率
    if target_gmv > 0:
        completion_rate = (current_gmv / target_gmv) * 100
        st.metric(
            label="目标完成率",
            value=f"{completion_rate:.1f}%",
            delta=f"{completion_rate - 100:.1f}%" if completion_rate != 100 else "达标"
        )
    
    # 添加分割线
    st.markdown("---本月优化分析---")
    
    # 添加分析按钮
    if st.button('开始分析'):
        # 创建图形
        fig = plt.figure(figsize=(12, 8))
        
        # 调用分析函数
        analyze_commission(current_gmv, current_roi)
        
        # 显示图形
        st.pyplot(plt)
        
        # 清除当前图形，为下次分析做准备
        plt.close()
        
        # 添加说明
        st.write("""
        ### 图例说明：
        - 黑色箭头：建议优先提升GMV
        - 蓝色箭头：建议优先提升ROI
        - 红色点：当前位置
        - 绿色点：最优位置
        - 灰色虚线：优化路径
        """)

if __name__ == "__main__":
    main() 