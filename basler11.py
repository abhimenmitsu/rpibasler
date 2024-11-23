import logging
from pypylon import pylon
import cv2
import sys
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# Create a directory to save images
output_dir = 'captured_images'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    logger.debug(f"Created output directory: {output_dir}")
else:
    logger.debug(f"Output directory already exists: {output_dir}")

# Connect to the first available camera
logger.info("Connecting to the first available camera...")
try:
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    logger.info(f"Connected to camera: {camera.GetDeviceInfo().GetModelName()}")
except Exception as e:
    logger.error(f"Could not connect to camera: {e}")
    sys.exit(1)

# Open the camera
camera.Open()
logger.debug("Camera opened.")

# Configure camera settings for desired FPS
try:
    # Disable auto features
    camera.ExposureAuto.SetValue('Off')
    camera.GainAuto.SetValue('Off')
    camera.BalanceWhiteAuto.SetValue('Off')

    # Set exposure time to achieve 250 FPS (exposure < 1/250 seconds)
    exposure_time_us = 4000  # 4000 microseconds = 4 ms
    camera.ExposureTime.SetValue(exposure_time_us)
    logger.debug(f"Exposure time set to {exposure_time_us} microseconds.")

    # Enable and set frame rate to 250 FPS
    camera.AcquisitionFrameRateEnable.SetValue(True)
    desired_fps = 250
    camera.AcquisitionFrameRate.SetValue(desired_fps)
    logger.debug(f"Frame rate set to {desired_fps} FPS.")

    # Optionally reduce resolution to optimize performance
    camera.Width.SetValue(640)
    camera.Height.SetValue(360)
    logger.debug("Resolution set to 640x360.")
except Exception as e:
    logger.error(f"Error setting camera parameters: {e}")
    camera.Close()
    sys.exit(1)

# Start grabbing with the latest image strategy
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
logger.info("Camera started grabbing images.")

# Create the ImageFormatConverter object
converter = pylon.ImageFormatConverter()
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
logger.debug("ImageFormatConverter configured for BGR8packed output.")

# Initialize variables for timing and counting
start_time = time.time()
elapsed_time = 0
image_count = 0

try:
    while elapsed_time < 10:  # Run the loop for 10 seconds
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            # Convert to OpenCV format
            # image = converter.Convert(grabResult)
            # img = image.GetArray()
            
            # Save the image (optional)
            # filename = os.path.join(output_dir, f'image_{image_count:05d}.jpg')
            # cv2.imwrite(filename, img)
            # logger.debug(f"Image saved as {filename}.")
            
            image_count += 1
            elapsed_time = time.time() - start_time
        else:
            logger.error(f"Error: {grabResult.ErrorCode} {grabResult.ErrorDescription}")
        grabResult.Release()

except Exception as e:
    logger.exception(f"An exception occurred: {e}")

finally:
    # Stop the camera and release resources
    camera.StopGrabbing()
    camera.Close()
    logger.info("Camera stopped and closed.")

    # Calculate and log FPS
    total_time = time.time() - start_time
    fps = image_count / total_time if total_time > 0 else 0
    logger.info("\nCapture completed.")
    logger.info(f"Total images captured: {image_count}")
    logger.info(f"Total time elapsed: {total_time:.2f} seconds")
    logger.info(f"Average FPS: {fps:.2f}")


#     python3 basler11.py
# 2024-11-23 19:41:08,439 [DEBUG] Created output directory: captured_images
# 2024-11-23 19:41:08,440 [INFO] Connecting to the first available camera...
# 2024-11-23 19:41:09,411 [INFO] Connected to camera: acA1440-220uc
# 2024-11-23 19:41:09,431 [DEBUG] Camera opened.
# 2024-11-23 19:41:09,438 [DEBUG] Exposure time set to 4000 microseconds.
# 2024-11-23 19:41:09,441 [DEBUG] Frame rate set to 250 FPS.
# 2024-11-23 19:41:09,444 [DEBUG] Resolution set to 640x360.
# 2024-11-23 19:41:09,455 [INFO] Camera started grabbing images.
# 2024-11-23 19:41:09,456 [DEBUG] ImageFormatConverter configured for BGR8packed output.
# 2024-11-23 19:41:19,483 [INFO] Camera stopped and closed.
# 2024-11-23 19:41:19,483 [INFO] 
# Capture completed.
# 2024-11-23 19:41:19,484 [INFO] Total images captured: 2464
# 2024-11-23 19:41:19,484 [INFO] Total time elapsed: 10.03 seconds
# 2024-11-23 19:41:19,485 [INFO] Average FPS: 245.74
