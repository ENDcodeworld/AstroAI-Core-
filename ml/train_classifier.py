"""
模型训练管道

功能:
- 训练循环
- 验证和测试
- 模型保存和加载
- 训练日志和可视化
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingLR
import numpy as np
from tqdm import tqdm

# 导入本地模块
from models.star_classifier import StarClassifier, create_model
from data_loader import create_data_loaders, get_transforms


class TrainingConfig:
    """训练配置"""
    
    def __init__(
        self,
        # 数据配置
        data_dir: str = './data',
        batch_size: int = 32,
        img_size: int = 224,
        num_workers: int = 4,
        
        # 模型配置
        model_type: str = 'resnet',
        num_main_classes: int = 3,
        num_sub_classes: int = 10,
        pretrained: bool = True,
        
        # 训练配置
        epochs: int = 50,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        momentum: float = 0.9,
        
        # 优化器配置
        optimizer: str = 'adamw',
        scheduler: str = 'cosine',
        
        # 正则化
        dropout_rate: float = 0.3,
        label_smoothing: float = 0.1,
        
        # 设备配置
        device: str = 'cuda',
        mixed_precision: bool = True,
        
        # 日志配置
        log_dir: str = './logs',
        checkpoint_dir: str = './checkpoints',
        save_every: int = 5,
        
        # 早停配置
        early_stopping: bool = True,
        patience: int = 10,
        min_delta: float = 0.001
    ):
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.img_size = img_size
        self.num_workers = num_workers
        
        self.model_type = model_type
        self.num_main_classes = num_main_classes
        self.num_sub_classes = num_sub_classes
        self.pretrained = pretrained
        
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.momentum = momentum
        
        self.optimizer = optimizer
        self.scheduler = scheduler
        
        self.dropout_rate = dropout_rate
        self.label_smoothing = label_smoothing
        
        self.device = device
        self.mixed_precision = mixed_precision
        
        self.log_dir = log_dir
        self.checkpoint_dir = checkpoint_dir
        self.save_every = save_every
        
        self.early_stopping = early_stopping
        self.patience = patience
        self.min_delta = min_delta
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return self.__dict__.copy()
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'TrainingConfig':
        """从字典创建"""
        return cls(**config_dict)
    
    def save(self, path: str):
        """保存配置"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'TrainingConfig':
        """加载配置"""
        with open(path, 'r') as f:
            return cls.from_dict(json.load(f))


