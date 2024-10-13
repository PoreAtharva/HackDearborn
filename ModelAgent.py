import base64
import os
import cv2
from uagents.setup import fund_agent_if_low
from uagents import Agent, Context, Model

# Store received file chunks in memory
received_file_chunks = []

# Function to decode base64 to file
def decode_base64_to_file(encoded_data, output_file_path):
    with open(output_file_path, "wb") as file:
        file.write(base64.b64decode(encoded_data))

# Function to extract one frame per second from a video file
def extract_frames_from_video(video_path, output_dir, file_name_base):
    video = cv2.VideoCapture(video_path)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_count = 0
    second = 1

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        # Capture one frame per second
        frame_count += 1
        if frame_count % fps == 0:
            frame_file = os.path.join(output_dir, f"{file_name_base}_frame_{second}.png")
            cv2.imwrite(frame_file, frame)
            second += 1

    video.release()

# Define the message model to include a flag for the last chunk (EOF)
class FileMessage(Model):
    file_data: str  # This stores the base64-encoded file data
    filename: str   # Filename for keeping track
    is_last_chunk: bool  # To indicate if this is the last chunk

# Initialize slaanesh agent
slaanesh = Agent(
    name="slaanesh",
    port=8001,
    seed="ModelAgent secret phrase",
    endpoint=["http://127.0.0.1:8002/submit"],
)

# Ensure the agent has enough funds
fund_agent_if_low(slaanesh.wallet.address())

# Handle the reception of files
@slaanesh.on_message(model=FileMessage)
async def receive_file_chunk(ctx: Context, sender: str, msg: FileMessage):
    # Append the chunk to the list of received chunks
    received_file_chunks.append(msg.file_data)
    ctx.logger.info(f"Received file chunk from {sender}")

    # Check if this is the last chunk (EOF)
    if msg.is_last_chunk:
        # Combine the chunks into a complete file
        complete_file_data = ''.join(received_file_chunks)
        
        # Decode the base64 data and save it to a file
        output_file_path = f"E:\\HackDearborn\\FetchAI\\Agents\\Video sender and Image frame creator\\test_videos\\{msg.filename}"
        decode_base64_to_file(complete_file_data, output_file_path)
        ctx.logger.info(f"File received and saved as {output_file_path}")

        # Extract frames from the video
        file_name_base = os.path.splitext(msg.filename)[0]
        output_dir = r"E:\\HackDearborn\\FetchAI\\Agents\\Video sender and Image frame creator\\test_images"
        os.makedirs(output_dir, exist_ok=True)
        extract_frames_from_video(output_file_path, output_dir, file_name_base)
        ctx.logger.info(f"Frames extracted and saved in {output_dir}")

        # Clear the received chunks list for the next file transfer
        received_file_chunks.clear()
    else:
        ctx.logger.info(f"Waiting for more chunks...")

# Run the agent
if __name__ == "__main__":
    slaanesh.run()
