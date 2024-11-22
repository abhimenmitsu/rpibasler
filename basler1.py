'''
more logging with opencv capturing images
settting exposure rate - this decides the frame rate of basler
setting frame rate to show on window through opencv
'''

import logging
from pypylon import pylon
import cv2
import sys
import time
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all levels of logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
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

cv2.namedWindow('title', cv2.WINDOW_NORMAL)
# Open the camera
camera.Open()
logger.debug("Camera opened.")

# Ensure the camera is in continuous acquisition mode
try:
    camera.AcquisitionMode.SetValue('Continuous')
    logger.debug("Acquisition mode set to 'Continuous'.")
except Exception as e:
    logger.error(f"Could not set AcquisitionMode: {e}")
    camera.Close()
    sys.exit(1)

# Disable trigger mode (ensure 'Free Run' mode)
try:
    camera.TriggerMode.SetValue('Off')
    logger.debug("Trigger mode set to 'Off'.")
except Exception as e:
    logger.error(f"Could not set TriggerMode: {e}")
    camera.Close()
    sys.exit(1)

# Set the frame rate (if supported)
# try:
#     camera.AcquisitionFrameRateEnable.SetValue(True)
#     camera.AcquisitionFrameRate.SetValue(desired_fps)
#     logger.debug(f"Frame rate set to {desired_fps} FPS.")
# except Exception as e:
#     logger.warning(f"Could not set frame rate: {e}")



# # Set the frame rate to auto (if supported)
# try:
#     camera.AcquisitionFrameRateEnable.SetValue(False)  # Disable manual frame rate setting to allow auto mode
#     logger.debug("Frame rate set to auto.")
# except Exception as e:
#     logger.warning(f"Could not set frame rate to auto: {e}")


try:
    camera.ExposureAuto.SetValue('Off')  # Disable automatic exposure
    camera.ExposureTime.SetValue(12500.0)  # Set exposure time to 10,000 microseconds (10 ms)  #100fps
    logger.debug("Exposure time set to 10,000 microseconds.")
except Exception as e:
    logger.warning(f"Could not set exposure time: {e}")


# Optionally, adjust gain if images are too dark
try:
    camera.GainAuto.SetValue('Off')  # Disable automatic gain
    camera.Gain.SetValue(0.0)  # Set gain to 10 dB
    logger.debug("Gain set to 0.0.")
except Exception as e:
    logger.warning(f"Could not set gain: {e}")

try:
    camera.BalanceWhiteAuto.SetValue('Off')
    camera.BalanceWhiteAuto.SetValue('continuous')
    logger.debug("white balance continuous")
except Exception as e:
    logger.warning(f"Could not set gain: {e}")



# Optionally, reduce image resolution to increase frame rate
# try:
#     camera.Width.SetValue(640)
#     camera.Height.SetValue(360)
#     logger.debug("Image resolution set to 640x360.")
# except Exception as e:
#     logger.warning(f"Could not set image resolution: {e}")

# Start grabbing with appropriate strategy
# camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByInstantCamera)
# logger.info("Camera started grabbing images.")


# # Start grabbing continuously with minimal delay
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
logger.info("Camera started grabbing images.")

# Create the ImageFormatConverter object
converter = pylon.ImageFormatConverter()

# Set the converter output format to BGR8 (for OpenCV)
converter.OutputPixelFormat = pylon.PixelType_BGR8packed
converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
logger.debug("ImageFormatConverter configured for BGR8packed output.")

# Initialize variables for timing and counting
start_time = time.time()
elapsed_time = 0
image_count = 0
total_save_time = 0


# Calculate the wait time in milliseconds for cv2.imshow
#wait_time = int(1000 / 60)

try:
    while elapsed_time < 20:  # Run the loop for 10 seconds
        frame_start_time = time.time()
        logger.debug(f"Starting frame capture {image_count + 1}.")

        # Retrieve the latest image from the camera
        start_time1 = time.time()
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        logger.debug("Image retrieved from camera.")
        end_time1 = time.time()
        save_time1 = end_time1 - start_time1
        logger.debug(f"Time taken to grab image: {save_time1:.6f} seconds.")
        if grabResult.GrabSucceeded():
            logger.debug("Image grab succeeded.")

            start_time2 = time.time()
            # Convert the image to OpenCV format using the converter
            image = converter.Convert(grabResult)
            logger.debug("Image converted to OpenCV format.")
            end_time2 = time.time()
            save_time2 = end_time2 - start_time2
            logger.debug(f"Time taken to convert image: {save_time2:.6f} seconds.")


            start_time3 = time.time()
            img = image.GetArray()
            logger.debug(f"Image array shape: {img.shape}")
            end_time3 = time.time()
            save_time3 = end_time3 - start_time3
            logger.debug(f"Time taken to getarray image: {save_time3:.6f} seconds.")
            # Resize the image to 640x360
            # resized_img = cv2.resize(img, (640, 360))
            # logger.debug(f"Image resized to {resized_img.shape[1]}x{resized_img.shape[0]}.")

            # Generate a unique filename
            filename = os.path.join(output_dir, f'image_{image_count:05d}.jpg')

            # Measure the time taken to save the image
            # save_start_time = time.time()
            # cv2.imwrite(filename, img)
            # save_end_time = time.time()
            # logger.debug(f"Image saved as {filename}.")

            save_start_time = time.time()
            cv2.imshow('title', img)
            save_end_time = time.time()

            # if cv2.waitKey(wait_time) == 27:  # Wait 'wait_time' milliseconds; exit if 'Esc' is pressed
            #     break

            if cv2.waitKey(1) & 0xff == ord('q'):
                break

            # Update counters and timing
            image_count += 1
            save_time = save_end_time - save_start_time
            total_save_time += save_time
            logger.debug(f"Time taken to show 1 frame: {save_time:.6f} seconds.")

            # Update elapsed time
            elapsed_time = time.time() - start_time
            logger.debug(f"Elapsed time: {elapsed_time:.2f} seconds.")

            # Calculate the time to wait to maintain the desired FPS
            frame_end_time = time.time()
            frame_duration = frame_end_time - frame_start_time

        else:
            # If the grab was not successful, print the error
            logger.error(f"Error: {grabResult.ErrorCode} {grabResult.ErrorDescription}")

        # Release the grab result to free resources
        grabResult.Release()
        logger.debug("Grab result released.")

except Exception as e:
    logger.exception(f"An exception occurred: {e}")

finally:
    # Stop the camera and release resources
    camera.StopGrabbing()
    camera.Close()
    logger.info("Camera stopped and closed.")

    # Calculate statistics
    total_time = time.time() - start_time
    average_save_time = total_save_time / image_count if image_count > 0 else 0
    fps = image_count / total_time if total_time > 0 else 0

    # Print out the results
    logger.info("\nCapture completed.")
    logger.info(f"Total images saved: {image_count}")
    logger.info(f"Total time elapsed: {total_time:.2f} seconds")
    logger.info(f"Total time saving images: {total_save_time:.4f} seconds")
    logger.info(f"Average time per image: {average_save_time:.4f} seconds")
    logger.info(f"Average FPS: {fps:.2f}")
