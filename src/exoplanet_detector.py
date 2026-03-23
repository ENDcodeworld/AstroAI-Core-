"""
系外行星检测模块
使用光变曲线分析检测行星凌日信号
"""

import numpy as np
from scipy import signal
from scipy.optimize import curve_fit
from typing import Tuple, List, Dict, Optional
import warnings


class TransitDetector:
    """行星凌日检测器"""
    
    def __init__(self, 
                 period_min: float = 0.5,  # 天
                 period_max: float = 365.0,
                 duration_max: float = 0.5):  # 天
        self.period_min = period_min
        self.period_max = period_max
        self.duration_max = duration_max
        
    def box_least_squares(self,
                          time: np.ndarray,
                          flux: np.ndarray,
                          flux_err: Optional[np.ndarray] = None) -> Dict:
        """
        Box Least Squares (BLS) 算法检测周期性凌日信号
        
        Args:
            time: 时间数组 (天)
            flux: 光变流量（归一化）
            flux_err: 流量误差
            
        Returns:
            检测结果字典
        """
        # 数据预处理
        time = np.array(time)
        flux = np.array(flux)
        
        # 移除趋势
        flux_detrended = self._detrend_flux(time, flux)
        
        # BLS搜索参数
        n_periods = 1000
        periods = np.linspace(self.period_min, self.period_max, n_periods)
        
        best_period = None
        best_power = 0
        best_t0 = None
        best_duration = None
        best_depth = None
        
        for period in periods:
            # 相位折叠
            phase = (time % period) / period
            
            # 尝试不同持续时间
            for duration in np.linspace(0.01, min(self.duration_max / period, 0.3), 20):
                # 滑动窗口
                powers = []
                t0s = np.linspace(0, 1 - duration, 50)
                
                for t0 in t0s:
                    # 创建箱型模型
                    in_transit = ((phase >= t0) & (phase < t0 + duration))
                    
                    if np.sum(in_transit) < 3:
                        continue
                    
                    # 计算BLS功率
                    out_transit = ~in_transit
                    r = np.sum(in_transit) / len(in_transit)
                    
                    if r == 0 or r == 1:
                        continue
                    
                    s = np.sum(flux_detrended[in_transit])
                    
                    delta = s / np.sum(in_transit) - np.mean(flux_detrended[out_transit])
                    power = delta**2 * r * (1 - r)
                    
                    powers.append((t0, power, delta))
                
                if powers:
                    max_power_idx = np.argmax([p[1] for p in powers])
                    if powers[max_power_idx][1] > best_power:
                        best_power = powers[max_power_idx][1]
                        best_period = period
                        best_t0 = powers[max_power_idx][0] * period
                        best_duration = duration * period
                        best_depth = -powers[max_power_idx][2]  # 负号因为凌日是流量下降
        
        # 计算信噪比
        snr = self._calculate_snr(time, flux_detrended, best_period, best_t0, best_duration, best_depth)
        
        return {
            'period_days': best_period,
            'epoch': best_t0,
            'duration_hours': best_duration * 24 if best_duration else None,
            'depth_ppm': best_depth * 1e6 if best_depth else None,
            'power': best_power,
            'snr': snr,
            'is_planet_candidate': snr > 10 and best_depth > 0.0001
        }
    
    def _detrend_flux(self, time: np.ndarray, flux: np.ndarray, window: int = 101) -> np.ndarray:
        """使用滑动窗口移除趋势"""
        if window % 2 == 0:
            window += 1
        
        # 使用Savitzky-Golay滤波器平滑
        try:
            trend = signal.savgol_filter(flux, window, 3)
            return flux / trend
        except:
            # 如果失败，使用简单多项式拟合
            coeffs = np.polyfit(time - time[0], flux, 3)
            trend = np.polyval(coeffs, time - time[0])
            return flux / trend
    
    def _calculate_snr(self,
                      time: np.ndarray,
                      flux: np.ndarray,
                      period: float,
                      t0: float,
                      duration: float,
                      depth: float) -> float:
        """计算信噪比"""
        if period is None or depth is None or depth <= 0:
            return 0
        
        # 相位折叠
        phase = ((time - t0) % period) / period
        
        # 找出凌日中的点
        in_transit_mask = (phase >= 0) & (phase <= duration / period)
        in_transit_mask |= (phase >= 1 - duration / period)  # 处理相位环绕
        
        if np.sum(in_transit_mask) < 3:
            return 0
        
        # 计算凌日内外的标准差
        out_transit_mask = ~in_transit_mask
        noise = np.std(flux[out_transit_mask]) if np.sum(out_transit_mask) > 10 else 1e-4
        
        # 计算SNR
        n_transits = (time[-1] - time[0]) / period
        n_points_per_transit = np.sum(in_transit_mask) / n_transits
        
        snr = depth / noise * np.sqrt(n_points_per_transit * n_transits)
        
        return snr
    
    def fit_transit_model(self,
                         time: np.ndarray,
                         flux: np.ndarray,
                         period: float,
                         t0: float) -> Dict:
        """
        拟合凌日模型参数
        
        Args:
            time: 时间数组
            flux: 流量数组
            period: 周期
            t0: 参考时间
            
        Returns:
            拟合参数
        """
        # 相位折叠到凌日中心
        phase = ((time - t0) % period) / period
        phase[phase > 0.5] -= 1  # 中心化
        
        # 只取凌日前后的数据
        mask = np.abs(phase) < 0.1
        if np.sum(mask) < 10:
            return {}
        
        phase_fit = phase[mask]
        flux_fit = flux[mask]
        
        # 简化的梯形凌日模型
        def transit_model(p, depth, duration, ingress):
            """梯形凌日模型"""
            result = np.ones_like(p)
            
            half_dur = duration / 2
            
            for i, phase in enumerate(p):
                if np.abs(phase) < half_dur - ingress:
                    result[i] = 1 - depth
                elif np.abs(phase) < half_dur:
                    # 斜坡
                    frac = (half_dur - np.abs(phase)) / ingress
                    result[i] = 1 - depth * frac
            
            return result
        
        # 初始猜测
        p0 = [0.01, 0.05, 0.01]  # depth, duration, ingress
        
        try:
            popt, pcov = curve_fit(transit_model, phase_fit, flux_fit, p0=p0, maxfev=10000)
            
            return {
                'depth': popt[0],
                'duration': popt[1] * period * 24,  # 转换为小时
                'ingress_time': popt[2] * period * 24,  # 转换为小时
                'depth_ppm': popt[0] * 1e6
            }
        except:
            return {'depth': None, 'duration': None}


