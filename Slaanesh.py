import base64
import os
import cv2
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model

RECIPIENT_ADDRESS="agent1qtu6wt5jphhmdjau0hdhc002ashzjnueqe89gvvuln8mawm3m0xrwmn9a76"

# Function to decode base64 and save it to an image file
def decode_base64_to_image(encoded_data, output_file_path):
    try:
        with open(output_file_path, "wb") as file:
            file.write(base64.b64decode(encoded_data))
    except IOError as e:
        print(f"Error writing image file: {e}")

# Function to preprocess the image (resize to 224x224)
def preprocess_image(image_path):
    # Read the image from the file
    image = cv2.imread(image_path)
    
    # Check if the image was loaded successfully
    if image is None:
        raise ValueError(f"Error: Unable to read image from {image_path}")
    
    # Resize the image to 224x224
    resized_image = cv2.resize(image, (224, 224))
    
    # Save the preprocessed image back to the same path or return it for further processing
    cv2.imwrite(image_path, resized_image)
    
    return resized_image

# Message model to handle file data
class FileMessage(Model):
    file_data: str  # Base64-encoded image data
    filename: str   # Filename

# Initialize slaanesh agent
slaanesh = Agent(
    name="slaanesh",
    port=8001,
    seed="slaanesh secret phrase",
    endpoint=["http://127.0.0.1:8001/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(slaanesh.wallet.address())

# Handle the reception of image files
@slaanesh.on_message(model=FileMessage)
async def receive_image(ctx: Context, sender: str, msg: FileMessage):
    image_data = msg.file_data  # Base64-encoded image data
    output_file_path = f"E:\\HackDearborn\\FetchAI\\Agents\\Video sender and Image frame creator\\test_images\\{msg.filename}"
    
    try:
        # Decode and save the image
        decode_base64_to_image(image_data, output_file_path)
        ctx.logger.info(f"Image received and saved as {output_file_path}")
        
        # Preprocess the saved image (resize it to 224x224)
        preprocess_image(output_file_path)
        ctx.logger.info(f"Image preprocessed (resized to 224x224) and saved as {output_file_path}")

    except IOError as e:
        ctx.logger.error(f"Error saving or preprocessing image file: {e}")



    # Send the encoded image file
    await ctx.send(RECIPIENT_ADDRESS, FileMessage(file_data=str(preprocess_image)))
    ctx.logger.info(f"Sent image to Model")

# Run the agent
if __name__ == "__main__":
    slaanesh.run()
