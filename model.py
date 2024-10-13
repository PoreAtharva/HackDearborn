from keras.models import load_model  # TensorFlow is required for Keras to work
import numpy as np
import cv2

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("E:/HackDearborn/FetchAI/Agents/Video sender and Image frame creator/keras_Model.h5", compile=False)

# Load the labels
class_names = open("E:/HackDearborn/FetchAI/Agents/Video sender and Image frame creator/labels.txt", "r").readlines()

# Create the array of the right shape to feed into the keras model
# The 'length' or number of images you can put into the array is
# determined by the first position in the shape tuple, in this case 1
data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

# Replace this with the path to your image
image = cv2.imread("E:/HackDearborn/FetchAI/Agents/Video sender and Image frame creator/test_dataset/test_dataset/fake/aagfhgtpmv_frame_0_0.jpg")
print(type(image))

# Resize the image to 224x224
image = cv2.resize(image, (224, 224))

# Convert the image to RGB (if needed, since OpenCV loads images in BGR format)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Normalize the image to the range [-1, 1]
normalized_image_array = (image.astype(np.float32) / 127.5) - 1

# Load the image into the array
data[0] = normalized_image_array

# Predict using the model
prediction = model.predict(data)
index = np.argmax(prediction)
class_name = class_names[index]
confidence_score = prediction[0][index]

# Print prediction and confidence score
print("Class:", class_name[2:], end="")
print("Confidence Score:", confidence_score)
