def intro_to_string():
    print("""═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    ██████╗ ██╗  ██╗ ██████╗ ████████╗ ██████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗███╗   ███╗███████╗████████╗██████╗ ██╗   ██╗     ██████╗██╗     ██╗
    ██╔══██╗██║  ██║██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║████╗ ████║██╔════╝╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ██╔════╝██║     ██║
    ██████╔╝███████║██║   ██║   ██║   ██║   ██║██║  ███╗██████╔╝███████║██╔████╔██║██╔████╔██║█████╗     ██║   ██████╔╝ ╚████╔╝     ██║     ██║     ██║
    ██╔═══╝ ██╔══██║██║   ██║   ██║   ██║   ██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██╗  ╚██╔╝      ██║     ██║     ██║
    ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗   ██║   ██║  ██║   ██║       ╚██████╗███████╗██║
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝        ╚═════╝╚══════╝╚═╝
    
    Usage: <command> [arguments]
    Type -help for more information abot the available commands.
    Type -exit to close the program.
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════""")


def v2i_help():
    print("________________________________________________________")
    print("Usage: video2images (or v2i) <video_path (must be in .mp4 format)> <project_path (creates a file named "
          "'images' inside)> [max_frames] [max_overlap_percentage] [ssim_threshold]")
    print("\nDescription:")
    print("Extract frames from a video file and save them as images.")
    print("\nArguments:")
    print("<video_path>: Path to the input video file in .mp4 format.")
    print("<project_path>: Path to the project folder where the images will be saved.")
    print("[max_frames]: Maximum number of frames to extract from the video (default: 100).")
    print("[max_overlap_percentage]: Maximum percentage of overlap allowed between frames (default: 6).")
    print("[ssim_threshold]: SSIM threshold for frame similarity (default: 0.95).")
    print("\nExample:")
    print("video2images video.mp4 project_folder 200 5 0.92")
    print("________________________________________________________")


def gpc_help():
    print("________________________________________________________")
    print("Usage: generatePointCloud (or gpc) <project_path (must contain a file named 'images')>")
    print("\nDescription:")
    print("Generate a point cloud from a set of images.")
    print("\nArguments:")
    print("<project_path>: Path to the project folder containing the images.")
    print("\nExample:")
    print("generatePointCloud project_folder")
    print("________________________________________________________")


def cpc_help():
    print("________________________________________________________")
    print("Usage: combinePointClouds (or cpc) <cloud1_path> <cloud2_path>")
    print("\nDescription:")
    print("Combine two point clouds into a single point cloud.")
    print("\nArguments:")
    print("<cloud1_path>: Path to the first point cloud file.")
    print("<cloud2_path>: Path to the second point cloud file.")
    print("\nExample:")
    print("combinePointClouds cloud1.las cloud2.las")
    print("________________________________________________________")


def general_help():
    print("________________________________________________________")
    print("Usage: <command> [arguments]\n")
    print("Available commands:")
    print("video2images (or v2i) <video_path (must be in .mp4 format)> <project_path (creates a file named "
          "'images' inside)> [max_frames] [max_overlap_percentage] [ssim_threshold]")
    print("generatePointCloud (or gpc) <project_path (must contain a file named 'images')>")
    print("combinePointClouds (or cpc) <cloud1_path> <cloud2_path>\n")
    print("For more details on each command, use: <command> -h")
    print("To exit the program, use: stop")
    print("________________________________________________________")
    print("To get detailed help for a specific command, use: <command> -h")


def help_to_string(cmd=""):
    if cmd == "v2i_help":
        v2i_help()
    elif cmd == "gpc_help":
        gpc_help()
    elif cmd == "cpc_help":
        cpc_help()
    else:
        general_help()
