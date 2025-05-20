import os

# Silenciar logs de TensorFlow (0=todo, 3=solo errores)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Desactivar el uso de GPU completamente
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
