import math

def sigmoid(x: float, center: float, steepness: float = 10) -> float:
    """
    计算sigmoid函数值，用于平滑过渡
    """
    return 1 / (1 + math.exp(-steepness * (x - center)))

def calculate_commission(gmv: float, roi: float) -> tuple[float, float]:
    """
    计算销售提成金额的函数（使用平滑过渡）
    
    参数:
        gmv: float - 当月GMV(美元，万美元)
        roi: float - ROI值
        
    返回:
        tuple[float, float]: (美元提成金额, 人民币提成金额) (单位：万元)
    """
    # ROI提成系数计算（使用sigmoid函数实现平滑过渡）
    roi_points = [(1.5, 0.002), (1.6, 0.004), (1.7, 0.005), (2.0, 0.007),
                  (2.1, 0.008), (2.2, 0.01), (2.3, 0.012), (2.4, 0.014),
                  (2.5, 0.016), (3.0, 0.018)]
    
    roi_commission = 0.002  # 基础值
    for i, (threshold, rate) in enumerate(roi_points):
        transition = sigmoid(roi, threshold)
        if i < len(roi_points) - 1:
            roi_commission += (roi_points[i+1][1] - rate) * transition
    
    # 处理ROI > 3.0的情况
    roi_commission += (0.02 - 0.018) * sigmoid(roi, 3.0)

    # GMV系数计算（使用sigmoid函数实现平滑过渡）
    gmv_points = [(1.5, 0.6), (3, 0.8), (6, 1.15), (10, 1.2),
                  (15, 1.3), (20, 1.4), (30, 1.5), (50, 1.6)]
    
    gmv_multiplier = 0.6  # 基础值
    for i, (threshold, rate) in enumerate(gmv_points):
        transition = sigmoid(gmv, threshold)
        if i < len(gmv_points) - 1:
            gmv_multiplier += (gmv_points[i+1][1] - rate) * transition
    
    # 处理GMV > 50的情况
    gmv_multiplier += (2.0 - 1.6) * sigmoid(gmv, 50)

    # ... existing code ...
    # 最终提成 = ROI提成系数 × GMV系数
    commission_rate = roi_commission * gmv_multiplier
    
    # 计算最终提成金额（美元）
    final_commission_usd = gmv * commission_rate
    
    # 转换为人民币 (汇率 1:7)
    final_commission_cny = final_commission_usd * 7
    
    return final_commission_usd, final_commission_cny