class StellarParameters:
    """恒星参数计算器"""
    
    @staticmethod
    def calculate_planet_radius(depth: float, stellar_radius: float) -> float:
        """
        从凌日深度计算行星半径
        
        Args:
            depth: 凌日深度（相对流量下降）
            stellar_radius: 恒星半径（太阳半径为单位）
            
        Returns:
            行星半径（地球半径为单位）
        """
        # (Rp/Rs)^2 = depth
        rp_rs = np.sqrt(depth)
        planet_radius_solar = stellar_radius * rp_rs
        
        # 转换为地球半径
        planet_radius_earth = planet_radius_solar * 109.2
        
        return planet_radius_earth
    
    @staticmethod
    def calculate_semi_major_axis(period_days: float, stellar_mass: float = 1.0) -> float:
        """
        从周期计算半长轴（开普勒第三定律）
        
        Args:
            period_days: 轨道周期（天）
            stellar_mass: 恒星质量（太阳质量为单位）
            
        Returns:
            半长轴（AU）
        """
        # a^3 / P^2 = M_star (简化版，单位AU, year, M_sun)
        period_years = period_days / 365.25
        a_au = (period_years**2 * stellar_mass)**(1/3)
        
        return a_au
    
    @staticmethod
    def estimate_equilibrium_temperature(stellar_temp: float,
                                        stellar_radius: float,
                                        semi_major_axis: float,
                                        albedo: float = 0.3) -> float:
        """
        估算行星平衡温度
        
        Args:
            stellar_temp: 恒星有效温度（K）
            stellar_radius: 恒星半径（太阳半径）
            semi_major_axis: 半长轴（AU）
            albedo: 反照率
            
        Returns:
            平衡温度（K）
        """
        # T_eq = T_star * sqrt(R_star / 2a) * (1 - A)^(1/4)
        r_star_m = stellar_radius * 6.957e8  # 转换为米
        a_m = semi_major_axis * 1.496e11     # 转换为米
        
        t_eq = stellar_temp * np.sqrt(r_star_m / (2 * a_m)) * (1 - albedo)**0.25
        
        return t_eq


