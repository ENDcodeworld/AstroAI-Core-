"""
天文数据可视化模块
提供光变曲线、光谱、星图等可视化功能
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional, Dict
import matplotlib.patches as mpatches


class LightCurvePlotter:
    """光变曲线绘图器"""
    
    def __init__(self, figsize=(12, 6)):
        self.figsize = figsize
        
    def plot_lightcurve(self,
                       time: np.ndarray,
                       flux: np.ndarray,
                       flux_err: Optional[np.ndarray] = None,
                       period: Optional[float] = None,
                       title: str = "Light Curve",
                       phase_fold: bool = False,
                       save_path: Optional[str] = None):
        """
        绘制光变曲线
        
        Args:
            time: 时间数组（天）
            flux: 流量数组
            flux_err: 流量误差
            period: 周期（用于相位折叠）
            title: 图表标题
            phase_fold: 是否进行相位折叠
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        if phase_fold and period:
            # 相位折叠
            phase = (time % period) / period
            xlabel = "Phase"
            xdata = phase
        else:
            xlabel = "Time (days)"
            xdata = time
        
        # 绘制数据点
        if flux_err is not None:
            ax.errorbar(xdata, flux, yerr=flux_err, fmt='o', 
                       markersize=3, alpha=0.6, capsize=2, label='Data')
        else:
            ax.scatter(xdata, flux, s=10, alpha=0.6, label='Data')
        
        # 如果有周期，绘制折叠后的平均值
        if phase_fold and period:
            # 分箱平均
            bins = np.linspace(0, 1, 50)
            digitized = np.digitize(phase, bins)
            bin_means = [flux[digitized == i].mean() 
                        for i in range(1, len(bins))]
            bin_centers = (bins[:-1] + bins[1:]) / 2
            ax.plot(bin_centers, bin_means, 'r-', linewidth=2, label='Binned Mean')
        
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel("Relative Flux", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig, ax
    
    def plot_folded_transits(self,
                            time: np.ndarray,
                            flux: np.ndarray,
                            period: float,
                            t0: float,
                            duration: float,
                            title: str = "Folded Transit",
                            save_path: Optional[str] = None):
        """
        绘制折叠的凌日曲线
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 相位折叠到凌日中心
        phase = ((time - t0) % period) / period
        phase[phase > 0.5] -= 1  # 中心化到凌日
        
        # 只绘制凌日前后的数据
        mask = np.abs(phase) < 0.1
        
        ax.scatter(phase[mask], flux[mask], s=20, alpha=0.5, c='blue', label='Data')
        
        # 标注凌日持续时间
        ax.axvline(-duration/2/24/period, color='red', linestyle='--', alpha=0.5)
        ax.axvline(duration/2/24/period, color='red', linestyle='--', alpha=0.5)
        ax.axvspan(-duration/2/24/period, duration/2/24/period, alpha=0.1, color='red', label='Transit')
        
        ax.set_xlabel("Phase", fontsize=12)
        ax.set_ylabel("Relative Flux", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-0.1, 0.1)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig, ax


class SpectrumPlotter:
    """光谱绘图器"""
    
    def __init__(self, figsize=(14, 6)):
        self.figsize = figsize
        
    def plot_spectrum(self,
                     wavelength: np.ndarray,
                     flux: np.ndarray,
                     spectral_lines: Optional[Dict[str, float]] = None,
                     title: str = "Stellar Spectrum",
                     normalize: bool = True,
                     save_path: Optional[str] = None):
        """
        绘制光谱
        
        Args:
            wavelength: 波长数组（埃）
            flux: 流量数组
            spectral_lines: 要标记的谱线字典 {名称: 波长}
            title: 图表标题
            normalize: 是否归一化
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 归一化
        if normalize:
            flux = flux / np.median(flux)
        
        # 绘制光谱
        ax.plot(wavelength, flux, 'k-', linewidth=0.8, label='Spectrum')
        
        # 标记特征谱线
        if spectral_lines:
            for name, wave in spectral_lines.items():
                if wavelength.min() <= wave <= wavelength.max():
                    ax.axvline(wave, color='r', linestyle='--', alpha=0.3)
                    ax.text(wave, ax.get_ylim()[1]*0.95, name, 
                           rotation=90, fontsize=8, ha='right')
        
        ax.set_xlabel("Wavelength (Å)", fontsize=12)
        ax.set_ylabel("Normalized Flux", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig, ax
    
    def plot_multi_spectra(self,
                          spectra: List[Tuple[str, np.ndarray, np.ndarray]],
                          title: str = "Multi-Species Comparison",
                          save_path: Optional[str] = None):
        """
        绘制多个光谱比较
        
        Args:
            spectra: [(标签, 波长, 流量), ...]
            title: 图表标题
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(spectra)))
        
        for i, (label, wave, flux) in enumerate(spectra):
            # 归一化并偏移以便比较
            flux_norm = flux / np.median(flux) + i * 0.5
            ax.plot(wave, flux_norm, color=colors[i], linewidth=0.8, label=label)
        
        ax.set_xlabel("Wavelength (Å)", fontsize=12)
        ax.set_ylabel("Normalized Flux + Offset", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig, ax


class SkyMapPlotter:
    """星空图绘图器"""
    
    def __init__(self, figsize=(12, 8)):
        self.figsize = figsize
        
    def plot_skymap(self,
                   ra: np.ndarray,
                   dec: np.ndarray,
                   mag: Optional[np.ndarray] = None,
                   color: Optional[np.ndarray] = None,
                   title: str = "Sky Map",
                   projection: str = 'mollweide',
                   save_path: Optional[str] = None):
        """
        绘制星空图
        
        Args:
            ra: 赤经（度）
            dec: 赤纬（度）
            mag: 视星等（用于控制点大小）
            color: 颜色值（用于颜色映射）
            title: 图表标题
            projection: 投影类型
            save_path: 保存路径
        """
        fig = plt.figure(figsize=self.figsize)
        ax = fig.add_subplot(111, projection=projection)
        
        # 转换到弧度
        ra_rad = np.radians(ra)
        dec_rad = np.radians(dec)
        
        # 调整RA范围到[-π, π]
        ra_rad = np.where(ra_rad > np.pi, ra_rad - 2*np.pi, ra_rad)
        
        # 点大小基于星等（越亮越大）
        if mag is not None:
            sizes = (6 - mag) * 20  # 星等越小（越亮），点越大
            sizes = np.clip(sizes, 1, 200)
        else:
            sizes = 10
        
        # 颜色
        if color is not None:
            scatter = ax.scatter(ra_rad, dec_rad, s=sizes, c=color, 
                               cmap='viridis', alpha=0.6)
            plt.colorbar(scatter, ax=ax, label='Color Index')
        else:
            ax.scatter(ra_rad, dec_rad, s=sizes, alpha=0.6, c='blue')
        
        ax.set_xlabel("Right Ascension", fontsize=12)
        ax.set_ylabel("Declination", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig, ax
    
    def plot_constellation(self,
                          stars_ra: np.ndarray,
                          stars_dec: np.ndarray,
                          stars_mag: np.ndarray,
                          connections: List[Tuple[int, int]],
                          title: str = "Constellation",
                          save_path: Optional[str] = None):
        """
        绘制星座连线图
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 绘制恒星
        sizes = (6 - stars_mag) * 30
        sizes = np.clip(sizes, 5, 300)
        ax.scatter(stars_ra, stars_dec, s=sizes, c='white', alpha=0.9, zorder=2)
        
        # 绘制连线
        for i, j in connections:
            ax.plot([stars_ra[i], stars_ra[j]], [stars_dec[i], stars_dec[j]], 
                   'w-', linewidth=1, alpha=0.6, zorder=1)
        
        # 设置黑色背景（夜空）
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        
        ax.set_xlabel("Right Ascension (°)", fontsize=12, color='white')
        ax.set_ylabel("Declination (°)", fontsize=12, color='white')
        ax.set_title(title, fontsize=14, fontweight='bold', color='white')
        ax.tick_params(colors='white')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='black')
        
        return fig, ax


class HRDiagramPlotter:
    """赫罗图绘图器"""
    
    def __init__(self, figsize=(10, 8)):
        self.figsize = figsize
        
    def plot_hr_diagram(self,
                       color_index: np.ndarray,
                       absolute_mag: np.ndarray,
                       spectral_types: Optional[np.ndarray] = None,
                       title: str = "H-R Diagram",
                       save_path: Optional[str] = None):
        """
        绘制赫罗图
        
        Args:
            color_index: 颜色指数（B-V）
            absolute_mag: 绝对星等
            spectral_types: 光谱类型（用于颜色）
            title: 图表标题
            save_path: 保存路径
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # 颜色映射
        if spectral_types is not None:
            # 将光谱型映射到颜色
            type_colors = {'O': 'blue', 'B': 'cyan', 'A': 'white', 
                          'F': 'lightyellow', 'G': 'yellow', 
                          'K': 'orange', 'M': 'red'}
            colors = [type_colors.get(t, 'gray') for t in spectral_types]
        else:
            colors = 'blue'
        
        # 绘制散点
        ax.scatter(color_index, absolute_mag, c=colors, s=20, alpha=0.6)
        
        # 反转Y轴（越亮越小）
        ax.invert_yaxis()
        
        # 标注区域
        ax.axhspan(-10, -5, alpha=0.1, color='blue', label='Supergiants')
        ax.axhspan(10, 15, alpha=0.1, color='red', label='White Dwarfs')
        
        ax.set_xlabel("Color Index (B-V)", fontsize=12)
        ax.set_ylabel("Absolute Magnitude", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        
        # 设置黑色背景
        ax.set_facecolor('black')
        fig.patch.set_facecolor('black')
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='black')
        
        return fig, ax


if __name__ == "__main__":
    print("=" * 60)
    print("🌌 AstroAI-Core - 天文数据可视化系统")
    print("=" * 60)
    
    # 测试光变曲线
    print("\n📊 生成测试光变曲线...")
    np.random.seed(42)
    
    time = np.linspace(0, 30, 3000)
    flux = np.ones_like(time)
    
    # 添加周期性凌日
    period = 5.0
    for t0 in np.arange(2.5, 30, period):
        mask = np.abs(time - t0) < 0.1
        flux[mask] *= 0.99
    
    # 添加噪声
    flux += np.random.normal(0, 0.001, len(flux))
    
    lc_plotter = LightCurvePlotter()
    
    fig1, _ = lc_plotter.plot_lightcurve(
        time, flux, 
        title="Simulated Exoplanet Light Curve",
        save_path="/tmp/lightcurve.png"
    )
    print("   ✅ 光变曲线已保存到 /tmp/lightcurve.png")
    
    # 测试相位折叠
    fig2, _ = lc_plotter.plot_folded_transits(
        time, flux, period=5.0, t0=2.5, duration=3.0,
        save_path="/tmp/folded_transit.png"
    )
    print("   ✅ 折叠凌日曲线已保存到 /tmp/folded_transit.png")
    
    # 测试光谱
    print("\n📈 生成测试光谱...")
    wavelength = np.linspace(4000, 7000, 3000)
    flux_spec = np.ones_like(wavelength)
    
    # 添加Balmer线
    for line in [4102, 4340, 4861, 6563]:
        mask = np.abs(wavelength - line) < 20
        flux_spec[mask] *= (1 - 0.1 * np.exp(-((wavelength[mask] - line)/5)**2))
    
    spec_plotter = SpectrumPlotter()
    spectral_lines = {
        'Hδ': 4102,
        'Hγ': 4340,
        'Hβ': 4861,
        'Hα': 6563
    }
    
    fig3, _ = spec_plotter.plot_spectrum(
        wavelength, flux_spec,
        spectral_lines=spectral_lines,
        title="Stellar Spectrum with Balmer Lines",
        save_path="/tmp/spectrum.png"
    )
    print("   ✅ 光谱图已保存到 /tmp/spectrum.png")
    
    print("\n" + "=" * 60)
    print("✅ 可视化系统测试完成！")
    print("=" * 60)
