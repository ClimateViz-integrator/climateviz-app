# dataset.py - Clase para gestión de datos
"""
Módulo para la gestión de datos de series temporales,
incluyendo división en conjuntos y creación de secuencias.
"""


import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from Helper.config import CONFIG

class TimeSeriesDataset:
    """
    Clase para gestionar conjuntos de datos de series temporales para modelos de aprendizaje supervisado.

    Permite dividir los datos en conjuntos de entrenamiento, validación y prueba, 
    así como generar secuencias de entrada-salida para aprendizaje secuencial.
    """

    def __init__(self, input_length=None, output_length=None):
        """
        Inicializa el dataset temporal.

        Args:
            input_length (int, optional): Longitud de la secuencia de entrada. 
                                          Por defecto, se toma de CONFIG.
            output_length (int, optional): Longitud de la secuencia de salida. 
                                           Por defecto, se toma de CONFIG.
        """
        self.input_length = input_length or CONFIG['SECUENCIA']['INPUT_LENGTH']
        self.output_length = output_length or CONFIG['SECUENCIA']['OUTPUT_LENGTH']

    def split_data(self, df, train_size=None, val_size=None, test_size=None):
        """
        Divide el DataFrame en conjuntos de entrenamiento, validación y prueba.

        Args:
            df (pd.DataFrame): Conjunto de datos completo.
            train_size (float): Proporción para entrenamiento (0 < train_size < 1).
            val_size (float): Proporción para validación (0 < val_size < 1).
            test_size (float): Proporción para prueba (0 < test_size < 1).

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (train, val, test)
        """
        train_size = train_size or CONFIG['DATOS']['TRAIN_SIZE']
        val_size = val_size or CONFIG['DATOS']['VAL_SIZE']
        test_size = test_size or CONFIG['DATOS']['TEST_SIZE']

        if not np.isclose(train_size + val_size + test_size, 1.0):
            raise ValueError("Las proporciones de división deben sumar 1.0")

        # División secuencial (sin barajar)
        test_rel_size = test_size
        val_rel_size = val_size / (1.0 - test_size)

        train_val, test = train_test_split(df, test_size=test_rel_size, shuffle=False)
        train, val = train_test_split(train_val, test_size=val_rel_size, shuffle=False)

        print(f'[INFO] Tamaño del set de entrenamiento: {train.shape}')
        print(f'[INFO] Tamaño del set de validación: {val.shape}')
        print(f'[INFO] Tamaño del set de prueba: {test.shape}')

        return train, val, test

    def _get_target_indices(self, df, target_col):
        """
        Obtiene los índices de las columnas objetivo.

        Args:
            df (pd.DataFrame): DataFrame original.
            target_col (str | int | list): Nombre(s) o índice(s) de columna(s).

        Returns:
            List[int]: Índices de columnas objetivo.
        """
        target_col = target_col or CONFIG['TARGET_COL']
        if isinstance(target_col, (str, int)):
            target_col = [target_col]

        target_idxs = []
        for col in target_col:
            if isinstance(col, str):
                if col not in df.columns:
                    raise ValueError(f"Columna '{col}' no existe en el DataFrame.")
                target_idxs.append(df.columns.get_loc(col))
            elif isinstance(col, int):
                if col < 0 or col >= df.shape[1]:
                    raise ValueError(f"Índice de columna inválido: {col}")
                target_idxs.append(col)
            else:
                raise TypeError("target_col debe ser str, int o lista de estos.")

        return target_idxs

    def create_sequences(self, df, target_col=None):
        """
        Genera secuencias de entrada y salida para entrenamiento supervisado.

        Args:
            df (pd.DataFrame): Datos de entrada.
            target_col (str | int | list, optional): Columnas objetivo.

        Returns:
            Tuple[np.ndarray, np.ndarray]: X (input), y (target output)
        """
        array = df.values
        X, y = [], []

        target_idxs = self._get_target_indices(df, target_col)
        total_len = len(df)

        for i in range(total_len - self.input_length - self.output_length + 1):
            X.append(array[i:i + self.input_length, :])
            y_seq = array[i + self.input_length: i + self.input_length + self.output_length, target_idxs]
            y.append(y_seq)

        return np.array(X), np.array(y)

    def prepare_dataset(self, df, target_col=None):
        """
        Prepara el dataset completo para entrenamiento, validación y prueba.

        Args:
            df (pd.DataFrame): Conjunto de datos completo.
            target_col (str | int | list, optional): Columnas objetivo.

        Returns:
            dict: Diccionario con:
                'x_train', 'y_train',
                'x_val', 'y_val',
                'x_test', 'y_test'
        """
        df_train, df_val, df_test = self.split_data(df)
        x_train, y_train = self.create_sequences(df_train, target_col)
        x_val, y_val = self.create_sequences(df_val, target_col)
        x_test, y_test = self.create_sequences(df_test, target_col)

        print('[INFO] Tamaños finales:')
        print(f'x_train: {x_train.shape}, y_train: {y_train.shape}')
        print(f'x_val:   {x_val.shape}, y_val:   {y_val.shape}')
        print(f'x_test:  {x_test.shape}, y_test:  {y_test.shape}')

        return {
            'x_train': x_train, 'y_train': y_train,
            'x_val': x_val, 'y_val': y_val,
            'x_test': x_test, 'y_test': y_test
        }
