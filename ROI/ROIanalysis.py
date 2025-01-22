import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from ROIfunction import calculate_commission
import plotly.graph_objects as go
# from ROI_new import calculate_commission

def find_optimal_path(current_gmv, current_roi, ROI, GMV, Z):
    """
    找到从当前位置到最优点的路径，并计算每个阶段的优化方向
    """
    # 找到当前位置最接近的网格点
    current_idx = (
        np.abs(GMV[:,0] - current_gmv).argmin(),
        np.abs(ROI[0,:] - current_roi).argmin()
    )
    
    # 找到最优点
    max_idx = np.unravel_index(Z.argmax(), Z.shape)
    
    # 生成路径点
    steps = 5  # 减少步数以便更清晰地显示每个阶段
    path_gmv = np.linspace(GMV[current_idx[0], current_idx[1]], GMV[max_idx[0], max_idx[1]], steps)
    path_roi = np.linspace(ROI[current_idx[0], current_idx[1]], ROI[max_idx[0], max_idx[1]], steps)
    
    # 计算路径上的提成金额
    path_z = np.zeros(steps)
    for i in range(steps):
        _, commission_cny, bonus = calculate_commission(float(path_gmv[i]), float(path_roi[i]))
        path_z[i] = commission_cny + bonus  # 将提成和奖励合并
    
    # 计算每个阶段的优化方向
    directions = []
    for i in range(steps-1):
        delta_gmv = path_gmv[i+1] - path_gmv[i]
        delta_roi = path_roi[i+1] - path_roi[i]
        
        # 计算当前点周围的梯度
        gmv_grad = calculate_gradient_gmv(path_gmv[i], path_roi[i])
        roi_grad = calculate_gradient_roi(path_gmv[i], path_roi[i])
        
        # 根据梯度决定优化方向
        if abs(gmv_grad) > abs(roi_grad):
            directions.append(('GMV', delta_gmv, delta_roi))
        else:
            directions.append(('ROI', delta_gmv, delta_roi))
    
    return path_gmv, path_roi, path_z, directions

def calculate_gradient_gmv(gmv, roi, delta=0.1):
    """计算GMV方向的梯度"""
    _, commission1, bonus1 = calculate_commission(gmv, roi)
    _, commission2, bonus2 = calculate_commission(gmv + delta, roi)
    return ((commission2 + bonus2) - (commission1 + bonus1)) / delta

def calculate_gradient_roi(gmv, roi, delta=0.1):
    """计算ROI方向的梯度"""
    _, commission1, bonus1 = calculate_commission(gmv, roi)
    _, commission2, bonus2 = calculate_commission(gmv, roi + delta)
    return ((commission2 + bonus2) - (commission1 + bonus1)) / delta

def plot_optimization_arrow(ax, pos_gmv, pos_roi, pos_z, direction, scale=2):
    """绘制优化方向箭头"""
    if direction[0] == 'GMV':
        color = 'black'
        label = 'GMV优先'
    else:
        color = 'blue'
        label = 'ROI优先'
    
    # 计算箭头方向
    arrow_length = scale
    if direction[0] == 'GMV':
        dx, dy = 0, arrow_length
    else:
        dx, dy = arrow_length, 0
    
    ax.quiver(pos_roi, pos_gmv, pos_z, 
              dx, dy, 0,
              color=color, alpha=0.8, 
              arrow_length_ratio=0.2)
    
    return label

