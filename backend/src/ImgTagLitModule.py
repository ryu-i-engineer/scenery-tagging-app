import pytorch_lightning as pl
import torch.optim as optim
from torch import nn


class BeiTNet(nn.Module):
    def __init__(self, pretrained_beit_model, class_num):
        super(BeiTNet, self).__init__()
        self.beit = pretrained_beit_model
        self.fc = nn.Sequential(
            nn.LayerNorm(768, eps=1e-12),
            nn.Linear(768, 768),
            nn.Tanh(),
            nn.Dropout(p=0.0),
            nn.Linear(768, class_num),
        )

        # まず全パラメータを勾配計算Falseにする
        for param in self.parameters():
            param.requires_grad = False

        for param in self.beit.encoder.layer[-1].parameters():
            param.requires_grad = True

        # 追加したクラス分類用の全結合層を勾配計算ありに変更
        for param in self.fc.parameters():
            param.requires_grad = True

    def _get_cls_vec(self, states):
        return states["last_hidden_state"][:, 0, :]

    def forward(self, img):
        output = self.beit(img)
        output = self._get_cls_vec(output)
        output = self.fc(output).squeeze(1)
        return output


class ImgTagLitModule(pl.LightningModule):
    def __init__(self, net, class_num, lr=5e-4, pos_weight=None):
        super().__init__()
        # self.save_hyperparameters()

        self.lr = lr
        self.pos_weight = pos_weight
        self.net = BeiTNet(net, class_num)
        self.forward = self.net.forward

    def training_step(self, batch, batch_idx):
        img, labels = batch
        outputs = self.forward(img)

        loss = 0
        if labels is not None:
            loss = nn.functional.binary_cross_entropy_with_logits(
                outputs, labels, pos_weight=self.pos_weight
            )

        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        img, labels = batch
        outputs = self.forward(img)

        loss = 0
        if labels is not None:
            loss = nn.functional.binary_cross_entropy_with_logits(
                outputs, labels, pos_weight=self.pos_weight
            )

        self.log("val_loss", loss)
        return loss

    def test_step(self, batch, batch_idx):
        img, labels = batch
        outputs = self.forward(img)

        loss = 0
        if labels is not None:
            loss = nn.functional.binary_cross_entropy_with_logits(
                outputs, labels, pos_weight=self.pos_weight
            )

        self.log("test_loss", loss)
        return loss

    def configure_optimizers(self):
        optimizer = optim.Adam(
            [
                {"params": self.net.beit.encoder.layer[-1].parameters(), "lr": 1e-8},
                {"params": self.net.fc.parameters(), "lr": self.lr},
            ]
        )

        return optimizer
