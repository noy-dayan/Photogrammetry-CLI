import os
import subprocess
from scripts.video_to_images_generator import extract_frames
from scripts.user_manual import *
from scripts.point_cloud_generator import PointCloudGenerator
import pyCloudCompare as pcc


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
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] {e}")


def run_batch_file_and_command(batch_file, command):
    try:
        # Call the batch file and command directly
        exec_cmd(f'call {batch_file} && {command}')
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {e}")
    except Exception as e:
        print(f"[ERROR] {e}")


def video_to_image(args):
    if len(args) == 2 and (args[1] == "-h" or args[1] == "-help"):
        help_to_string("v2i_help")
        return 2

    elif len(args) < 3:
        print("[ERROR] Please provide the video path and project path.")
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
        print("[ERROR] Please provide the project path (must contain a file named 'images').")
        return 1

    project_path = args[1]
    pcg = PointCloudGenerator(project_path)
    pcg.run()


def combine_point_clouds(args):
    if len(args) == 2 and (args[1] == "-h" or args[1] == "-help"):
        help_to_string("gpc_help")
        return 2

    elif len(args) < 3:
        print("Error: Please provide paths to two point clouds.")
        return 1

    cloud1_path = args[1]
    cloud2_path = args[2]
    output_path = "../combined_cloud.ply"

    # Check if CloudCompare is installed
    #if shutil.which("CloudCompare") is None:
    #print("[ERROR] CloudCompare is not installed or not in the system's PATH.")
    #return 1

    try:

        cc_cli = pcc.CloudCompareCLI()
        cmd = cc_cli.new_command()

        """"
        cmd.open(cloud1_path)  # Read file
        cmd.cloud_export_format(cc.CLOUD_EXPORT_FORMAT.PLY)
        cmd.save_clouds("C:\\Photogrammetry\\meshroom_cli\\tests\\v1\\13_Texturing\\v1.ply")
        cmd.execute()
        cmd.clear()
        cmd.open(cloud2_path)  # Read file
        cmd.cloud_export_format(cc.CLOUD_EXPORT_FORMAT.PLY)
        cmd.save_clouds("C:\\Photogrammetry\\meshroom_cli\\tests\\v2\\13_Texturing\\v2.ply")
        cmd.execute()
        cmd.clear()
        """
        cmd.open("../tests/v1/v1.ply")
        cmd.open("../tests/v2/v2.ply")
        cmd.icp()
        cmd.merge_clouds()
        cmd.cloud_export_format(pcc.CLOUD_EXPORT_FORMAT.PLY)
        cmd.save_clouds(output_path)
        print(cmd)
        #cmd.execute()

        from simpleicp import PointCloud, SimpleICP
        import numpy as np

        # Read point clouds from xyz files into n-by-3 numpy arrays
        X_fix = np.genfromtxt("../tests/v1/v1.xyz")
        X_mov = np.genfromtxt("../tests/v1/v2.xyz")

        # Create point cloud objects
        pc_fix = PointCloud(X_fix, columns=["x", "y", "z"])
        pc_mov = PointCloud(X_mov, columns=["x", "y", "z"])

        # Create simpleICP object, add point clouds, and run algorithm!
        icp = SimpleICP()
        icp.add_point_clouds(pc_fix, pc_mov)
        H, X_mov_transformed, rigid_body_transformation_params, distance_residuals = icp.run(max_overlap_distance=1)
        print(H, X_mov_transformed, rigid_body_transformation_params, distance_residuals)
        #cmd = f"\"C:\Program Files\CloudCompare\CloudCompare.exe\" -O {cloud1_path} -O {cloud2_path} -ICP -MERGE_CLOUDS -SAVE_CLOUDS {output_path}"
        #exec_cmd(cmd)
        #print(f"Combined point cloud saved to {output_path}")

    except Exception as e:
        print(e)


def cli(cmd):
    cmd = cmd.strip()
    args = cmd.split(" ")
    if cmd == '-h' or cmd == '-help':
        help_to_string()

    elif cmd == 'stop' or cmd == 'quit' or cmd == 'exit':
        return 0

    elif args[0] == 'video2images' or args[0] == 'v2i':
        video_to_image(args)

    elif args[0] == 'generatePointCloud' or args[0] == 'gpc':
        generate_point_cloud(args)

    elif args[0] == 'combinePointClouds' or args[0] == 'cpc':
        combine_point_clouds(args)

    else:
        print("Invalid command, type -help for viewing the user manual.")