def create_3d_analysis(current_gmv=None, current_roi=None):
    """创建交互式3D分析图"""
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号
    
    # 创建ROI和GMV的数值范围
    roi_range = np.linspace(1.0, 3.5, 50)
    gmv_range = np.linspace(0.5, 60, 50)
    
    # 创建网格
    ROI, GMV = np.meshgrid(roi_range, gmv_range)
    
    # 计算提成金额（人民币）
    Z = np.zeros_like(ROI)
    for i in range(len(gmv_range)):
        for j in range(len(roi_range)):
            _, cny_amount, bonus = calculate_commission(float(GMV[i,j]), float(ROI[i,j]))
            Z[i,j] = cny_amount + bonus  # 将提成和奖励合并
    
    # 创建3D图表
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制3D表面图
    surf = ax.plot_surface(ROI, GMV, Z, cmap='viridis', alpha=0.8)
    
    # 如果提供了当前位置，计算并显示优化路径
    if current_gmv is not None and current_roi is not None:
        # 计算当前提成
        _, current_commission, current_bonus = calculate_commission(current_gmv, current_roi)
        current_total = current_commission + current_bonus
        
        # 找到优化路径和方向
        path_gmv, path_roi, path_z, directions = find_optimal_path(current_gmv, current_roi, ROI, GMV, Z)
        
        # 绘制当前点
        ax.scatter([current_roi], [current_gmv], [current_commission], 
                  color='red', s=100, label='当前位置')
        
        # 绘制优化路径
        ax.plot(path_roi, path_gmv, path_z, 'gray', linewidth=1, linestyle='--', label='优化路径')
        
        # 创建自定义图例的元素
        from matplotlib.lines import Line2D
        custom_lines = [
            Line2D([0], [0], color='black', marker='^', linestyle='none', 
                  markersize=10, label='优先提升GMV'),
            Line2D([0], [0], color='blue', marker='^', linestyle='none', 
                  markersize=10, label='优先提升ROI'),
            Line2D([0], [0], color='red', marker='o', linestyle='none', 
                  markersize=10, label='当前位置'),
            Line2D([0], [0], color='green', marker='o', linestyle='none', 
                  markersize=10, label='最优位置'),
            Line2D([0], [0], color='gray', linestyle='--', 
                  label='优化路径')
        ]
        
        # 绘制每个阶段的优化方向
        for i in range(len(directions)):
            plot_optimization_arrow(ax, path_gmv[i], path_roi[i], path_z[i], 
                                 directions[i])
        
        # 绘制最优点
        max_commission_idx = np.unravel_index(Z.argmax(), Z.shape)
        ax.scatter([ROI[max_commission_idx]], [GMV[max_commission_idx]], [Z[max_commission_idx]], 
                  color='green', s=100)
    
    ax.set_xlabel('ROI值')
    ax.set_ylabel('GMV (万美元)')
    ax.set_zlabel('提成金额 (万人民币)')
    ax.set_title('提成金额与ROI、GMV的关系(3D视图)')
    
    # 添加自定义图例
    if current_gmv is not None:
        ax.legend(handles=custom_lines, loc='upper left', bbox_to_anchor=(1.15, 1))
    
    # 添加颜色条
    fig.colorbar(surf, ax=ax, label='提成金额 (万人民币)')
    
    plt.tight_layout()
    plt.show()
    
    # 计算并打印分析结果
    max_commission_idx = np.unravel_index(Z.argmax(), Z.shape)
    optimal_gmv = GMV[max_commission_idx]
    optimal_roi = ROI[max_commission_idx]
    max_commission = Z[max_commission_idx]
    
    print(f"\n最优参数分析:")
    print(f"最高提成金额: {max_commission:.2f}万人民币")
    print(f"对应GMV: {optimal_gmv:.2f}万美元")
    print(f"对应ROI: {optimal_roi:.2f}")
    
    if current_gmv is not None and current_roi is not None:
        _, current_commission, current_bonus = calculate_commission(current_gmv, current_roi)
        current_total = current_commission + current_bonus
        print(f"\n当前状态:")
        print(f"当前提成金额: {current_commission:.2f}万人民币")
        print(f"当前任务奖励: {current_bonus:.2f}万人民币")
        print(f"当前总收入: {current_total:.2f}万人民币")

def analyze_commission(current_gmv=None, current_roi=None):
    """
    分析并返回可视化结果和数据分析
    
    参数:
        current_gmv: float, 当前GMV值（万美元）
        current_roi: float, 当前ROI值
        
    返回:
        dict: 包含图表对象和分析结果的字典
    """
    # 创建3D分析图
    fig = create_3d_analysis(current_gmv, current_roi)
    
    # 准备分析结果
    results = {}
    if current_gmv is not None and current_roi is not None:
        _, current_commission, current_bonus = calculate_commission(current_gmv, current_roi)
        current_total = current_commission + current_bonus
        results = {
            'current_commission': current_commission,
            'current_gmv': current_gmv,
            'current_roi': current_roi
        }
    
    return {
        'figure': fig,
        'results': results,
        'instructions': """
### 图例说明：
- 红色点：当前位置
- 绿色点：最优位置
- 灰色虚线：优化路径

### 操作说明：
- 鼠标拖动可旋转视图
- 滚轮可缩放视图
- 双击可重置视图
- 右上角工具栏提供更多视图操作选项
        """
    }

if __name__ == "__main__":
    # 示例：分析当前位置 GMV=20, ROI=2.0 的优化路径
    analyze_commission(current_gmv=21.4, current_roi=2.07)
