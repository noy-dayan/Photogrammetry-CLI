def intro_to_string():
    print("""\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
    
    ██████╗ ██╗  ██╗ ██████╗ ████████╗ ██████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗███╗   ███╗███████╗████████╗██████╗ ██╗   ██╗     ██████╗██╗     ██╗
    ██╔══██╗██║  ██║██╔═══██╗╚══██╔══╝██╔═══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║████╗ ████║██╔════╝╚══██╔══╝██╔══██╗╚██╗ ██╔╝    ██╔════╝██║     ██║
    ██████╔╝███████║██║   ██║   ██║   ██║   ██║██║  ███╗██████╔╝███████║██╔████╔██║██╔████╔██║█████╗     ██║   ██████╔╝ ╚████╔╝     ██║     ██║     ██║
    ██╔═══╝ ██╔══██║██║   ██║   ██║   ██║   ██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝     ██║   ██╔══██╗  ╚██╔╝      ██║     ██║     ██║
    ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗   ██║   ██║  ██║   ██║       ╚██████╗███████╗██║
    ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝        ╚═════╝╚══════╝╚═╝
    \033[0m
    Type \033[35m-help\033[0m for more information abot the available commands.
    Type \033[31m-exit\033[0m to close the program.
\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m""")


def v2i_help():
    print("""\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m
    \033[35mUsage:\033[0m video2images (or v2i) \033[32m<video_path (must be in .mp4 format)> <project_path (creates a file named 'images' inside)>\033[0m \033[36m[max_frames] [max_overlap_percentage] [ssim_threshold]\033[0m
    
    \033[35mDescription:\033[0m
    Extract frames from a video file and save them as images.
    
    \033[35mArguments:\033[0m
    \033[32m<video_path>\033[0m: Path to the input video file in .mp4 format.
    \033[32m<project_path>\033[0m: Path to the project folder where the images will be saved in a folder named 'images'.
    \033[36m[max_frames]\033[0m: Maximum number of frames to extract from the video (default: 100).
    \033[36m[max_overlap_percentage]\033[0m: Maximum percentage of overlap allowed between frames (default: 6).
    \033[36m[ssim_threshold]\033[0m: SSIM threshold for frame similarity (default: 0.95).
          
    \033[35mExample:\033[0m
    video2images \033[32mpath\\video.mp4 path\\project\\dir\033[0m \033[36m200 5 0.92\033[0m
\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m""")


def gpc_help():
    print("""\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m
    \033[35mUsage:\033[0m generatePointCloud (or gpc) \033[32m<project_path (must contain a folder named 'images')>\033[0m

    \033[35mDescription:\033[0m
    Generate a point cloud (.ply) from a set of images.

    \033[35mArguments:\033[0m
    \033[32m<project_path>\033[0m: Path to the project folder containing the images folder.

    \033[35mExample:\033[0m
    generatePointCloud \033[32mpath\\project\\dir\033[0m
\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m""")


def cpc_help():
    print("""\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m
    \033[35mUsage:\033[0m combinePointClouds (or cpc) \033[32m<cloud1_path> <cloud2_path>\033[0m

    \033[35mDescription:\033[0m
    Combine two point clouds into a single point cloud using ICP.

    \033[35mArguments:\033[0m
    \033[32m<cloud1_path>\033[0m: Path to the first point cloud file.
    \033[32m<cloud2_path>\033[0m: Path to the second point cloud file.

    \033[35mExample:\033[0m
    cpc \033[32mpath\\cloud1.ply path\\cloud2.ply\033[0m
\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m""")


def general_help():
    print("""\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m
    \033[35mAvailable commands:\033[0m
    \033[35m>\033[0m video2images (or v2i) \033[32m<video_path (must be in .mp4 format)> <project_path (creates a file named 'images' inside)>\033[0m \033[36m[max_frames] [max_overlap_percentage] [ssim_threshold]\033[0m
    \033[35m>\033[0m generatePointCloud (or gpc) \033[32m<project_path (must contain a folder named 'images')>\033[0m
    \033[35m>\033[0m combinePointClouds (or cpc) \033[32m<cloud1_path> <cloud2_path>\033[0m

    To get detailed help for a specific command, Type: \033[32m<command>\033[0m \033[35m-help\033[0m
    Type \033[31m-exit\033[0m to close the program.
\033[35m═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════\033[0m""")


def help_to_string(cmd=""):
    if cmd == "v2i_help":
        v2i_help()
    elif cmd == "gpc_help":
        gpc_help()
    elif cmd == "cpc_help":
        cpc_help()
    else:
        general_help()
