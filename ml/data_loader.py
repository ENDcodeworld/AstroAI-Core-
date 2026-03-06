"""
数据加载器 - 天文图像数据集处理

功能:
- 加载 Hubble 公开图像数据集
- 数据增强（旋转、翻转、缩放）
- 创建训练/验证/测试集
- 批量数据加载
"""

import os
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from collections import defaultdict

import torch
from torch.utils.data import Dataset, DataLoader, SubsetRandomSampler
from torchvision import transforms
from PIL import Image
import numpy as np


class CelestialDataset(Dataset):
    """
    天文图像数据集
    
    支持格式:
    - 目录结构：data/{category}/{image}.jpg
    - JSON 标注文件：annotations.json
    """
    
    def __init__(
        self,
        root_dir: str,
        transform: Optional[transforms.Compose] = None,
        annotation_file: Optional[str] = None,
        categories: Optional[List[str]] = None,
        return_path: bool = False
    ):
        """
        初始化数据集
        
        Args:
            root_dir: 数据根目录
            transform: 数据变换
            annotation_file: 标注文件路径 (可选)
            categories: 要加载的类别列表 (可选)
            return_path: 是否返回图像路径
        """
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.return_path = return_path
        
        # 类别映射
        self.categories = categories or [
            'star', 'galaxy', 'nebula',
            'elliptical_galaxy', 'spiral_galaxy', 'irregular_galaxy',
            'emission_nebula', 'reflection_nebula', 'planetary_nebula', 'dark_nebula'
        ]
        
        self.category_to_idx = {cat: idx for idx, cat in enumerate(self.categories)}
        self.idx_to_category = {idx: cat for cat, idx in self.category_to_idx.items()}
        
        # 加载数据
        self.samples = self._load_samples(annotation_file)
        
        print(f"Loaded {len(self.samples)} samples from {root_dir}")
    
    def _load_samples(self, annotation_file: Optional[str]) -> List[Dict]:
        """
        加载样本
        
        支持两种方式:
        1. 从 JSON 标注文件加载
        2. 从目录结构自动推断
        """
        samples = []
        
        if annotation_file and os.path.exists(annotation_file):
            # 从标注文件加载
            with open(annotation_file, 'r') as f:
                annotations = json.load(f)
            
            for ann in annotations:
                img_path = self.root_dir / ann['image_path']
                if img_path.exists():
                    samples.append({
                        'path': str(img_path),
                        'main_category': ann.get('main_category', 'unknown'),
                        'sub_category': ann.get('sub_category', 'unknown'),
                        'metadata': ann.get('metadata', {})
                    })
        else:
            # 从目录结构加载
            for category in self.categories:
                category_dir = self.root_dir / category
                if not category_dir.exists():
                    continue
                
                for img_file in category_dir.glob('*.[jp][pn][g]'):
                    samples.append({
                        'path': str(img_file),
                        'main_category': category,
                        'sub_category': category,
                        'metadata': {}
                    })
        
        return samples
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Dict[str, any]:
        sample = self.samples[idx]
        
        # 加载图像
        image = Image.open(sample['path']).convert('RGB')
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        # 获取标签
        main_label = self.category_to_idx.get(sample['main_category'], 0)
        sub_label = self.category_to_idx.get(sample['sub_category'], 0)
        
        result = {
            'image': image,
            'main_label': main_label,
            'sub_label': sub_label,
            'main_category': sample['main_category'],
            'sub_category': sample['sub_category']
        }
        
        if self.return_path:
            result['path'] = sample['path']
        
        if sample.get('metadata'):
            result['metadata'] = sample['metadata']
        
        return result
    
    def get_class_weights(self) -> torch.Tensor:
        """计算类别权重用于处理不平衡数据"""
        class_counts = defaultdict(int)
        for sample in self.samples:
            class_counts[sample['main_category']] += 1
        
        total = len(self.samples)
        weights = []
        for idx in range(len(self.categories)):
            category = self.idx_to_category[idx]
            count = class_counts.get(category, 1)
            weights.append(total / (len(self.categories) * count))
        
        return torch.tensor(weights, dtype=torch.float32)


class HubbleDataset(CelestialDataset):
    """
    Hubble 太空望远镜图像数据集
    
    专门处理 Hubble 公开数据
    """
    
    def __init__(
        self,
        root_dir: str,
        transform: Optional[transforms.Compose] = None,
        split: str = 'train',
        min_resolution: int = 128
    ):
        self.split = split
        self.min_resolution = min_resolution
        
        super().__init__(root_dir, transform)
        
        # 过滤低分辨率图像
        self.samples = self._filter_by_resolution()
    
    def _filter_by_resolution(self) -> List[Dict]:
        """过滤低于最小分辨率的图像"""
        filtered = []
        for sample in self.samples:
            try:
                with Image.open(sample['path']) as img:
                    if min(img.size) >= self.min_resolution:
                        filtered.append(sample)
            except Exception as e:
                print(f"Warning: Could not open {sample['path']}: {e}")
        
        print(f"After resolution filtering: {len(filtered)} samples")
        return filtered


