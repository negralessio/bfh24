import torch
import torch.nn as nn
import numpy as np
import pytorch_lightning as pl


class PLModel(pl.LightningModule):

    def __init__(self, n_timesteps, n_features, n_target_steps):
        super().__init__()
        self.model = PredictorModel(n_timesteps, n_features, n_target_steps)
        self.loss_fn = nn.MSELoss()

    def predict_step(self, batch, batch_idx):
        input, target = batch
        y_pred = self.model(input)
        return y_pred

    def training_step(self, batch, batch_idx):
        input, target = batch
        y_pred = self.model(input)
        loss = self.loss_fn(target, y_pred)
        self.log(name="train_loss", value=loss, on_step=False, on_epoch=True)
        return loss

    def test_step(self, batch, batch_idx):
        input, target = batch
        y_pred = self.model(input)
        test_loss = self.loss_fn(target, y_pred)
        self.log(name="val_loss", value=test_loss, on_step=False, on_epoch=True)
        return test_loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=1e-3)


class PredictorModel(nn.Module):

    def __init__(self, n_timesteps, n_features, hidden_size=20, n_target_steps=7):
        super().__init__()
        self.n_timesteps = n_timesteps
        self.n_features = n_features
        self.hidden_size = hidden_size
        self.n_target_steps = n_target_steps

        self.lstm = nn.LSTM(input_size=self.n_features, hidden_size=self.hidden_size, num_layers=1, batch_first=True)
        self.linear = nn.Linear(self.hidden_size, out_features=self.n_features)
        self.double()

    def forward(self, x):
        # Pass through LSTM
        x, _ = self.lstm(x)

        # Slice the output to the last `n_target_steps` timesteps
        x = x[:, -self.n_target_steps :, :]

        # Pass through the linear layer
        x = self.linear(x)
        return x
