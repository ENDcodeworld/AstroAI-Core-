# ML Models

PyTorch models for astronomical data analysis.

## Models

- **ExoPlanetNet**: Exoplanet transit detection from light curves
- **StarClassifier**: Stellar classification (OBAFGKM)
- **AnomalyDetector**: Unsupervised anomaly detection
- **GalaxyMorphNet**: Galaxy morphology classification

## Training

```bash
# Train ExoPlanetNet
python train_exoplanet.py --data data/tess --epochs 50 --batch-size 64

# Train StarClassifier
python train_classifier.py --data data/sdss --model resnet50
```

## Inference

```python
from models.exoplanet import ExoPlanetNet

model = ExoPlanetNet.load_from_checkpoint("checkpoints/exoplanet.ckpt")
prediction = model.predict(lightcurve_data)
```
