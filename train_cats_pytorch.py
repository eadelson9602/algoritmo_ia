# train_cats_pytorch.py
import os, random, numpy as np, pandas as pd
from PIL import Image, ImageOps
import torch, torch.nn as nn, torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib
matplotlib.use('Agg')  # Backend no interactivo para evitar problemas en servidores
import matplotlib.pyplot as plt
import sys
import traceback

# ------------- Config -------------
CSV = "dataset.csv"   # generado en Paso 1
IMG_SIZE = 128
BATCH = 16
EPOCHS = 20
OUT_DIR = "artifacts"
os.makedirs(OUT_DIR, exist_ok=True)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}", flush=True)
# Crear archivo de log
log_file = open("training.log", "w", encoding="utf-8")
def log_print(*args):
    msg = " ".join(str(a) for a in args)
    print(msg, flush=True)
    log_file.write(msg + "\n")
    log_file.flush()

# ------------- Dataset -------------
class CatsDataset(Dataset):
    def __init__(self, df, train=True):
        self.df = df.reset_index(drop=True); self.train = train
    def __len__(self): return len(self.df)
    def rand_transform(self, img):
        if random.random() < 0.5:
            img = ImageOps.mirror(img)
        angle = random.uniform(-10, 10)
        img = img.rotate(angle)
        # otros augmentations si se desea
        return img
    def pil_to_tensor(self, img):
        img = img.resize((IMG_SIZE,IMG_SIZE))
        arr = np.array(img).astype('float32') / 255.0
        mean = np.array([0.485,0.456,0.406])
        std  = np.array([0.229,0.224,0.225])
        arr = (arr - mean) / std
        arr = np.transpose(arr, (2,0,1))
        return torch.from_numpy(arr).float()
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # Normalizar la ruta para que funcione en Windows y Linux
        img_path = row['image_path'].replace('\\', os.sep).replace('/', os.sep)
        if not os.path.isabs(img_path):
            img_path = os.path.join(os.getcwd(), img_path)
        img = Image.open(img_path).convert('RGB')
        if self.train:
            img = self.rand_transform(img)
        tensor = self.pil_to_tensor(img)
        label = int(row['label'])
        return tensor, label

# ------------- Load CSV and split -------------
log_print(f"Cargando CSV: {CSV}")
try:
    df = pd.read_csv(CSV)
    log_print(f"Total de imágenes: {len(df)}")
    # Normalizar rutas en el DataFrame
    df['image_path'] = df['image_path'].str.replace('\\', os.sep).str.replace('/', os.sep)
    # Verificar que las imágenes existan
    missing = []
    for idx, row in df.iterrows():
        img_path = row['image_path']
        if not os.path.isabs(img_path):
            img_path = os.path.join(os.getcwd(), img_path)
        if not os.path.exists(img_path):
            missing.append(row['image_path'])
    if missing:
        log_print(f"Advertencia: {len(missing)} imágenes no encontradas")
        df = df[~df['image_path'].isin(missing)].reset_index(drop=True)
        log_print(f"Imágenes válidas: {len(df)}")

    # shuffle
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    n = len(df)
    if n < 3:
        raise ValueError(f"No hay suficientes imágenes ({n}). Se necesitan al menos 3 para train/val/test")
    train = df.iloc[:int(0.7*n)]
    val   = df.iloc[int(0.7*n):int(0.85*n)]
    test  = df.iloc[int(0.85*n):]
    log_print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