class Trainer:
    """
    模型训练器
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        
        # 设置设备
        if config.device == 'cuda' and not torch.cuda.is_available():
            print("Warning: CUDA not available, using CPU")
            self.device = torch.device('cpu')
        else:
            self.device = torch.device(config.device)
        
        print(f"Using device: {self.device}")
        
        # 创建目录
        Path(config.log_dir).mkdir(parents=True, exist_ok=True)
        Path(config.checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化模型
        self.model = create_model(
            model_type=config.model_type,
            num_main_classes=config.num_main_classes,
            num_sub_classes=config.num_sub_classes,
            pretrained=config.pretrained,
            dropout_rate=config.dropout_rate
        ).to(self.device)
        
        # 初始化优化器
        self.optimizer = self._create_optimizer()
        
        # 初始化学习率调度器
        self.scheduler = self._create_scheduler()
        
        # 损失函数
        self.main_criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)
        self.sub_criterion = nn.CrossEntropyLoss(label_smoothing=config.label_smoothing)
        
        # 训练历史
        self.history = {
            'train_loss': [],
            'train_main_acc': [],
            'train_sub_acc': [],
            'val_loss': [],
            'val_main_acc': [],
            'val_sub_acc': [],
            'learning_rates': []
        }
        
        # 早停
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        
        # 混合精度训练
        self.scaler = torch.cuda.amp.GradScaler() if config.mixed_precision and self.device.type == 'cuda' else None
    
    def _create_optimizer(self):
        """创建优化器"""
        params = self.model.parameters()
        
        if self.config.optimizer.lower() == 'adam':
            return optim.Adam(params, lr=self.config.learning_rate, weight_decay=self.config.weight_decay)
        elif self.config.optimizer.lower() == 'adamw':
            return optim.AdamW(params, lr=self.config.learning_rate, weight_decay=self.config.weight_decay)
        elif self.config.optimizer.lower() == 'sgd':
            return optim.SGD(params, lr=self.config.learning_rate, momentum=self.config.momentum, 
                           weight_decay=self.config.weight_decay)
        else:
            raise ValueError(f"Unknown optimizer: {self.config.optimizer}")
    
    def _create_scheduler(self):
        """创建学习率调度器"""
        if self.config.scheduler.lower() == 'cosine':
            return CosineAnnealingLR(self.optimizer, T_max=self.config.epochs, eta_min=1e-6)
        elif self.config.scheduler.lower() == 'plateau':
            return ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=5, verbose=True)
        else:
            return None
    
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        """
        训练一个 epoch
        
        Returns:
            训练指标字典
        """
        self.model.train()
        
        total_loss = 0.0
        main_correct = 0
        sub_correct = 0
        total_samples = 0
        
        pbar = tqdm(train_loader, desc='Training')
        
        for batch_idx, batch in enumerate(pbar):
            images = batch['image'].to(self.device)
            main_labels = batch['main_label'].to(self.device)
            sub_labels = batch['sub_label'].to(self.device)
            
            # 混合精度训练
            if self.scaler:
                with torch.cuda.amp.autocast():
                    outputs = self.model(images)
                    
                    main_loss = self.main_criterion(outputs['main_logits'], main_labels)
                    sub_loss = self.sub_criterion(outputs['sub_logits'], sub_labels)
                    loss = main_loss + sub_loss
                
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(images)
                
                main_loss = self.main_criterion(outputs['main_logits'], main_labels)
                sub_loss = self.sub_criterion(outputs['sub_logits'], sub_labels)
                loss = main_loss + sub_loss
                
                loss.backward()
                self.optimizer.step()
            
            self.optimizer.zero_grad()
            
            # 统计
            total_loss += loss.item() * images.size(0)
            
            main_preds = torch.argmax(outputs['main_logits'], dim=1)
            sub_preds = torch.argmax(outputs['sub_logits'], dim=1)
            
            main_correct += (main_preds == main_labels).sum().item()
            sub_correct += (sub_preds == sub_labels).sum().item()
            total_samples += images.size(0)
            
            # 更新进度条
            pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'main_acc': f'{main_correct/total_samples:.4f}',
                'sub_acc': f'{sub_correct/total_samples:.4f}'
            })
        
        return {
            'loss': total_loss / total_samples,
            'main_accuracy': main_correct / total_samples,
            'sub_accuracy': sub_correct / total_samples
        }
    
    @torch.no_grad()
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """
        验证
        
        Returns:
            验证指标字典
        """
        self.model.eval()
        
        total_loss = 0.0
        main_correct = 0
        sub_correct = 0
        total_samples = 0
        
        pbar = tqdm(val_loader, desc='Validating')
        
        for batch in pbar:
            images = batch['image'].to(self.device)
            main_labels = batch['main_label'].to(self.device)
            sub_labels = batch['sub_label'].to(self.device)
            
            outputs = self.model(images)
            
            main_loss = self.main_criterion(outputs['main_logits'], main_labels)
            sub_loss = self.sub_criterion(outputs['sub_logits'], sub_labels)
            loss = main_loss + sub_loss
            
            total_loss += loss.item() * images.size(0)
            
            main_preds = torch.argmax(outputs['main_logits'], dim=1)
            sub_preds = torch.argmax(outputs['sub_logits'], dim=1)
            
            main_correct += (main_preds == main_labels).sum().item()
            sub_correct += (sub_preds == sub_labels).sum().item()
            total_samples += images.size(0)
        
        return {
            'loss': total_loss / total_samples,
            'main_accuracy': main_correct / total_samples,
            'sub_accuracy': sub_correct / total_samples
        }
    
    def train(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict:
        """
        完整训练流程
        
        Args:
            train_loader: 训练数据加载器
            val_loader: 验证数据加载器
            
        Returns:
            训练历史
        """
        print(f"\nStarting training for {self.config.epochs} epochs...")
        print(f"Training samples: {len(train_loader.dataset)}")
        print(f"Validation samples: {len(val_loader.dataset)}")
        
        start_time = time.time()
        
        for epoch in range(self.config.epochs):
            print(f"\n{'='*50}")
            print(f"Epoch {epoch + 1}/{self.config.epochs}")
            print(f"{'='*50}")
            
            # 训练
            train_metrics = self.train_epoch(train_loader)
            
            # 验证
            val_metrics = self.validate(val_loader)
            
            # 更新学习率
            if self.scheduler:
                if isinstance(self.scheduler, ReduceLROnPlateau):
                    self.scheduler.step(val_metrics['loss'])
                else:
                    self.scheduler.step()
            
            # 记录历史
            self.history['train_loss'].append(train_metrics['loss'])
            self.history['train_main_acc'].append(train_metrics['main_accuracy'])
            self.history['train_sub_acc'].append(train_metrics['sub_accuracy'])
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_main_acc'].append(val_metrics['main_accuracy'])
            self.history['val_sub_acc'].append(val_metrics['sub_accuracy'])
            self.history['learning_rates'].append(self.optimizer.param_groups[0]['lr'])
            
            # 打印结果
            print(f"\nTrain Loss: {train_metrics['loss']:.4f}")
            print(f"Train Main Acc: {train_metrics['main_accuracy']:.4f}")
            print(f"Train Sub Acc: {train_metrics['sub_accuracy']:.4f}")
            print(f"Val Loss: {val_metrics['loss']:.4f}")
            print(f"Val Main Acc: {val_metrics['main_accuracy']:.4f}")
            print(f"Val Sub Acc: {val_metrics['sub_accuracy']:.4f}")
            print(f"Learning Rate: {self.optimizer.param_groups[0]['lr']:.6f}")
            
            # 保存检查点
            if (epoch + 1) % self.config.save_every == 0:
                self.save_checkpoint(epoch, val_metrics)
            
            # 早停检查
            if self.config.early_stopping:
                if val_metrics['loss'] < self.best_val_loss - self.config.min_delta:
                    self.best_val_loss = val_metrics['loss']
                    self.patience_counter = 0
                    # 保存最佳模型
                    self.save_checkpoint(epoch, val_metrics, name='best_model.pth')
                else:
                    self.patience_counter += 1
                    if self.patience_counter >= self.config.patience:
                        print(f"\nEarly stopping triggered at epoch {epoch + 1}")
                        break
        
        total_time = time.time() - start_time
        print(f"\nTraining completed in {total_time/3600:.2f} hours")
        
        # 保存最终模型
        self.save_checkpoint(self.config.epochs - 1, val_metrics, name='final_model.pth')
        
        # 保存训练历史
        self.save_history()
        
        return self.history
    
    def save_checkpoint(self, epoch: int, metrics: Dict, name: Optional[str] = None):
        """保存检查点"""
        if name is None:
            name = f'checkpoint_epoch_{epoch+1}.pth'
        
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics': metrics,
            'config': self.config.to_dict(),
            'history': self.history
        }
        
        if self.scheduler:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        if self.scaler:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()
        
        path = Path(self.config.checkpoint_dir) / name
        torch.save(checkpoint, path)
        print(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str):
        """加载检查点"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        if 'scheduler_state_dict' in checkpoint and self.scheduler:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        if 'scaler_state_dict' in checkpoint and self.scaler:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
        
        print(f"Checkpoint loaded from {path}")
        return checkpoint
    
    def save_history(self):
        """保存训练历史"""
        path = Path(self.config.log_dir) / 'training_history.json'
        with open(path, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"Training history saved to {path}")
    
    def plot_history(self, save_path: Optional[str] = None):
        """绘制训练历史"""
        try:
            import matplotlib.pyplot as plt
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # Loss
            axes[0, 0].plot(self.history['train_loss'], label='Train Loss')
            axes[0, 0].plot(self.history['val_loss'], label='Val Loss')
            axes[0, 0].set_xlabel('Epoch')
            axes[0, 0].set_ylabel('Loss')
            axes[0, 0].legend()
            axes[0, 0].set_title('Loss')
            
            # Main Accuracy
            axes[0, 1].plot(self.history['train_main_acc'], label='Train Main Acc')
            axes[0, 1].plot(self.history['val_main_acc'], label='Val Main Acc')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('Accuracy')
            axes[0, 1].legend()
            axes[0, 1].set_title('Main Category Accuracy')
            
            # Sub Accuracy
            axes[1, 0].plot(self.history['train_sub_acc'], label='Train Sub Acc')
            axes[1, 0].plot(self.history['val_sub_acc'], label='Val Sub Acc')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('Accuracy')
            axes[1, 0].legend()
            axes[1, 0].set_title('Sub Category Accuracy')
            
            # Learning Rate
            axes[1, 1].plot(self.history['learning_rates'])
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Learning Rate')
            axes[1, 1].set_title('Learning Rate')
            axes[1, 1].set_yscale('log')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150)
                print(f"Training curves saved to {save_path}")
            else:
                plt.show()
                
        except ImportError:
            print("Matplotlib not available, skipping plot")


def main():
    """主训练函数"""
    # 创建配置
    config = TrainingConfig(
        data_dir='./data/celestial',
        batch_size=32,
        epochs=50,
        learning_rate=1e-3,
        model_type='resnet'
    )
    
    # 创建训练器
    trainer = Trainer(config)
    
    # 创建数据加载器
    train_loader, val_loader, test_loader = create_data_loaders(
        data_dir=config.data_dir,
        batch_size=config.batch_size,
        img_size=config.img_size
    )
    
    # 开始训练
    history = trainer.train(train_loader, val_loader)
    
    # 在测试集上评估
    print("\nEvaluating on test set...")
    test_metrics = trainer.validate(test_loader)
    print(f"Test Loss: {test_metrics['loss']:.4f}")
    print(f"Test Main Acc: {test_metrics['main_accuracy']:.4f}")
    print(f"Test Sub Acc: {test_metrics['sub_accuracy']:.4f}")
    
    # 绘制训练曲线
    trainer.plot_history(save_path='./logs/training_curves.png')
    
    print("\nTraining completed successfully!")


if __name__ == '__main__':
    main()