class PlanetValidator:
    """行星候选体验证器"""
    
    def __init__(self):
        self.min_snr = 10
        self.min_depth = 100  # ppm
        self.max_depth = 0.1  # 10%
        
    def validate(self, detection_result: Dict) -> Tuple[bool, List[str]]:
        """
        验证检测结果是否为真正的行星候选体
        
        Args:
            detection_result: BLS检测结果
            
        Returns:
            (是否通过验证, 验证信息列表)
        """
        checks = []
        passed = True
        
        # 检查1: SNR
        if detection_result.get('snr', 0) >= self.min_snr:
            checks.append(f"✅ SNR = {detection_result['snr']:.1f} (>= {self.min_snr})")
        else:
            checks.append(f"❌ SNR = {detection_result['snr']:.1f} (< {self.min_snr})")
            passed = False
        
        # 检查2: 深度
        depth = detection_result.get('depth_ppm', 0)
        if self.min_depth <= depth <= self.max_depth * 1e6:
            checks.append(f"✅ 深度 = {depth:.0f} ppm (合理范围)")
        else:
            checks.append(f"❌ 深度 = {depth:.0f} ppm (超出范围)")
            passed = False
        
        # 检查3: 周期
        period = detection_result.get('period_days', 0)
        if 0.5 <= period <= 1000:
            checks.append(f"✅ 周期 = {period:.2f} 天 (合理范围)")
        else:
            checks.append(f"⚠️ 周期 = {period:.2f} 天 (需进一步验证)")
        
        # 检查4: 持续时间
        duration = detection_result.get('duration_hours', 0)
        if duration and 0.5 <= duration <= 24:
            checks.append(f"✅ 持续时间 = {duration:.2f} 小时 (合理)")
        else:
            checks.append(f"⚠️ 持续时间 = {duration:.2f} 小时 (需检查)")
        
        return passed, checks
    
    def check_false_positive(self,
                            time: np.ndarray,
                            flux: np.ndarray,
                            period: float,
                            t0: float) -> Dict:
        """
        检查假阳性信号（如食双星）
        
        Returns:
            假阳性指标
        """
        # 相位折叠
        phase = ((time - t0) % period) / period
        phase[phase > 0.5] -= 1
        
        # 检查V形特征（可能是双星）
        sorted_idx = np.argsort(phase)
        phase_sorted = phase[sorted_idx]
        flux_sorted = flux[sorted_idx]
        
        # 计算光变曲线的对称性
        center_idx = len(phase_sorted) // 2
        
        if center_idx > 10:
            left_flux = flux_sorted[:center_idx]
            right_flux = flux_sorted[center_idx:][::-1]
            min_len = min(len(left_flux), len(right_flux))
            
            symmetry = np.corrcoef(left_flux[:min_len], right_flux[:min_len])[0, 1]
        else:
            symmetry = 0
        
        # 检查二次凌日（相位0.5附近）
        secondary_mask = np.abs(phase - 0.5) < 0.05
        secondary_depth = 1 - np.median(flux[secondary_mask]) if np.sum(secondary_mask) > 5 else 0
        
        return {
            'symmetry_score': symmetry,
            'is_v_shaped': symmetry > 0.9,
            'secondary_depth': secondary_depth,
            'is_eclipsing_binary': secondary_depth > 0.001 or symmetry > 0.95
        }


