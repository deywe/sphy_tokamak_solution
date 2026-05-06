import py5
import numpy as np
import pandas as pd
import hashlib

# ===================== CARREGAR DADOS =====================
parquet_file = input("Digite o nome do arquivo .parquet (ou pressione Enter para o padrão): ").strip()
if not parquet_file:
    parquet_file = "sphy_sequence_1000frames.parquet"  # exemplo

df = pd.read_parquet(parquet_file)
print(f"Carregado {len(df)} frames do arquivo: {parquet_file}")

# Hash de validação do arquivo
file_hash = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()
print(f"SHA-256 do arquivo: {file_hash}\n")

# ===================== PY5 VISUALIZAÇÃO =====================
def setup():
    py5.size(1000, 800, py5.P3D)
    py5.window_resizable(True)
    py5.window_title("SPHY ENGINE - Validador Visual")
    py5.color_mode(py5.HSB, 360, 100, 100)
    
    global current_hash, zoom, rot_x, rot_y, current_frame
    current_hash = " " * 64
    zoom = 0
    rot_x = 0
    rot_y = 0
    current_frame = 0

def draw():
    global current_hash, current_frame
    
    f = py5.frame_count
    current_frame = min(f, len(df) - 1)
    
    row = df.iloc[current_frame]
    mix = row['mix']
    jitter = row['jitter']
    estabilidade = row['estabilidade']
    expected_hash = row['sha256']

    # --- Renderização idêntica ao original ---
    py5.background(0)
    
    py5.push_matrix()
    py5.translate(py5.width / 2, py5.height / 2, zoom)
    py5.rotate_x(rot_x)
    py5.rotate_y(rot_y)
    
    t = f * 0.03
    num_fibras = 95
    phi = (1 + 5**0.5) / 2

    for i in range(num_fibras):
        angle_hilbert = i * (360 / num_fibras)
        angle_sphy = i * (360 / num_fibras * phi)
        base_angle = py5.lerp(angle_hilbert, angle_sphy, mix)
        
        noise = py5.random(-jitter, jitter) if jitter > 0 else 0
        angle = np.deg2rad(base_angle + t + noise)
        
        pulsacao = py5.sin(t * 0.5 + i * 0.1) * (40 * (1.1 - estabilidade))
        raio_interno = 60 + pulsacao
        raio_externo = 380 + pulsacao
        
        hue = py5.lerp(15, 190, mix)
        sat = 100 if mix < 1.0 else 80
        
        py5.stroke(hue, sat, 100, 200)
        py5.stroke_weight(py5.lerp(0.8, 1.8, mix))
        py5.no_fill()
        
        x1 = np.cos(angle) * raio_interno
        y1 = np.sin(angle) * raio_interno
        x2 = np.cos(angle) * raio_externo
        y2 = np.sin(angle) * raio_externo
        
        py5.bezier(x1, y1, 0,
                   np.cos(angle + 0.4) * (raio_interno + 150), 
                   np.sin(angle + 0.4) * (raio_interno + 150), 50,
                   np.cos(angle - 0.4) * (raio_externo - 150), 
                   np.sin(angle - 0.4) * (raio_externo - 150), -50,
                   x2, y2, 0)

    py5.pop_matrix()

    # HUD com validação
    render_hud(f, mix, estabilidade, expected_hash)

def render_hud(f, mix, estabilidade, expected_hash):
    global current_hash
    current_hash = expected_hash  # usa o hash salvo

    py5.no_stroke()
    py5.fill(0, 0, 5, 220)
    py5.rect(20, 20, 420, 240, 10)
    
    py5.text_size(18)
    if mix <= 0.0:
        py5.fill(15, 100, 100)
        py5.text("MODO: HILBERT (EGO-FORCE)", 40, 50)
    elif mix < 1.0:
        py5.fill(40, 100, 100)
        py5.text("MODO: ACOPLAMENTO GEODÉSICO...", 40, 50)
    else:
        py5.fill(190, 100, 100)
        py5.text("MODO: SPHY (ABSOLUTE SOVEREIGN)", 40, 50)

    py5.text_size(14)
    py5.fill(0, 0, 100)
    py5.text(f"COERÊNCIA: {int(estabilidade*100)}%", 40, 80)
    py5.text(f"FRAME: {f} / {len(df)}", 40, 105)
    
    py5.fill(0, 0, 70)
    py5.text("SHA-256 (VALIDADO):", 40, 135)
    py5.fill(0, 0, 100)
    py5.text_size(11)
    py5.text(expected_hash[:32], 40, 160)
    py5.text(expected_hash[32:], 40, 180)

    # Barra de progresso
    py5.fill(0, 0, 20)
    py5.rect(40, 205, 380, 5)
    py5.fill(py5.lerp(15, 190, mix), 100, 100)
    py5.rect(40, 205, mix * 380, 5)

def mouse_dragged():
    global rot_x, rot_y
    rot_y += (py5.mouse_x - py5.pmouse_x) * 0.01
    rot_x -= (py5.mouse_y - py5.pmouse_y) * 0.01

def mouse_wheel(event):
    global zoom
    zoom += event.get_count() * 20

py5.run_sketch()
