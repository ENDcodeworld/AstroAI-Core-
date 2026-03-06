"""
模型测试

包含:
- 模型架构测试
- 推理测试
- 数据加载测试
- API 端点测试
"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'ml'))
sys.path.insert(0, str(project_root))

import torch
import numpy as np
from PIL import Image


class TestStarClassifier(unittest.TestCase):
    """StarClassifier 模型测试"""
    
    def setUp(self):
        """测试前准备"""
        from ml.models.star_classifier import StarClassifier, create_model, CelestialCategory
        
        self.StarClassifier = StarClassifier
        self.create_model = create_model
        self.CelestialCategory = CelestialCategory
        
        # 创建测试模型
        self.model = create_model(
            model_type='resnet',
            num_main_classes=3,
            num_sub_classes=10,
            pretrained=False
        )
    
    def test_model_creation(self):
        """测试模型创建"""
        self.assertIsNotNone(self.model)
        self.assertEqual(self.model.num_main_classes, 3)
        self.assertEqual(self.model.num_sub_classes, 10)
    
    def test_forward_pass(self):
        """测试前向传播"""
        self.model.eval()
        
        # 创建 dummy 输入
        dummy_input = torch.randn(2, 3, 224, 224)
        
        with torch.no_grad():
            output = self.model(dummy_input)
        
        # 检查输出
        self.assertIn('main_logits', output)
        self.assertIn('sub_logits', output)
        self.assertIn('confidence', output)
        
        self.assertEqual(output['main_logits'].shape, (2, 3))
        self.assertEqual(output['sub_logits'].shape, (2, 10))
        self.assertEqual(output['confidence'].shape, (2, 1))
    
    def test_predict_method(self):
        """测试预测方法"""
        self.model.eval()
        
        dummy_input = torch.randn(1, 3, 224, 224)
        
        with torch.no_grad():
            result = self.model.predict(dummy_input)
        
        # 检查结果结构
        self.assertIn('main_category_id', result)
        self.assertIn('main_category_prob', result)
        self.assertIn('sub_category_id', result)
        self.assertIn('sub_category_prob', result)
        self.assertIn('overall_confidence', result)
        
        # 检查值范围
        self.assertGreaterEqual(result['main_category_prob'], 0)
        self.assertLessEqual(result['main_category_prob'], 1)
        self.assertGreaterEqual(result['overall_confidence'], 0)
        self.assertLessEqual(result['overall_confidence'], 1)
    
    def test_category_enum(self):
        """测试类别枚举"""
        main_cats = self.CelestialCategory.get_main_categories()
        self.assertEqual(len(main_cats), 3)
        self.assertIn('star', main_cats)
        self.assertIn('galaxy', main_cats)
        self.assertIn('nebula', main_cats)
        
        sub_cats = self.CelestialCategory.get_subcategories()
        self.assertGreater(len(sub_cats), 3)
    
    def test_vit_model(self):
        """测试 ViT 模型"""
        vit_model = create_model(
            model_type='vit',
            num_main_classes=3,
            num_sub_classes=10,
            pretrained=False
        )
        
        dummy_input = torch.randn(1, 3, 224, 224)
        
        with torch.no_grad():
            output = vit_model(dummy_input)
        
        self.assertIn('main_logits', output)
        self.assertEqual(output['main_logits'].shape, (1, 3))


class TestDataLoader(unittest.TestCase):
    """数据加载器测试"""
    
    def setUp(self):
        """创建测试数据"""
        from ml.data_loader import CelestialDataset, get_transforms, create_data_loaders
        
        self.CelestialDataset = CelestialDataset
        self.get_transforms = get_transforms
        self.create_data_loaders = create_data_loaders
        
        # 创建临时测试数据
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_data()
    
    def _create_test_data(self):
        """创建测试图像数据"""
        for category in ['star', 'galaxy', 'nebula']:
            cat_dir = Path(self.temp_dir) / category
            cat_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建测试图像
            for i in range(5):
                img = Image.new('RGB', (256, 256), color=(np.random.randint(0, 255), 0, 0))
                img.save(cat_dir / f'test_{i}.jpg')
    
    def tearDown(self):
        """清理临时数据"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_dataset_creation(self):
        """测试数据集创建"""
        dataset = self.CelestialDataset(root_dir=self.temp_dir)
        
        self.assertGreater(len(dataset), 0)
        self.assertEqual(len(dataset), 15)  # 3 categories * 5 images
    
    def test_dataset_getitem(self):
        """测试数据集样本获取"""
        dataset = self.CelestialDataset(root_dir=self.temp_dir)
        
        sample = dataset[0]
        
        self.assertIn('image', sample)
        self.assertIn('main_label', sample)
        self.assertIn('sub_label', sample)
    
    def test_transforms(self):
        """测试数据变换"""
        train_transform = self.get_transforms(img_size=224, is_training=True)
        val_transform = self.get_transforms(img_size=224, is_training=False)
        
        # 创建测试图像
        img = Image.new('RGB', (256, 256), color=(100, 100, 100))
        
        # 应用变换
        train_tensor = train_transform(img)
        val_tensor = val_transform(img)
        
        self.assertEqual(train_tensor.shape[0], 3)
        self.assertEqual(val_tensor.shape[0], 3)
    
    def test_data_loaders(self):
        """测试数据加载器"""
        train_loader, val_loader, test_loader = self.create_data_loaders(
            data_dir=self.temp_dir,
            batch_size=4,
            train_ratio=0.6,
            val_ratio=0.2,
            test_ratio=0.2
        )
        
        self.assertGreater(len(train_loader), 0)
        self.assertGreater(len(val_loader), 0)
        self.assertGreater(len(test_loader), 0)
        
        # 测试批次
        batch = next(iter(train_loader))
        self.assertIn('image', batch)
        self.assertIn('main_label', batch)
        self.assertEqual(batch['image'].shape[0], 4)  # batch size


