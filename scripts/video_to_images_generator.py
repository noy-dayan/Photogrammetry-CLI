import cv2
import os
from skimage.metrics import structural_similarity as ssim


def extract_frames(video_path, output_folder, max_frames=100, max_overlap_percentage=6, ssim_threshold=0.95):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Calculate step size for extracting frames
    step_size = total_frames // max_frames

    count = 0
    frame_num = 0
    extracted_frames = []

    prev_frame = None

    while count < max_frames and frame_num < total_frames:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()

        if ret:
            if prev_frame is not None:
                # Calculate SSIM between current frame and previous frame
                similarity = ssim(cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY), cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

                if similarity > ssim_threshold:
                    # Skip current frame if similarity is too high
                    frame_num += step_size
                    continue

            # Check overlap with previous frames
            overlap = False
            for existing_frame in extracted_frames[max(0, count - 10):]:  # Check last 10 frames for overlap
                overlap_percentage = calculate_overlap_percentage(frame, existing_frame)
                if overlap_percentage > max_overlap_percentage:
                    overlap = True
                    break

            if not overlap:
                extracted_frames.append(frame)
                output_path = os.path.join(output_folder, f"frame_{count}.jpg")
                cv2.imwrite(output_path, frame)
                print(f"Extracted frame {count}")
                count += 1

            prev_frame = frame

        frame_num += step_size

    cap.release()
    if len(extracted_frames) == 0:
        print("No frames were extracted.")
    else:
        print(f"Finished extracting {len(extracted_frames)} frames.")

    return extracted_frames


def calculate_overlap_percentage(image1, image2):
    # Convert images to grayscale
    gray_image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray_image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference between the images
    diff = cv2.absdiff(gray_image1, gray_image2)

    # Count the number of non-zero pixels (pixels that are different)
    non_zero_pixels = cv2.countNonZero(diff)

    # Calculate overlap percentage
    total_pixels = image1.shape[0] * image1.shape[1]
    overlap_percentage = (total_pixels - non_zero_pixels) / total_pixels * 100

    return overlap_percentage


