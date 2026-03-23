"""
恒星光谱分类模块
使用机器学习对恒星光谱进行分类
"""

import numpy as np
from scipy import interpolate
from scipy.signal import savgol_filter
from typing import Dict, List, Tuple, Optional
import warnings


class SpectralClassifier:
    """光谱分类器"""
    
    # 哈佛光谱分类系统的标准颜色
    SPECTRAL_TYPES = ['O', 'B', 'A', 'F', 'G', 'K', 'M']
    
    # 每个光谱型的典型温度（K）
    TEMPERATURES = {
        'O': (30000, 50000),
        'B': (10000, 30000),
        'A': (7500, 10000),
        'F': (6000, 7500),
        'G': (5200, 6000),
        'K': (3700, 5200),
        'M': (2400, 3700)
    }
    
    # 每个光谱型的特征谱线（埃）
    CHARACTERISTIC_LINES = {
        'O': [4102, 4340, 4541, 4686],  # He II, Hγ
        'B': [4102, 4340, 4471, 4552],  # Hγ, Hδ, He I
        'A': [3933, 3968, 4102, 4340],  # Ca II H&K, Hγ
        'F': [3933, 3968, 4102, 4300],  # Ca II, Hγ, CH
        'G': [3933, 4226, 4300, 5175],  # Ca II, Ca I, CH, Mg I
        'K': [3933, 4226, 4300, 5890],  # Ca II, Ca I, Na I
        'M': [5890, 7665, 8190, 8542]   # Na I, K I, Ca II
    }
    
    def __init__(self):
        self.wavelength_range = (3800, 9000)  # 可见光范围（埃）
        
    def classify_by_color_indices(self,
                                   u_mag: float,
                                   g_mag: float,
                                   r_mag: float,
                                   i_mag: float) -> Dict:
        """
        使用颜色指数分类恒星
        
        Args:
            u_mag, g_mag, r_mag, i_mag: 不同波段的星等
            
        Returns:
            分类结果
        """
        # 计算颜色指数
        u_g = u_mag - g_mag
        g_r = g_mag - r_mag
        r_i = r_mag - i_mag
        
        # 使用SDSS颜色-光谱型关系进行简单分类
        if u_g < 0.5 and g_r < -0.2:
            spectral_type = 'O'
        elif u_g < 0.8 and g_r < 0.0:
            spectral_type = 'B'
        elif u_g < 1.2 and g_r < 0.3:
            spectral_type = 'A'
        elif g_r < 0.5:
            spectral_type = 'F'
        elif g_r < 0.7:
            spectral_type = 'G'
        elif g_r < 1.0:
            spectral_type = 'K'
        else:
            spectral_type = 'M'
        
        # 估算温度
        temp_range = self.TEMPERATURES[spectral_type]
        estimated_temp = (temp_range[0] + temp_range[1]) / 2
        
        return {
            'spectral_type': spectral_type,
            'confidence': self._calculate_color_confidence(u_g, g_r, spectral_type),
            'estimated_temperature': estimated_temp,
            'temperature_range': temp_range,
            'color_indices': {
                'u-g': round(u_g, 3),
                'g-r': round(g_r, 3),
                'r-i': round(r_i, 3)
            }
        }
    
    def classify_by_spectrum(self,
                            wavelength: np.ndarray,
                            flux: np.ndarray,
                            resolution: Optional[float] = None) -> Dict:
        """
        使用光谱数据进行详细分类
        
        Args:
            wavelength: 波长数组（埃）
            flux: 流量数组
            resolution: 光谱分辨率 R=λ/Δλ
            
        Returns:
            详细分类结果
        """
        # 预处理
        flux_processed = self._preprocess_spectrum(wavelength, flux)
        
        # 提取光谱特征
        features = self._extract_features(wavelength, flux_processed)
        
        # 基于特征分类
        spectral_type, sub_type = self._classify_from_features(features)
        
        # 计算物理参数
        physical_params = self._estimate_physical_parameters(
            spectral_type, features
        )
        
        return {
            'spectral_type': spectral_type,
            'sub_type': sub_type,
            'full_type': f"{spectral_type}{sub_type}",
            'confidence': features['classification_confidence'],
            'features': features,
            'physical_parameters': physical_params
        }
    
    def _preprocess_spectrum(self,
                            wavelength: np.ndarray,
                            flux: np.ndarray) -> np.ndarray:
        """预处理光谱"""
        # 归一化
        flux_norm = flux / np.median(flux)
        
        # 平滑（使用Savitzky-Golay滤波器）
        window = min(51, len(flux) // 10 * 2 + 1)
        if window >= 5:
            flux_smooth = savgol_filter(flux_norm, window, 3)
        else:
            flux_smooth = flux_norm
        
        return flux_smooth
    
    def _extract_features(self,
                         wavelength: np.ndarray,
                         flux: np.ndarray) -> Dict:
        """提取光谱特征"""
        features = {}
        
        # 1. Balmer线强度 (Hα, Hβ, Hγ, Hδ)
        balmer_lines = {
            'H_alpha': 6563,
            'H_beta': 4861,
            'H_gamma': 4340,
            'H_delta': 4102
        }
        
        balmer_strengths = {}
        for name, wave in balmer_lines.items():
            strength = self._measure_line_strength(wavelength, flux, wave, width=20)
            balmer_strengths[name] = strength
        
        features['balmer_strengths'] = balmer_strengths
        features['balmer_decrement'] = balmer_strengths.get('H_alpha', 0) / max(balmer_strengths.get('H_beta', 1e-10), 1e-10)
        
        # 2. Ca II H&K 线 (3968, 3933 Å)
        ca_hk_strength = (self._measure_line_strength(wavelength, flux, 3933, width=15) +
                         self._measure_line_strength(wavelength, flux, 3968, width=15)) / 2
        features['ca_hk_strength'] = ca_hk_strength
        
        # 3. Na I D 线 (5890, 5896 Å)
        na_d_strength = self._measure_line_strength(wavelength, flux, 5893, width=20)
        features['na_d_strength'] = na_d_strength
        
        # 4. CH G带 (4300 Å)
        ch_g_strength = self._measure_line_strength(wavelength, flux, 4300, width=30)
        features['ch_g_strength'] = ch_g_strength
        
        # 5. TiO带强度 (M型星特征)
        tio_strength = self._measure_band_strength(wavelength, flux, 7050, 7120)
        features['tio_strength'] = tio_strength
        
        # 6. 连续谱形状（颜色）
        blue_flux = self._get_mean_flux(wavelength, flux, 4000, 4500)
        green_flux = self._get_mean_flux(wavelength, flux, 5000, 5500)
        red_flux = self._get_mean_flux(wavelength, flux, 6000, 6500)
        
        features['color_bv'] = -2.5 * np.log10(blue_flux / max(green_flux, 1e-10))
        features['color_vr'] = -2.5 * np.log10(green_flux / max(red_flux, 1e-10))
        
        return features
    
    def _measure_line_strength(self,
                              wavelength: np.ndarray,
                              flux: np.ndarray,
                              line_center: float,
                              width: float = 20) -> float:
        """测量谱线强度"""
        # 找到谱线附近的数据点
        mask = np.abs(wavelength - line_center) < width
        if np.sum(mask) < 3:
            return 0.0
        
        # 计算线心深度（相对于局部连续谱）
        line_flux = np.min(flux[mask])
        
        # 估算连续谱
        continuum_mask = (np.abs(wavelength - (line_center - width*2)) < width/2) | \
                        (np.abs(wavelength - (line_center + width*2)) < width/2)
        
        if np.sum(continuum_mask) > 0:
            continuum = np.median(flux[continuum_mask])
        else:
            continuum = 1.0
        
        depth = continuum - line_flux
        return depth
    
    def _measure_band_strength(self,
                              wavelength: np.ndarray,
                              flux: np.ndarray,
                              band_start: float,
                              band_end: float) -> float:
        """测量分子带强度"""
        band_mask = (wavelength >= band_start) & (wavelength <= band_end)
        if np.sum(band_mask) < 2:
            return 0.0
        
        return np.mean(1 - flux[band_mask])
    
    def _get_mean_flux(self,
                      wavelength: np.ndarray,
                      flux: np.ndarray,
                      wave_min: float,
                      wave_max: float) -> float:
        """获取某一波段的平均流量"""
        mask = (wavelength >= wave_min) & (wavelength <= wave_max)
        if np.sum(mask) > 0:
            return np.mean(flux[mask])
        return 1.0
    
    def _classify_from_features(self, features: Dict) -> Tuple[str, int]:
        """基于特征分类"""
        balmer = features['balmer_strengths']
        
        # 分类决策树
        if balmer['H_gamma'] > 0.3 and features.get('color_bv', 0) < -0.2:
            # 早期型（O-B），强Balmer线，蓝色
            spectral_type = 'B'
            sub_type = int((1 - balmer['H_gamma']) * 9)
        elif balmer['H_gamma'] > 0.2 and features.get('color_bv', 0) < 0.2:
            # A型，强Balmer线，白色
            spectral_type = 'A'
            sub_type = int((0.4 - balmer['H_gamma']) * 20)
        elif features['ca_hk_strength'] > 0.1 and features.get('color_bv', 0) < 0.6:
            # F-G型，Ca II出现，黄白色
            if features['ch_g_strength'] > 0.05:
                spectral_type = 'G'
                sub_type = int((0.6 - features.get('color_bv', 0)) * 10)
            else:
                spectral_type = 'F'
                sub_type = int((0.4 - features.get('color_bv', 0)) * 10)
        elif features['ca_hk_strength'] > 0.15:
            # K型，强Ca II，橙色
            spectral_type = 'K'
            sub_type = int(features['ca_hk_strength'] * 20)
        else:
            # M型，TiO带，红色
            spectral_type = 'M'
            sub_type = int(features.get('tio_strength', 0) * 50)
        
        sub_type = max(0, min(9, sub_type))
        
        # 计算置信度
        confidence = self._calculate_classification_confidence(features, spectral_type)
        features['classification_confidence'] = confidence
        
        return spectral_type, sub_type
    
    def _calculate_classification_confidence(self,
                                            features: Dict,
                                            spectral_type: str) -> float:
        """计算分类置信度"""
        # 简化的置信度计算
        balmer = features['balmer_strengths']
        
        if spectral_type in ['O', 'B']:
            return min(0.95, 0.5 + balmer['H_gamma'])
        elif spectral_type == 'A':
            return min(0.95, 0.6 + balmer['H_gamma'] * 0.5)
        elif spectral_type in ['F', 'G']:
            return min(0.95, 0.5 + features['ca_hk_strength'])
        elif spectral_type == 'K':
            return min(0.95, 0.5 + features['ca_hk_strength'] * 0.8)
        else:  # M
            return min(0.95, 0.4 + features.get('tio_strength', 0) * 2)
    
    def _estimate_physical_parameters(self,
                                     spectral_type: str,
                                     features: Dict) -> Dict:
        """估算恒星物理参数"""
        temp_range = self.TEMPERATURES[spectral_type]
        temperature = (temp_range[0] + temp_range[1]) / 2
        
        # 粗略的质量-光度关系
        mass_sun = self._estimate_mass(spectral_type)
        luminosity_sun = self._estimate_luminosity(temperature, mass_sun)
        
        # 估算半径（Stefan-Boltzmann定律）
        radius_sun = np.sqrt(luminosity_sun) * (5778 / temperature)**2
        
        return {
            'effective_temperature_k': int(temperature),
            'temperature_range_k': temp_range,
            'mass_solar': round(mass_sun, 2),
            'radius_solar': round(radius_sun, 2),
            'luminosity_solar': round(luminosity_sun, 3),
            'stellar_class': self._get_stellar_class(spectral_type, temperature)
        }
    
    def _estimate_mass(self, spectral_type: str) -> float:
        """根据光谱型估算质量"""
        masses = {'O': 20, 'B': 8, 'A': 2.5, 'F': 1.4, 'G': 1.0, 'K': 0.7, 'M': 0.3}
        return masses.get(spectral_type, 1.0)
    
    def _estimate_luminosity(self, temperature: float, mass: float) -> float:
        """估算光度"""
        # 简化公式: L ~ M^3.5 (主序星)
        return mass**3.5
    
    def _get_stellar_class(self, spectral_type: str, temperature: float) -> str:
        """获取恒星分类描述"""
        classes = {
            'O': '大质量蓝巨星',
            'B': '蓝白色主序星',
            'A': '白色主序星',
            'F': '黄白色主序星',
            'G': '黄色主序星 (如太阳)',
            'K': '橙色主序星',
            'M': '红矮星'
        }
        return classes.get(spectral_type, '未知')
    
    def _calculate_color_confidence(self,
                                   u_g: float,
                                   g_r: float,
                                   spectral_type: str) -> float:
        """计算颜色分类的置信度"""
        # 简化的置信度
        return 0.75


def generate_mock_spectrum(spectral_type: str = 'G',
                          sub_type: int = 2,
                          snr: float = 100) -> Tuple[np.ndarray, np.ndarray]:
    """
    生成模拟恒星光谱（用于测试）
    
    Args:
        spectral_type: 光谱型
        sub_type: 次型 (0-9)
        snr: 信噪比
        
    Returns:
        (wavelength, flux) 数组
    """
    # 波长范围 (Å)
    wavelength = np.linspace(3800, 9000, 5200)
    
    # 黑体连续谱
    temperatures = {'O': 40000, 'B': 20000, 'A': 8500, 'F': 6500, 
                   'G': 5778, 'K': 4500, 'M': 3200}
    temp = temperatures.get(spectral_type, 5778)
    
    # 简化黑体谱
    h = 6.626e-34
    c = 3e8
    k = 1.381e-23
    wave_m = wavelength * 1e-10
    
    flux = (2 * h * c**2 / wave_m**5) / (np.exp(h * c / (wave_m * k * temp)) - 1)
    flux = flux / np.max(flux)  # 归一化
    
    # 添加Balmer线
    balmer_lines = [4102, 4340, 4861, 6563]
    for line in balmer_lines:
        if spectral_type in ['A', 'F']:
            depth = 0.3 - sub_type * 0.02  # A型强，F型减弱
        elif spectral_type in ['B']:
            depth = 0.15
        elif spectral_type in ['G', 'K', 'M']:
            depth = 0.05
        else:
            depth = 0.02
        
        depth = max(0, depth)
        
        # 添加吸收线
        mask = np.abs(wavelength - line) < 10
        flux[mask] *= (1 - depth * np.exp(-((wavelength[mask] - line) / 3)**2))
    
    # 添加噪声
    noise = np.random.normal(0, 1/snr, len(flux))
    flux += noise
    
    return wavelength, flux


if __name__ == "__main__":
    print("=" * 60)
    print("⭐ AstroAI-Core - 恒星光谱分类系统")
    print("=" * 60)
    
    classifier = SpectralClassifier()
    
    # 测试1: 使用颜色指数分类
    print("\n📊 测试1: 使用颜色指数分类")
    print("-" * 60)
    
    test_stars = [
        ('太阳 (G2V)', 15.0, 13.5, 12.8, 12.3),      # 黄色
        ('天狼星 (A1V)', 11.0, 10.0, 9.5, 9.2),      # 白色
        ('参宿七 (B8Ia)', 8.5, 7.8, 7.5, 7.3),       # 蓝白色
        ('参宿四 (M1Ia)', 18.0, 15.0, 12.5, 11.0),   # 红色
    ]
    
    for name, u, g, r, i in test_stars:
        result = classifier.classify_by_color_indices(u, g, r, i)
        print(f"\n   {name}:")
        print(f"      光谱型: {result['spectral_type']}")
        print(f"      估计温度: {result['estimated_temperature']:,} K")
        print(f"      颜色指数 u-g: {result['color_indices']['u-g']:.2f}")
    
    # 测试2: 使用光谱数据分类
    print("\n\n📈 测试2: 使用光谱数据分类")
    print("-" * 60)
    
    for spec_type in ['A', 'F', 'G', 'K']:
        print(f"\n   生成 {spec_type} 型模拟光谱...")
        wavelength, flux = generate_mock_spectrum(spec_type, sub_type=2)
        
        result = classifier.classify_by_spectrum(wavelength, flux)
        
        print(f"      预测光谱型: {result['full_type']}")
        print(f"      置信度: {result['confidence']*100:.1f}%")
        print(f"      有效温度: {result['physical_parameters']['effective_temperature_k']:,} K")
        print(f"      质量: {result['physical_parameters']['mass_solar']} M☉")
        print(f"      半径: {result['physical_parameters']['radius_solar']} R☉")
    
    print("\n" + "=" * 60)
    print("✅ 光谱分类系统测试完成！")
    print("=" * 60)