if __name__ == "__main__":
    print("=" * 60)
    print("🔭 AstroAI-Core - 系外行星检测系统")
    print("=" * 60)
    
    # 生成模拟数据（类似Kepler光变曲线）
    print("\n📊 生成模拟光变曲线数据...")
    
    np.random.seed(42)
    
    # 模拟参数
    true_period = 10.5  # 天
    true_t0 = 2.0
    true_depth = 0.001  # 0.1%
    true_duration = 3.0  # 小时
    
    # 生成时间序列（90天观测）
    time = np.linspace(0, 90, 9000)
    
    # 基础流量
    flux = np.ones_like(time)
    
    # 添加凌日信号
    phase = ((time - true_t0) % true_period) / true_period
    in_transit = (phase >= 0) & (phase < true_duration / 24 / true_period)
    flux[in_transit] -= true_depth
    
    # 添加噪声
    noise = np.random.normal(0, 0.0005, len(time))
    flux += noise
    
    print(f"   观测时间: {time[0]:.1f} - {time[-1]:.1f} 天")
    print(f"   数据点数: {len(time)}")
    print(f"   模拟周期: {true_period} 天")
    print(f"   模拟深度: {true_depth*1e6:.0f} ppm")
    
    # 检测
    print("\n🔍 运行BLS检测算法...")
    detector = TransitDetector()
    result = detector.box_least_squares(time, flux)
    
    print("\n📋 检测结果:")
    print("-" * 40)
    print(f"   检测周期: {result['period_days']:.3f} 天 (真实值: {true_period} 天)")
    print(f"   凌日深度: {result['depth_ppm']:.0f} ppm (真实值: {true_depth*1e6:.0f} ppm)")
    print(f"   持续时间: {result['duration_hours']:.2f} 小时")
    print(f"   信噪比 (SNR): {result['snr']:.1f}")
    print(f"   是否候选体: {'✅ 是' if result['is_planet_candidate'] else '❌ 否'}")
    
    # 验证
    print("\n✅ 验证检测结果...")
    validator = PlanetValidator()
    passed, checks = validator.validate(result)
    
    print("\n   验证项目:")
    for check in checks:
        print(f"   {check}")
    
    # 计算行星参数
    print("\n🌍 推导行星参数:")
    print("-" * 40)
    
    stellar_params = StellarParameters()
    
    if result['depth_ppm']:
        planet_radius = stellar_params.calculate_planet_radius(
            result['depth_ppm'] / 1e6, 
            stellar_radius=1.0
        )
        print(f"   估算行星半径: {planet_radius:.2f} 地球半径")
    
    if result['period_days']:
        semi_major_axis = stellar_params.calculate_semi_major_axis(
            result['period_days'],
            stellar_mass=1.0
        )
        print(f"   估算轨道半长轴: {semi_major_axis:.3f} AU")
        
        # 估算平衡温度
        temp = stellar_params.estimate_equilibrium_temperature(
            stellar_temp=5778,
            stellar_radius=1.0,
            semi_major_axis=semi_major_axis
        )
        print(f"   估算平衡温度: {temp:.0f} K")
    
    # 假阳性检查
    print("\n⚠️ 假阳性检查...")
    fp_check = validator.check_false_positive(time, flux, result['period_days'], result['epoch'])
    
    if fp_check['is_eclipsing_binary']:
        print("   ⚠️ 警告: 可能为食双星系统！")
        print(f"      对称性: {fp_check['symmetry_score']:.3f}")
        print(f"      二次凌日深度: {fp_check['secondary_depth']*1e6:.0f} ppm")
    else:
        print("   ✅ 未检测到明显的食双星特征")
    
    print("\n" + "=" * 60)
    print("✅ 系外行星检测系统测试完成！")
    print("=" * 60)
