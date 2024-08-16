import cv2
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm
from utils import *


def extract_frames(video_path, output_folder, max_frames=100, max_overlap_percentage=6, ssim_threshold=0.95):
    """
       Extracts optimal frames from a video based on structural similarity (SSIM) and frame overlap criteria.

       Parameters:
       - video_path (str): Path to the input video file.
       - output_folder (str): Path to the output folder where frames will be saved.
       - max_frames (int, optional): Maximum number of frames to extract (default is 100).
       - max_overlap_percentage (int, optional): Maximum allowed percentage overlap with previous frames (default is 6).
       - ssim_threshold (float, optional): SSIM threshold below which frames are considered different (default is 0.95).

       Returns:
       - extracted_frames (list): List of extracted frames as numpy arrays.

       This function extracts frames from a video, ensuring that each frame differs significantly from the
       previous frames based on SSIM and overlap criteria. It skips frames that are too similar to already
       extracted frames to ensure diversity in the extracted set.

       Note:
       - Requires OpenCV (`cv2`), scikit-image (`skimage`), tqdm (`tqdm`), and `utils` module.
       - Outputs frames named 'frame_0.jpg', 'frame_1.jpg', ..., 'frame_N.jpg' in the specified output folder.
       """

    # Create output folder if it doesn't exist
    mkdir(output_folder)

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

    pbar = tqdm(total=max_frames, desc="Extracting frames", position=0, leave=True,
                bar_format='\033[35m{desc}:\033[0m \033[1;37m{percentage:3.0f}%|{bar}|\033[0m \033[37m[{elapsed}<{remaining}]\033[0m')

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
                output_path = f"{output_folder}\\frame_{count}.jpg"
                cv2.imwrite(output_path, frame)
                count += 1
                pbar.update(1)
                pbar.set_postfix({"Frame": count})

            prev_frame = frame

        frame_num += step_size

    # Update progress bar to 100% if fewer frames were extracted than max_frames
    if count < max_frames:
        pbar.update(max_frames-count)

    pbar.close()

    cap.release()

    if len(extracted_frames) == 0:
        print_err("No frames were extracted.")
    else:
        print(f"Finished extracting {len(extracted_frames)} optimal frames.")

    return extracted_frames


def calculate_overlap_percentage(image1, image2):
    """
    Calculates the percentage overlap between two images based on pixel differences.

    Parameters:
    - image1 (numpy.ndarray): First input image as a numpy array.
    - image2 (numpy.ndarray): Second input image as a numpy array.

    Returns:
    - overlap_percentage (float): Percentage overlap between the two images.

    This function computes the overlap percentage between two images by comparing
    their grayscale versions. It calculates the absolute difference between the images,
    counts the number of non-zero pixels (pixels that differ), and computes the
    percentage overlap based on the total number of pixels.

    Note:
    - Requires OpenCV (`cv2`).
    """
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


