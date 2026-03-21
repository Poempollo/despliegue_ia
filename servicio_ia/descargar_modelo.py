import tensorflow as tf

def main():
    print("Descargando modelo...")
    modelo = tf.keras.applications.MobileNetV2(weights='imagenet')
    
    ruta_guardado = "modelo_clasificacion.keras"
    modelo.save(ruta_guardado)
    print(f"¡Modelo guardado correctamente como {ruta_guardado}!")

if __name__ == "__main__":
    main()