class TestInferenceEngine(unittest.TestCase):
    """推理引擎测试"""
    
    def setUp(self):
        """准备测试模型"""
        from ml.inference import InferenceEngine
        from ml.models.star_classifier import create_model
        
        self.InferenceEngine = InferenceEngine
        
        # 创建临时模型
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = Path(self.temp_dir) / 'test_model.pth'
        
        # 保存测试模型
        model = create_model('resnet', num_main_classes=3, num_sub_classes=10, pretrained=False)
        torch.save({'model_state_dict': model.state_dict()}, self.model_path)
    
    def tearDown(self):
        """清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_engine_initialization(self):
        """测试引擎初始化"""
        engine = self.InferenceEngine(model_path=str(self.model_path))
        
        self.assertIsNotNone(engine.model)
        self.assertIsNotNone(engine.transform)
    
    def test_single_prediction(self):
        """测试单张图像预测"""
        engine = self.InferenceEngine(model_path=str(self.model_path))
        
        # 创建测试图像
        test_img = Image.new('RGB', (224, 224), color=(100, 100, 100))
        
        result = engine.predict(test_img)
        
        self.assertIn('main_predictions', result)
        self.assertIn('sub_predictions', result)
        self.assertIn('overall_confidence', result)
        self.assertIn('best_main_category', result)
        self.assertIn('best_sub_category', result)
    
    def test_batch_prediction(self):
        """测试批量预测"""
        engine = self.InferenceEngine(model_path=str(self.model_path))
        
        # 创建测试图像列表
        images = [Image.new('RGB', (224, 224), color=(i*50, 0, 0)) for i in range(5)]
        
        results = engine.predict_batch(images, batch_size=2)
        
        self.assertEqual(len(results), 5)
        self.assertIn('main_category', results[0])
        self.assertIn('sub_category', results[0])
    
    def test_base64_prediction(self):
        """测试 base64 预测"""
        import base64
        import io
        
        engine = self.InferenceEngine(model_path=str(self.model_path))
        
        # 创建测试图像并转为 base64
        img = Image.new('RGB', (224, 224), color=(100, 100, 100))
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        base64_str = base64.b64encode(buffer.getvalue()).decode()
        
        result = engine.predict_from_base64(base64_str)
        
        self.assertIn('main_predictions', result)


class TestAPIEndpoints(unittest.TestCase):
    """API 端点测试"""
    
    def setUp(self):
        """准备测试客户端"""
        try:
            from fastapi.testclient import TestClient
            from api.app.api.v1 import classify
            
            self.TestClient = TestClient
            self.classify_module = classify
            
            # 创建测试客户端
            self.app = classify.app if hasattr(classify, 'app') else None
            
        except ImportError:
            self.TestClient = None
            self.app = None
    
    @unittest.skipIf(TestClient is None, "FastAPI test client not available")
    def test_health_endpoint(self):
        """测试健康检查端点"""
        if not self.app:
            self.skipTest("App not available")
        
        client = self.TestClient(self.app)
        response = client.get("/health")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('inference_available', data)
    
    @unittest.skipIf(TestClient is None, "FastAPI test client not available")
    def test_categories_endpoint(self):
        """测试类别列表端点"""
        if not self.app:
            self.skipTest("App not available")
        
        client = self.TestClient(self.app)
        response = client.get("/categories")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('main_categories', data)
        self.assertIn('sub_categories', data)


class TestTrainingPipeline(unittest.TestCase):
    """训练管道测试"""
    
    def setUp(self):
        """准备"""
        from ml.train_classifier import TrainingConfig, Trainer
        
        self.TrainingConfig = TrainingConfig
        self.Trainer = Trainer
    
    def test_config_creation(self):
        """测试配置创建"""
        config = self.TrainingConfig(
            epochs=5,
            batch_size=16,
            learning_rate=0.001
        )
        
        self.assertEqual(config.epochs, 5)
        self.assertEqual(config.batch_size, 16)
        self.assertEqual(config.learning_rate, 0.001)
    
    def test_config_serialization(self):
        """测试配置序列化"""
        import tempfile
        
        config = self.TrainingConfig(epochs=10)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config.save(f.name)
            saved_config = self.TrainingConfig.load(f.name)
        
        self.assertEqual(saved_config.epochs, config.epochs)
    
    def test_trainer_initialization(self):
        """测试训练器初始化"""
        config = self.TrainingConfig(
            epochs=1,
            batch_size=8,
            pretrained=False
        )
        
        trainer = self.Trainer(config)
        
        self.assertIsNotNone(trainer.model)
        self.assertIsNotNone(trainer.optimizer)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestStarClassifier))
    suite.addTests(loader.loadTestsFromTestCase(TestDataLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestInferenceEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestTrainingPipeline))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 60)
    print("AstroAI-Core 测试套件")
    print("=" * 60)
    
    success = run_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 所有测试通过!")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
