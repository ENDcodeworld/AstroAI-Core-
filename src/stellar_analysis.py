"""恒星分析工具"""

import numpy as np

# 恒星光谱分类
SPECTRAL_CLASSES = {
    'O': {'temp': (30000, 50000), 'color': 'Blue', 'mass': (16, 150), 'example': 'Rigel'},
    'B': {'temp': (10000, 30000), 'color': 'Blue-White', 'mass': (2.1, 16), 'example': 'Spica'},
    'A': {'temp': (7500, 10000), 'color': 'White', 'mass': (1.4, 2.1), 'example': 'Sirius'},
    'F': {'temp': (6000, 7500), 'color': 'Yellow-White', 'mass': (1.04, 1.4), 'example': 'Procyon'},
    'G': {'temp': (5200, 6000), 'color': 'Yellow', 'mass': (0.8, 1.04), 'example': 'Sun'},
    'K': {'temp': (3700, 5200), 'color': 'Orange', 'mass': (0.45, 0.8), 'example': 'Arcturus'},
    'M': {'temp': (2400, 3700), 'color': 'Red', 'mass': (0.08, 0.45), 'example': 'Betelgeuse'},
}


def classify_star(temperature: float) -> dict:
    """根据表面温度分类恒星"""
    for cls, info in SPECTRAL_CLASSES.items():
        low, high = info['temp']
        if low <= temperature <= high:
            return {
                'class': cls,
                'temperature': temperature,
                'color': info['color'],
                'mass_range': info['mass'],
                'example': info['example']
            }
    return {'class': 'Unknown', 'temperature': temperature}


def luminosity(mass_solar: float) -> float:
    """质量-光度关系 (近似)"""
    if mass_solar < 0.43:
        return 0.23 * mass_solar ** 2.3
    elif mass_solar < 2:
        return mass_solar ** 4
    elif mass_solar < 55:
        return 1.4 * mass_solar ** 3.5
    else:
        return 32000 * mass_solar


def habitable_zone(L_solar: float) -> tuple:
    """计算宜居带 (AU)"""
    inner = sqrt(L_solar / 1.1)
    outer = sqrt(L_solar / 0.53)
    return (inner, outer)


from math import sqrt

if __name__ == "__main__":
    print("=" * 55)
    print("🔭 AstroAI-Core - Stellar Analysis Demo")
    print("=" * 55)
    
    # 恒星分类示例
    temperatures = [5778, 9940, 3600, 33000, 28000]
    
    print(f"\n{'分类':<6} {'温度(K)':<12} {'颜色':<15} {'代表恒星':<15}")
    print("-" * 55)
    for t in temperatures:
        star = classify_star(t)
        print(f"  {star['class']:<4} {t:<12,} {star['color']:<15} {star['example']:<15}")
    
    # 宜居带计算
    print(f"\n🌍 Habitable Zones:")
    for mass, name in [(1.0, "Sun"), (1.5, "F-type"), (0.5, "K-type"), (0.1, "M-type")]:
        L = luminosity(mass)
        inner, outer = habitable_zone(L)
        print(f"  {name} ({mass}M☉): {inner:.3f} - {outer:.3f} AU")
    
    print("\n✅ Stellar analysis complete!")
