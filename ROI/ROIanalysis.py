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
    """Draw optimization direction arrow"""
    if direction[0] == 'GMV':
        color = 'black'
        label = 'GMV Priority'
    else:
        color = 'blue'
        label = 'ROI Priority'
    
    # Calculate arrow direction
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
    """Create interactive 3D analysis plot"""
    # Create ROI and GMV value ranges
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
                  color='red', s=100, label='Current Position')
        
        # 绘制优化路径
        ax.plot(path_roi, path_gmv, path_z, 'gray', linewidth=1, linestyle='--', label='Optimization Path')
        
        # 创建自定义图例的元素
        from matplotlib.lines import Line2D
        custom_lines = [
            Line2D([0], [0], color='black', marker='^', linestyle='none', 
                  markersize=10, label='GMV Priority'),
            Line2D([0], [0], color='blue', marker='^', linestyle='none', 
                  markersize=10, label='ROI Priority'),
            Line2D([0], [0], color='red', marker='o', linestyle='none', 
                  markersize=10, label='Current Position'),
            Line2D([0], [0], color='green', marker='o', linestyle='none', 
                  markersize=10, label='Optimal Position'),
            Line2D([0], [0], color='gray', linestyle='--', 
                  label='Optimization Path')
        ]
        
        # 绘制每个阶段的优化方向
        for i in range(len(directions)):
            plot_optimization_arrow(ax, path_gmv[i], path_roi[i], path_z[i], 
                                 directions[i])
        
        # 绘制最优点
        max_commission_idx = np.unravel_index(Z.argmax(), Z.shape)
        ax.scatter([ROI[max_commission_idx]], [GMV[max_commission_idx]], [Z[max_commission_idx]], 
                  color='green', s=100)
    
    ax.set_xlabel('ROI Value')
    ax.set_ylabel('GMV (10k USD)')
    ax.set_zlabel('Commission Amount (10k CNY)')
    ax.set_title('Commission Amount vs ROI & GMV (3D View)')
    
    # 添加自定义图例
    if current_gmv is not None:
        ax.legend(handles=custom_lines, loc='upper left', bbox_to_anchor=(1.15, 1))
    
    # 添加颜色条
    fig.colorbar(surf, ax=ax, label='Commission Amount (10k CNY)')
    
    plt.tight_layout()
    plt.show()
    
    # 计算并打印分析结果
    max_commission_idx = np.unravel_index(Z.argmax(), Z.shape)
    optimal_gmv = GMV[max_commission_idx]
    optimal_roi = ROI[max_commission_idx]
    max_commission = Z[max_commission_idx]
    
    print(f"\nOptimal Parameters Analysis:")
    print(f"Maximum Commission: {max_commission:.2f} 10k CNY")
    print(f"Corresponding GMV: {optimal_gmv:.2f} 10k USD")
    print(f"Corresponding ROI: {optimal_roi:.2f}")
    
    if current_gmv is not None and current_roi is not None:
        _, current_commission, current_bonus = calculate_commission(current_gmv, current_roi)
        current_total = current_commission + current_bonus
        print(f"\nCurrent Status:")
        print(f"Current Commission: {current_commission:.2f} 10k CNY")
        print(f"Current Task Bonus: {current_bonus:.2f} 10k CNY")
        print(f"Current Total Income: {current_total:.2f} 10k CNY")

def analyze_commission(current_gmv=None, current_roi=None):
    """
    Analyze and return visualization results and data analysis
    
    Parameters:
        current_gmv: float, current GMV value (10k USD)
        current_roi: float, current ROI value
        
    Returns:
        dict: Dictionary containing chart objects and analysis results
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
### Legend Description:
- Red dot: Current Position
- Green dot: Optimal Position
- Gray dashed line: Optimization Path

### Operation Instructions:
- Drag mouse to rotate view
- Scroll wheel to zoom
- Double click to reset view
- More view options in top-right toolbar
        """
    }

if __name__ == "__main__":
    # 示例：分析当前位置 GMV=20, ROI=2.0 的优化路径
    analyze_commission(current_gmv=21.4, current_roi=2.07)
