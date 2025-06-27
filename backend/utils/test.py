import tensorflow as tf
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

print("Testing GPU acceleration...")
with tf.device('/GPU:0'):
    a = tf.random.normal([10000, 10000])
    b = tf.random.normal([10000, 10000])
    c = tf.matmul(a, b)

print("Done")