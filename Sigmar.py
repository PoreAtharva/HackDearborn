import base64
import os
import cv2
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model

# Define a list of image file extensions you want to process
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

# Function to encode the image into base64
def encode_image_to_base64(image_path):
    try:
        # Read the image from the file
        image = cv2.imread(image_path)
        
        # Check if the image was loaded correctly
        if image is None:
            print(f"Error: Unable to read image from {image_path}")
            return None

        # Encode the image to PNG format in memory
        success, encoded_image = cv2.imencode('.png', image)
        
        if not success:
            print("Error encoding the image")
            return None
        
        # Convert the encoded image to base64 string
        return base64.b64encode(encoded_image).decode('utf-8')
    
    except IOError as e:
        print(f"Error reading image file: {e}")
        return None
    
# Message model that holds the image data and filename
class FileMessage(Model):
    file_data: str  # Base64-encoded image data
    filename: str   # Filename for keeping track of the file

# Define the recipient's address
RECIPIENT_ADDRESS = "agent1qvm7v76zs6w2x90xvq99yc5xh7c2thjtm44zc09me556zxnra627gkf4zum"

# Create the sigmar agent
sigmar = Agent(
    name="sigmar",
    port=8000,
    seed="sigmar secret phrase",
    endpoint=["http://127.0.0.1:8000/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(sigmar.wallet.address())

# Send all images in the directory when the agent starts up
@sigmar.on_event("startup")
async def send_files(ctx: Context):
    directory = r"E:/HackDearborn/FetchAI/Agents/Video sender and Image frame creator/test_images"
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if it's an image file
        if filename.lower().endswith(IMAGE_EXTENSIONS):
            ctx.logger.info(f"Processing image file: {filename}")

            # Encode the image using base64
            encoded_file = encode_image_to_base64(file_path)

            # Check if the file encoding was successful
            if encoded_file is None:
                ctx.logger.error(f"Failed to encode the image: {file_path}")
                continue

            # Send the encoded image file
            await ctx.send(RECIPIENT_ADDRESS, FileMessage(file_data=encoded_file, filename=filename))
            ctx.logger.info(f"Sent image {filename}")

# Ensure the agent runs
if __name__ == "__main__":
    sigmar.run()
