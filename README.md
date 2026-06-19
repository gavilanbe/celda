# 🗡️ Celda

Un pequeño action-RPG top-down con estética Game Boy, hecho en canvas puro y sin frameworks.

## ✨ Características

- Héroe animado (idle, caminar y ataque) en cuatro direcciones, dibujado con un spritesheet de 128x128.
- Mundo por tiles de 64x64 con árboles, piedras y matorrales, y colisiones contra sólidos.
- Render pixel-perfect con escalado nearest-neighbor sobre un viewport lógico de 640x360.
- Pipeline de arte propio en Python para generar el sprite del héroe y assets al estilo de la paleta clásica.
- Incluye una copia vendorizada de la desensamblación `pokered` como referencia de estilo y fuente de assets.

## 🚀 Cómo jugar / ejecutar

```bash
# Servidor local sencillo (no necesita dependencias)
python3 -m http.server 5173
# Abre http://localhost:5173

# Regenerar el sprite del héroe (opcional)
python3 scripts/generate-hero.py
```

## 🎮 Controles

- Mover: Flechas o `W` `A` `S` `D`
- Atacar: `Espacio`

## 🛠️ Tecnología

- JavaScript (módulos ES) sobre Canvas 2D, sin dependencias en runtime.
- Configuración de juego declarativa en `game.config.json`.
- Scripts de generación de assets en Python.
- Referencia de arte: disassembly `pokered` vendorizada.

## 📦 Parte de mi colección de juegos

Uno más de mis juegos web hobby. ¡A explorar! 🎮