except Exception as e:
    print(f"Error al cargar el CSV: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    train_loader = DataLoader(CatsDataset(train,train=True), batch_size=BATCH, shuffle=True)
    val_loader   = DataLoader(CatsDataset(val,train=False), batch_size=BATCH, shuffle=False)
    test_loader  = DataLoader(CatsDataset(test,train=False), batch_size=BATCH, shuffle=False)
except Exception as e:
    log_print(f"Error al crear los DataLoaders: {e}")
    traceback.print_exc()
    log_file.close()
    sys.exit(1)

# ------------- Modelo sencillo -------------
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3,32,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32,64,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64,128,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
        )
        feat = (IMG_SIZE//8)*(IMG_SIZE//8)*128
        self.fc = nn.Sequential(nn.Flatten(), nn.Linear(feat,256), nn.ReLU(), nn.Dropout(0.4), nn.Linear(256,2))
    def forward(self,x): return self.fc(self.conv(x))

model = SimpleCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

# ------------- Entrenamiento -------------
print("\nIniciando entrenamiento...")
try:
    best_val_loss = 1e9
    history = {'train_loss':[], 'val_loss':[], 'train_acc':[], 'val_acc':[]}
    for epoch in range(1, EPOCHS+1):
        model.train()
        running_loss=0; correct=0; n=0
        for xb,yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad(); out = model(xb); loss = criterion(out,yb); loss.backward(); optimizer.step()
            running_loss += loss.item()*xb.size(0)
            preds = out.argmax(dim=1); correct += (preds==yb).sum().item(); n += xb.size(0)
        train_loss = running_loss/n; train_acc = correct/n

        # valida
        model.eval()
        vloss=0; vcorrect=0; vn=0
        ys=[]; ypred=[]
        with torch.no_grad():
            for xb,yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                out = model(xb); loss = criterion(out,yb)
                vloss += loss.item()*xb.size(0)
                preds = out.argmax(dim=1)
                ys.extend(yb.cpu().numpy().tolist()); ypred.extend(preds.cpu().numpy().tolist())
                vcorrect += (preds==yb).sum().item(); vn += xb.size(0)
        val_loss = vloss/vn; val_acc = vcorrect/vn

        history['train_loss'].append(train_loss); history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc); history['val_acc'].append(val_acc)

        log_print(f"Epoch {epoch}/{EPOCHS} - train_loss {train_loss:.4f} train_acc {train_acc:.4f} - val_loss {val_loss:.4f} val_acc {val_acc:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), os.path.join(OUT_DIR, "best_model.pth"))
except Exception as e:
    print(f"Error durante el entrenamiento: {e}")
    traceback.print_exc()
    sys.exit(1)

# ------------- Evaluación final en test -------------
try:
    model.load_state_dict(torch.load(os.path.join(OUT_DIR, "best_model.pth")))
    model.eval()
    ys=[]; ypred=[]
    tloss=0; tn=0
    with torch.no_grad():
        for xb,yb in test_loader:
            xb,yb = xb.to(device), yb.to(device)
            out = model(xb); loss = criterion(out,yb)
            tloss += loss.item()*xb.size(0); tn += xb.size(0)
            preds = out.argmax(dim=1)
            ys.extend(yb.cpu().numpy().tolist()); ypred.extend(preds.cpu().numpy().tolist())
    test_loss = tloss/tn
    print("Test loss:", test_loss)
    print(classification_report(ys, ypred, target_names=['sano','enfermo']))
    print("Confusion matrix:\n", confusion_matrix(ys, ypred))
except Exception as e:
    log_print(f"Error durante la evaluación: {e}")
    traceback.print_exc()
    log_file.close()
    sys.exit(1)

# ------------- Guardar curvas (ejemplo) -------------
try:
    if len(history['train_loss']) > 0:
        epochs = range(1, len(history['train_loss'])+1)
    plt.figure(); plt.plot(epochs, history['train_loss'], label='train_loss'); plt.plot(epochs, history['val_loss'], label='val_loss')
    plt.legend(); plt.title('Loss'); plt.savefig(os.path.join(OUT_DIR,'loss.png'))
    plt.close()
    plt.figure(); plt.plot(epochs, history['train_acc'], label='train_acc'); plt.plot(epochs, history['val_acc'], label='val_acc')
    plt.legend(); plt.title('Accuracy'); plt.savefig(os.path.join(OUT_DIR,'acc.png'))
    plt.close()
    log_print("\nEntrenamiento completado exitosamente!")
    log_print(f"Modelo guardado en: {os.path.join(OUT_DIR, 'best_model.pth')}")
    log_print(f"Gráficas guardadas en: {OUT_DIR}")
    log_file.close()
except Exception as e:
    log_print(f"Error al guardar las gráficas: {e}")
    traceback.print_exc()
    log_file.close()
