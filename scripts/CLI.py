import pyCloudCompare as pcc
from video_to_images_generator import extract_frames
from user_manual import *
from point_cloud_generator import PointCloudGenerator
from utils import *
import shlex


def video_to_image(args):
    """
    Extracts frames from a video and saves them to a specified project directory.

    Parameters:
    - args (list): Command-line arguments passed by the user. Expected arguments:
        - args[1] (str): Path to the input video file.
        - args[2] (str): Path to the project directory where frames will be saved.
        - args[3] (int, optional): Maximum number of frames to extract (default is 100).
        - args[4] (int, optional): Maximum allowed overlap percentage between frames (default is 6).
        - args[5] (float, optional): SSIM threshold to determine frame similarity (default is 0.95).

    Returns:
    - int: Status code (2 for help message, 1 for error, None for success).

    This function extracts optimal frames from a video based on structural similarity (SSIM)
    and overlap criteria and saves them in the specified project directory.
    It provides flexibility in adjusting the number of frames, overlap percentage, and SSIM threshold.

    Note:
    - To display help, use `-h` or `-help` as the second argument.
    - Requires the `video_to_images_generator`, `user_manual`, and `utils` modules.
    """
    if len(args) == 2 and (args[1] == "-h" or args[1] == "-help"):
        help_to_string("v2i_help")
        return 2

    elif len(args) < 3:
        print_err("Please provide the video path and project path.")
        return 1

    video_path = args[1]
    output_path = f"{args[2]}\\images"
    max_frames = 100
    max_overlap_percentage = 6
    ssim_threshold = 0.95

    if len(args) > 3 and args[3] is not None:
        max_frames = int(args[3])
    if len(args) > 4 and args[4] is not None:
        max_overlap_percentage = int(args[4])
    if len(args) > 5 and args[5] is not None:
        ssim_threshold = float(args[5])

    extracted_frames = extract_frames(video_path, output_path, max_frames, max_overlap_percentage,
                                      ssim_threshold)


def generate_point_cloud(args):
    """
    Generates a point cloud from images in a specified project directory.

    Parameters:
    - args (list): Command-line arguments passed by the user. Expected arguments:
        - args[1] (str): Path to the project directory containing the 'images' folder.

    Returns:
    - int: Status code (2 for help message, 1 for error, None for success).

    This function generates a point cloud from the images located in the specified project directory.
    It requires that the directory contains a folder named 'images'.

    Note:
    - To display help, use `-h` or `-help` as the second argument.
    - Requires the `point_cloud_generator` and `user_manual` modules.
    """
    if len(args) == 2 and (args[1] == "-h" or args[1] == "-help"):
        help_to_string("gpc_help")
        return 2

    elif len(args) < 2:
        print_err("Please provide the project path (must contain a file named 'images').")
        return 1

    project_path = args[1]
    pcg = PointCloudGenerator(project_path)
    pcg.run()


def combine_point_clouds(args):
    """
    Combines two point clouds using ICP alignment and saves the merged result.

    Parameters:
    - args (list): Command-line arguments passed by the user. Expected arguments:
        - args[1] (str): Path to the first point cloud file.
        - args[2] (str): Path to the second point cloud file.
        - args[3] (str): Path to save the merged point cloud.

    Returns:
    - int: Status code (2 for help message, 1 for error, None for success).

    This function combines two point clouds by aligning them using Iterative Closest Point (ICP)
    and then merging them. The merged cloud is saved in the specified output file.

    Note:
    - To display help, use `-h` or `-help` as the second argument.
    - Requires `pyCloudCompare` and `user_manual` modules.
    """
    if len(args) == 2 and (args[1] == "-h" or args[1] == "-help"):
        help_to_string("cpc_help")
        return 2

    elif len(args) < 3:
        print_err("Please provide paths to two point clouds.")
        return 1

    elif len(args) < 4:
        print_err("Please provide path to output cloud file.")
        return 1

    # Remove '.ply' extension if present
    output_file = args[3]
    if output_file.lower().endswith('.ply'):
        output_file = output_file[:-4]

    try:
        cc_cmd = pcc.CloudCompareCLI().new_command()
        #cc_cmd.silent()
        cc_cmd.open(args[1])
        cc_cmd.open(args[2])
        cc_cmd.icp(iter_=10_000, overlap=40)
        cc_cmd.merge_clouds()
        cc_cmd.cloud_export_format(pcc.CLOUD_EXPORT_FORMAT.PLY)
        cc_cmd.save_clouds(output_file)
        print(cc_cmd.to_cmd())
        if cc_cmd.execute() == 0:
            print("Point clouds merged successfully.")
        else:
            print_err("Failed to merge point clouds.")

    except Exception as e:
        print_err(e)


def cli(cmd):
    """
    Command-line interface (CLI) for executing video and point cloud processing tasks.

    Parameters:
    - cmd (str): The command string entered by the user.

    This function processes user commands and calls the appropriate function based on the input.
    It supports video frame extraction, point cloud generation, and point cloud combination.

    Commands:
    - `video2images`, `v2i`: Extracts frames from a video.
    - `generatePointCloud`, `gpc`: Generates a point cloud from images.
    - `combinePointClouds`, `cpc`: Combines two point clouds.
    - `-h`, `-help`: Displays help information.
    - `-e`, `-stop`, `-quit`, `-exit`: Exits the CLI.
    """

    cmd = cmd.strip()
    args = shlex.split(cmd)

    if cmd == "":
        pass

    elif cmd in ['-h', '-help']:
        help_to_string()

    elif cmd in ['-e', '-stop', '-quit', '-exit']:
        return 0

    elif args[0] in ['video2images', 'v2i']:
        video_to_image(args)

    elif args[0] in ['generatePointCloud', 'gpc']:
        generate_point_cloud(args)

    elif args[0] in ['combinePointClouds', 'cpc']:
        combine_point_clouds(args)

    else:
        print_err("Invalid command, type \033[35m-help\033[0m to read the user manual.")