def get_transforms(
    img_size: int = 224,
    is_training: bool = True,
    normalize: bool = True,
    augment: bool = True
) -> transforms.Compose:
    """
    获取数据变换
    
    Args:
        img_size: 图像尺寸
        is_training: 是否训练模式
        normalize: 是否标准化
        augment: 是否数据增强
        
    Returns:
        变换组合
    """
    transform_list = []
    
    if is_training and augment:
        # 训练时的数据增强
        transform_list.extend([
            transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.5),
            transforms.RandomRotation(degrees=30),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        ])
    else:
        # 验证/测试时的变换
        transform_list.extend([
            transforms.Resize(img_size + 32),
            transforms.CenterCrop(img_size),
        ])
    
    transform_list.append(transforms.ToTensor())
    
    if normalize:
        transform_list.append(
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        )
    
    return transforms.Compose(transform_list)


def create_data_loaders(
    data_dir: str,
    batch_size: int = 32,
    img_size: int = 224,
    num_workers: int = 4,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    annotation_file: Optional[str] = None,
    categories: Optional[List[str]] = None
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    创建训练/验证/测试数据加载器
    
    Args:
        data_dir: 数据目录
        batch_size: 批次大小
        img_size: 图像尺寸
        num_workers: 数据加载线程数
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        annotation_file: 标注文件
        categories: 类别列表
        
    Returns:
        (train_loader, val_loader, test_loader)
    """
    # 创建完整数据集
    full_dataset = CelestialDataset(
        root_dir=data_dir,
        transform=None,  # 先不应用变换
        annotation_file=annotation_file,
        categories=categories
    )
    
    # 划分数据集
    n_samples = len(full_dataset)
    n_train = int(n_samples * train_ratio)
    n_val = int(n_samples * val_ratio)
    n_test = n_samples - n_train - n_val
    
    # 随机打乱索引
    indices = list(range(n_samples))
    random.shuffle(indices)
    
    train_indices = indices[:n_train]
    val_indices = indices[n_train:n_train + n_val]
    test_indices = indices[n_train + n_val:]
    
    # 创建变换
    train_transform = get_transforms(img_size, is_training=True, augment=True)
    val_transform = get_transforms(img_size, is_training=False, augment=False)
    test_transform = get_transforms(img_size, is_training=False, augment=False)
    
    # 创建子集
    train_dataset = SubsetDataset(full_dataset, train_indices, train_transform)
    val_dataset = SubsetDataset(full_dataset, val_indices, val_transform)
    test_dataset = SubsetDataset(full_dataset, test_indices, test_transform)
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    print(f"Data split: train={n_train}, val={n_val}, test={n_test}")
    
    return train_loader, val_loader, test_loader


class SubsetDataset(Dataset):
    """数据集子集包装器"""
    
    def __init__(self, dataset, indices, transform):
        self.dataset = dataset
        self.indices = indices
        self.transform = transform
    
    def __len__(self):
        return len(self.indices)
    
    def __getitem__(self, idx):
        sample = self.dataset[self.indices[idx]]
        if self.transform and 'image' in sample:
            sample['image'] = self.transform(sample['image'])
        return sample


class DataAugmenter:
    """
    数据增强工具类
    
    支持多种增强策略
    """
    
    @staticmethod
    def create_augmented_dataset(
        input_dir: str,
        output_dir: str,
        augmentation_factor: int = 5,
        img_size: int = 224
    ):
        """
        创建增强数据集
        
        Args:
            input_dir: 输入数据目录
            output_dir: 输出数据目录
            augmentation_factor: 增强倍数
            img_size: 输出图像尺寸
        """
        os.makedirs(output_dir, exist_ok=True)
        
        transform = transforms.Compose([
            transforms.RandomResizedCrop(img_size, scale=(0.8, 1.0)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(30),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # 遍历所有类别
        for category_dir in Path(input_dir).iterdir():
            if not category_dir.is_dir():
                continue
            
            output_category_dir = Path(output_dir) / category_dir.name
            output_category_dir.mkdir(parents=True, exist_ok=True)
            
            # 处理每张图像
            for img_file in category_dir.glob('*.[jp][pn][g]'):
                image = Image.open(img_file).convert('RGB')
                
                # 生成增强版本
                for i in range(augmentation_factor):
                    augmented = transform(image)
                    # 转回 PIL 保存
                    augmented_pil = transforms.ToPILImage()(augmented)
                    
                    output_path = output_category_dir / f"{img_file.stem}_aug{i}{img_file.suffix}"
                    augmented_pil.save(output_path)
                
                # 保存原始图像
                image.save(output_category_dir / img_file.name)
        
        print(f"Augmented dataset saved to {output_dir}")


if __name__ == '__main__':
    # 测试数据加载器
    print("Testing data loader...")
    
    # 创建测试数据
    test_dir = Path('/tmp/test_celestial_data')
    test_dir.mkdir(exist_ok=True)
    
    for category in ['star', 'galaxy', 'nebula']:
        cat_dir = test_dir / category
        cat_dir.mkdir(exist_ok=True)
        
        # 创建测试图像
        for i in range(10):
            img = Image.new('RGB', (256, 256), color=(random.randint(0, 255), 0, 0))
            img.save(cat_dir / f'test_{i}.jpg')
    
    # 测试数据加载
    dataset = CelestialDataset(str(test_dir))
    print(f"Dataset size: {len(dataset)}")
    
    # 测试数据加载器
    train_loader, val_loader, test_loader = create_data_loaders(
        str(test_dir),
        batch_size=4,
        train_ratio=0.6,
        val_ratio=0.2,
        test_ratio=0.2
    )
    
    print(f"Train batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")
    print(f"Test batches: {len(test_loader)}")
    
    # 测试一个批次
    batch = next(iter(train_loader))
    print(f"Batch image shape: {batch['image'].shape}")
    print(f"Batch labels: {batch['main_label']}")
