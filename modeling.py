import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator

dim = (150, 150)
channel = (3, )
input_shape = dim + channel
batch_size = 16
epoch = 10

train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
val_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)
test_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_directory(
    'public/jupyter-notebook/dataset/train/',
    target_size=dim,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=True
)
val_generator = val_datagen.flow_from_directory(
    'public/jupyter-notebook/dataset/validation/',
    target_size=dim,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=True
)
test_generator = test_datagen.flow_from_directory(
    'public/jupyter-notebook/dataset/test/',
    target_size=dim,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=True
)

num_class = test_generator.num_classes
labels = train_generator.class_indices.keys()