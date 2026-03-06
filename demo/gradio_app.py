"""
AstroAI-Core Gradio Demo
系外行星探测快速演示

运行方式:
    python app.py
    
部署到 HuggingFace Spaces:
    1. 创建 Space: https://huggingface.co/spaces
    2. 选择 Gradio 作为 SDK
    3. 上传此文件和 requirements.txt
"""

import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# 模拟系外行星凌日信号生成
def generate_transit_signal(phase, depth=0.01, duration=0.1):
    """生成模拟的凌日光变曲线"""
    flux = np.ones_like(phase)
    transit_mask = np.abs(phase - 0.5) < duration / 2
    flux[transit_mask] -= depth * np.exp(-((phase[transit_mask] - 0.5) / (duration / 4)) ** 2)
    noise = np.random.normal(0, 0.002, len(phase))
    return flux + noise

def detect_transit(flux_data, threshold=0.005):
    """简单的凌日信号检测算法"""
    flux = np.array(flux_data)
    mean_flux = np.mean(flux)
    std_flux = np.std(flux)
    
    # 检测显著下降
    dips = []
    for i in range(len(flux)):
        if flux[i] < mean_flux - threshold:
            dips.append(i)
    
    if len(dips) > 10:  # 至少有 10 个连续点
        return True, f"检测到潜在的凌日信号！深度：{mean_flux - np.mean(flux[dips]):.4f}"
    else:
        return False, "未检测到明显的凌日信号"

def analyze_light_curve(noise_level, planet_size, num_points):
    """分析光变曲线"""
    # 生成相位数据
    phase = np.linspace(0, 1, int(num_points))
    
    # 生成凌日信号
    depth = planet_size / 100.0  # 行星大小转换为深度
    flux = generate_transit_signal(phase, depth=depth)
    
    # 添加噪声
    noise = np.random.normal(0, noise_level / 1000.0, len(phase))
    flux = flux + noise
    
    # 检测凌日
    detected, message = detect_transit(flux)
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(phase, flux, 'b.', alpha=0.5, label='观测数据', markersize=2)
    
    # 绘制拟合曲线
    from scipy.signal import savgol_filter
    if len(flux) > 10:
        smoothed = savgol_filter(flux, min(51, len(flux) // 2), 3)
        ax.plot(phase, smoothed, 'r-', linewidth=2, label='平滑拟合')
    
    ax.axhline(y=1.0, color='g', linestyle='--', alpha=0.5, label='基准亮度')
    ax.set_xlabel('相位 (Phase)', fontsize=12)
    ax.set_ylabel('相对亮度 (Relative Flux)', fontsize=12)
    ax.set_title('系外行星凌日光变曲线分析', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 添加检测结果
    status_color = 'green' if detected else 'red'
    ax.text(0.02, 0.98, message, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor=status_color, alpha=0.2))
    
    plt.tight_layout()
    
    return fig, message

# 创建 Gradio 界面
with gr.Blocks(title="AstroAI-Core Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🌌 AstroAI-Core 系外行星探测 Demo
    
    体验 AI 驱动的天文数据分析！调整参数观察系外行星凌日信号的检测过程。
    
    **使用说明**：
    1. 调整噪声水平、行星大小和数据点数量
    2. 点击"分析光变曲线"按钮
    3. 查看检测结果和可视化图表
    
    🔗 完整项目：[GitHub](https://github.com/ENDcodeworld/AstroAI-Core)
    """)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 🔧 参数设置")
            noise_slider = gr.Slider(
                minimum=0.1, 
                maximum=10.0, 
                value=2.0, 
                step=0.1,
                label="噪声水平 (Noise Level)"
            )
            planet_slider = gr.Slider(
                minimum=0.5, 
                maximum=10.0, 
                value=2.0, 
                step=0.5,
                label="行星相对大小 (Planet Size %)"
            )
            points_slider = gr.Slider(
                minimum=100, 
                maximum=2000, 
                value=500, 
                step=100,
                label="数据点数量 (Number of Points)"
            )
            analyze_btn = gr.Button("🔍 分析光变曲线", variant="primary")
        
        with gr.Column():
            gr.Markdown("### 📊 分析结果")
            output_plot = gr.Plot(label="光变曲线")
            output_text = gr.Textbox(label="检测状态")
    
    # 绑定事件
    analyze_btn.click(
        fn=analyze_light_curve,
        inputs=[noise_slider, planet_slider, points_slider],
        outputs=[output_plot, output_text]
    )
    
    gr.Markdown("""
    ---
    **关于 AstroAI-Core**
    
    AstroAI-Core 是一个开源的天文数据分析平台，提供：
    - 🔭 系外行星自动探测
    - ⭐ 恒星 AI 分类
    - 🌌 异常天体识别
    - 📊 光谱分析
    
    由 [ENDcodeworld](https://github.com/ENDcodeworld) 开发 | MIT License
    """)

if __name__ == "__main__":
    demo.launch()
