"""
ExoPlanetNet - Exoplanet Transit Detection Model

1D-CNN + LSTM architecture for analyzing light curve data
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ExoPlanetNet(nn.Module):
    """
    Exoplanet detection neural network.
    
    Architecture:
    - 1D CNN layers for local feature extraction
    - Bidirectional LSTM for temporal dependencies
    - Attention mechanism for important time points
    - Classification head for planet/non-planet
    """
    
    def __init__(
        self,
        input_size: int = 1,
        conv_channels: list = [64, 128, 256],
        hidden_size: int = 256,
        num_layers: int = 2,
        dropout: float = 0.3,
        num_classes: int = 2
    ):
        super().__init__()
        
        # 1D CNN blocks
        self.conv_blocks = nn.ModuleList()
        in_channels = input_size
        for out_channels in conv_channels:
            self.conv_blocks.append(
                nn.Sequential(
                    nn.Conv1d(in_channels, out_channels, kernel_size=7, padding=3),
                    nn.BatchNorm1d(out_channels),
                    nn.ReLU(),
                    nn.Conv1d(out_channels, out_channels, kernel_size=5, padding=2),
                    nn.BatchNorm1d(out_channels),
                    nn.ReLU(),
                    nn.MaxPool1d(kernel_size=2)
                )
            )
            in_channels = out_channels
        
        # LSTM
        self.lstm = nn.LSTM(
            input_size=conv_channels[-1],
            hidden_size=hidden_size,
            num_layers=num_layers,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Attention
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size * 2,
            num_heads=8,
            dropout=dropout
        )
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Input tensor of shape [batch, seq_len, 1]
        
        Returns:
            Logits of shape [batch, num_classes]
        """
        # x: [batch, seq_len, 1]
        x = x.transpose(1, 2)  # [batch, 1, seq_len]
        
        # CNN blocks
        for conv_block in self.conv_blocks:
            x = conv_block(x)  # [batch, channels, seq_len]
        
        # Prepare for LSTM: [batch, seq_len, channels]
        x = x.transpose(1, 2)
        
        # LSTM
        x, _ = self.lstm(x)  # [batch, seq_len, hidden*2]
        
        # Attention (transpose for multihead attention)
        x = x.transpose(0, 1)  # [seq_len, batch, hidden*2]
        x, _ = self.attention(x, x, x)
        x = x.mean(dim=0)  # [batch, hidden*2]
        
        # Classification
        logits = self.classifier(x)
        
        return logits
    
    def predict_proba(self, x):
        """Get prediction probabilities"""
        logits = self.forward(x)
        return F.softmax(logits, dim=-1)
    
    def predict(self, x, threshold: float = 0.5):
        """Get binary predictions"""
        proba = self.predict_proba(x)
        return (proba[:, 1] > threshold).int()


def create_model(pretrained: bool = False, **kwargs) -> ExoPlanetNet:
    """Create ExoPlanetNet model"""
    model = ExoPlanetNet(**kwargs)
    
    if pretrained:
        # TODO: Load pretrained weights
        pass
    
    return model


if __name__ == "__main__":
    # Test model
    model = create_model()
    x = torch.randn(32, 1024, 1)  # batch=32, seq_len=1024
    output = model(x)
    print(f"Input shape: {x.shape}")
    print(f"Output shape: {output.shape}")
