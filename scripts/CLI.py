import os
import subprocess
import pyCloudCompare as pcc
from video_to_images_generator import extract_frames
from user_manual import *
from point_cloud_generator import PointCloudGenerator
from utils import *
import open3d as o3d
import numpy as np
import shlex


def check_admin_permission():
    try:
        # Check for administrative privileges by attempting to create a folder in C:\
        if not os.path.isdir("C:\\TestAdminPermission"):
            os.makedirs("C:\\TestAdminPermission")
        os.rmdir("C:\\TestAdminPermission")
        return True
    except PermissionError:
        return False


def exec_cmd(command):
    try:
        # Use subprocess.Popen to capture output in real time
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for line in process.stdout:
            print(line, end='')
        process.stdout.close()
        process.wait()
        if process.returncode != 0:
            for line in process.stderr:
                print(line, end='')
        process.stderr.close()
    except subprocess.CalledProcessError as e:
        print_err(e)
    except Exception as e:
        print_err(e)


def run_batch_file_and_command(batch_file, command):
    try:
        # Call the batch file and command directly
        exec_cmd(f'call {batch_file} && {command}')
    except subprocess.CalledProcessError as e:
        print_err(e)
    except Exception as e:
        print_err(e)


def video_to_image(args):
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
    if len(args) == 2 and (args[1] == "-h" or args[1] == "-help"):
        help_to_string("cpc_help")
        return 2

    elif len(args) < 3:
        print_err("Please provide paths to two point clouds.")
        return 1

    cloud1_path = args[1]
    cloud2_path = args[2]
    output_path = r"C:\Users\StrikeOver.DESKTOP-HNIMD1Q\Desktop\Photogrammetry-CLI\test\combined_cloud.obj"

    # Check if CloudCompare is installed
    #if shutil.which("CloudCompare") is None:
    #print("[ERROR] CloudCompare is not installed or not in the system's PATH.")
    #return 1

    cc_cmd = pcc.CloudCompareCLI().new_command()
    #cc_cmd.silent()
    cc_cmd.open(cloud1_path)
    cc_cmd.open(cloud2_path)
    cc_cmd.icp(min_error_diff=2, iter_=100, overlap=40, adjust_scale=True)
    #cc_cmd.merge_meshes()
    #cc_cmd.mesh_export_format(pcc.MESH_EXPORT_FORMAT.OBJ)
    cc_cmd.auto_save(on_off=True)
    #cc_cmd.save_meshes(output_path)
    cc_cmd.execute()


def cli(cmd):
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
