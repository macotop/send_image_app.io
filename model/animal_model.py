from . import animal

import torch
import torch.nn as nn
import pytorch_lightning as pl
import torchvision
from torchvision.models import resnet18

# ネットワークの構築
class Net(pl.LightningModule):
    def __init__(self):
        super().__init__()

        self.feature = resnet18(pretrained=True)
        self.fc = nn.Linear(1000, 4)

    def forward(self, x):
        h = self.feature(x)
        h = self.fc(h)
        return h

# インスタンス化
net = Net().eval()

# 重みの読み込み
net.load_state_dict(torch.load('animal.pt'))