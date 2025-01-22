def calculate_commission(gmv: float, roi: float, target_gmv: float = 0) -> tuple[float, float, float]:
    """
    计算销售提成金额的函数
    
    参数:
        gmv: float - 当月GMV(美元，万美元)
        roi: float - ROI值
        target_gmv: float - 当月GMV目标值(美元，万美元)
        
    返回:
        tuple[float, float, float]: (美元提成金额, 人民币提成金额, 任务量奖励) (单位：万元)
    """
    # 首先根据ROI确定基础提成系数
    roi_commission = 0
    if roi < 1.5:
        roi_commission = 0.000
    elif 1.5 <= roi < 1.6:
        roi_commission = 0.002
    elif 1.6 <= roi < 1.7:
        roi_commission = 0.004
    elif 1.7 <= roi < 1.8:
        roi_commission = 0.005
    elif 1.8 <= roi < 1.9:
        roi_commission = 0.007
    elif 1.9 <= roi < 2.0:
        roi_commission = 0.009
    elif 2.0 <= roi < 2.2:
        roi_commission = 0.010
    elif 2.2 <= roi < 2.4:
        roi_commission = 0.012
    elif 2.4 <= roi < 2.6:
        roi_commission = 0.014
    elif 2.6 <= roi < 2.8:
        roi_commission = 0.016
    elif 2.8 <= roi < 3.1:
        roi_commission = 0.018
    elif roi >= 3.1:
        roi_commission = 0.02

    # 然后根据GMV确定GMV系数
    gmv_multiplier = 0
    if gmv <= 1.5:
        gmv_multiplier = 0.6
    elif 1.5 < gmv <= 3:
        gmv_multiplier = 0.8
    elif 3 < gmv <= 6:
        gmv_multiplier = 1.15
    elif 6 < gmv <= 10:
        gmv_multiplier = 1.2
    elif 10 < gmv <= 15:
        gmv_multiplier = 1.3
    elif 15 < gmv <= 20:
        gmv_multiplier = 1.4
    elif 20 < gmv <= 30:
        gmv_multiplier = 1.5
    elif 30 < gmv <= 50:
        gmv_multiplier = 1.6
    elif gmv > 50:
        gmv_multiplier = 2.0

    # 最终提成 = ROI提成系数 × GMV系数
    commission_rate = roi_commission * gmv_multiplier
    
    # 计算最终提成金额（美元）
    final_commission_usd = gmv * commission_rate
    
    # 转换为人民币 (汇率 1:7)，不进行四舍五入，保持完整精度
    final_commission_cny = final_commission_usd * 7.0
    
    # 计算任务量奖励（人民币）
    task_bonus = 0.0
    if target_gmv > 0:  # 只有设置了目标值才计算奖励
        completion_rate = gmv / target_gmv
        if completion_rate >= 2.0:
            task_bonus = 0.2  # 2000RMB = 0.2万
        elif completion_rate >= 1.5:
            task_bonus = 0.1  # 1000RMB = 0.1万
        elif completion_rate >= 1.2:
            task_bonus = 0.05  # 500RMB = 0.05万
        elif completion_rate >= 1.0:
            task_bonus = 0.03  # 300RMB = 0.03万
    
    return final_commission_usd, final_commission_cny, task_bonus

# 示例：如果GMV=5万美元，ROI=2.2，目标GMV=4万美元
usd_commission, cny_commission, bonus = calculate_commission(21.4, 2.07, 5)
print(f"美元提成金额为: {usd_commission:.2f}万USD")
print(f"提成金额为: {cny_commission:.2f}万人民币")
print(f"任务量奖励为: {bonus:.2f}万人民币")
print(f"总收入为: {(cny_commission + bonus):.2f}万人民币")
