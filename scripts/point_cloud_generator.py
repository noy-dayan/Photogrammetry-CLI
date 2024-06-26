import math
import os
import os.path
import time
import pyCloudCompare as pcc
from pathlib import Path
from utils import *


class PointCloudGenerator:
    """
    A class for generating a point cloud from a set of images using AliceVision and CloudCompare.

    Parameters:
    - project_path (str): The path to the project directory.

    Attributes:
    - cc_cli (pyCloudCompare.CloudCompareCLI): Instance of CloudCompare CLI for point cloud operations.
    - project_path (str): Path to the project directory.
    - image_dir_path (str): Path to the directory containing images.
    - bin_path (str): Path to AliceVision binaries.
    - num_of_images (int): Number of images in the image directory.
    - verboseLevel (str): Verbosity level for AliceVision logging.

    Methods:
    - silent_mkdir(dir): Creates a directory if it doesn't exist silently.
    - run_1_cameraInit(): Runs camera initialization using AliceVision.
    - run_2_featureExtraction(imagesPerGroup=40): Runs feature extraction from images.
    - run_3_imageMatching(): Matches images based on features.
    - run_4_featureMatching(imagesPerGroup=20): Matches features between images.
    - run_5_structureFromMotion(): Reconstructs the structure from motion.
    - run_6_prepareDenseScene(): Prepares a dense scene for depth mapping.
    - run_7_depthMap(groupSize=6, downscale=2): Generates depth maps from images.
    - run_8_depthMapFilter(): Filters the generated depth maps.
    - run_9_meshing(maxInputPoints=50000000, maxPoints=1000000): Generates a mesh from depth maps.
    - run_10_meshFiltering(keepLargestMeshOnly="True"): Filters the generated mesh.
    - run_11_meshDecimate(simplificationFactor=0.8, maxVertices=15000): Decimates the mesh.
    - run_12_meshResampling(simplificationFactor=0.8, maxVertices=15000): Resamples the mesh.
    - run_13_texturing(textureSide=4096, downscale=4, unwrapMethod="Basic"): Applies texturing to the mesh.
    - convert_mesh_to_point_cloud(method="POINTS", parameter=2000000): Converts the final mesh to a point cloud.
    - run(): Runs all tasks sequentially and converts the final mesh to a point cloud.

    Usage:
    Initialize with a project path, then call `run()` to execute the pipeline.
    """

    def __init__(self, project_path):
        """
        Initialize the PointCloudGenerator instance.

        Parameters:
        - project_path (str): The path to the project directory.
        """
        # Initialize CloudCompare CLI for later use
        self.cc_cli = pcc.CloudCompareCLI()

        # Set the project path
        self.project_path = project_path
        # Set the path for the image directory within the project path
        self.image_dir_path = f"{self.project_path}\\images"
        # Set the path for AliceVision binary files
        self.bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aliceVision", "bin"))
        # Calculate the number of images in the image directory
        self.num_of_images = len([name for name in os.listdir(self.image_dir_path) if os.path.isfile(
            os.path.join(self.image_dir_path, name))])  # Number of images to process

        # Set the verbosity level for logging
        self.verboseLevel = "\"error\""  # Detail of the logs (error, info, etc.)

    @staticmethod
    def silent_mkdir(dir_str):
        """
        Create a directory if it doesn't exist.

        Parameters:
        - dir_str (str): Directory path.
        """
        # Function to create a directory if it doesn't exist
        try:
            os.mkdir(dir_str)
        except:
            pass  # Ignore errors if the directory already exists

    def run_1_cameraInit(self):
        """
        Task for camera initialization using AliceVision.

        This function initializes the camera parameters using AliceVision's cameraInit tool.
        It reads images from the specified image directory, matches them with camera sensors,
        and outputs a camera initialization file (cameraInit.sfm).

        Command line execution:
        - AliceVision cameraInit tool
        """
        task = "\\tasks\\1_CameraInit"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 1/13 CAMERA INITIALIZATION ════════════════════════════════\033[0m")

        imageFolder = f"\"{self.image_dir_path}\""
        sensorDatabase = f"\"{str(Path(self.bin_path).parent)}\\share\\aliceVision\\cameraSensors.db\""  # Path to the sensors database, might change in later versions of meshrrom
        output = f"\"{self.project_path + task}\\cameraInit.sfm\""

        # Command line for camera initialization using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_cameraInit.exe "
                    f"--imageFolder {imageFolder} "
                    f"--sensorDatabase {sensorDatabase} "
                    f"--output {output} "
                    "--defaultFieldOfView 45 "
                    "--allowSingleView 1 "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_2_featureExtraction(self, imagesPerGroup=40):
        """
        Task for feature extraction using AliceVision.

        Parameters:
        - imagesPerGroup (int): Number of images processed per group.

        This function extracts features from images using AliceVision's featureExtraction tool.
        It takes the camera initialization file generated in the previous step and computes
        features for each image.

        It processes images in batches based on the provided imagesPerGroup parameter, reducing
        memory usage and optimizing performance.

        Command line execution:
        - AliceVision featureExtraction tool
        """
        task = "\\tasks\\2_FeatureExtraction"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 2/13 FEATURE EXTRACTION ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\""

        # Command line for feature extraction using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_featureExtraction "
                    f"--input {_input} "
                    f"--output {output} "
                    "--forceCpuExtraction 1")

        # When there are more than 40 images, send them in groups
        if self.num_of_images > imagesPerGroup:
            numberOfGroups = int(math.ceil(self.num_of_images / imagesPerGroup))
            for i in range(numberOfGroups):
                cmd = f"{cmd_line} --rangeStart {i * imagesPerGroup} --rangeSize {imagesPerGroup} "
                print(f"------- group {i + 1} / {numberOfGroups} --------")
                print(cmd)
                os.system(cmd)

        else:
            print(cmd_line)
            os.system(cmd_line)

    def run_3_imageMatching(self):
        """
        Task for image matching using AliceVision.

        This function matches images based on extracted features using AliceVision's imageMatching tool.
        It takes the camera initialization file and feature extraction results to generate image matches.

        Command line execution:
        - AliceVision imageMatching tool
        """
        task = "\\tasks\\3_ImageMatching"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 3/13 IMAGE MATCHING ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_FeatureExtraction\""
        output = f"\"{self.project_path + task}\\imageMatches.txt\""

        # Command line for image matching using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_imageMatching.exe "
                    f"--input {_input} "
                    f"--featuresFolders {featuresFolders} "
                    f"--output {output} "
                    f"--tree \"{str(Path(self.bin_path).parent)}\\share\\aliceVision\\vlfeat_K80L3.SIFT.tree\" "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_4_featureMatching(self, imagesPerGroup=20):
        """
        Task for feature matching using AliceVision.

        Parameters:
        - imagesPerGroup (int): Number of images processed per group.

        This function performs feature matching between images using AliceVision's featureMatching tool.
        It uses the camera initialization file, feature extraction results, and image matches to compute
        geometrically consistent correspondences.

        It processes images in batches based on the provided imagesPerGroup parameter to optimize performance.

        Command line execution:
        - AliceVision featureMatching tool
        """
        task = "\\tasks\\4_featureMatching"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 4/13 FEATURE MATCHING ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_FeatureExtraction\""
        imagePairsList = f"\"{self.project_path}\\tasks\\3_ImageMatching\\imageMatches.txt\""

        # Command line for feature matching using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_featureMatching.exe "
                    f"--input {_input} "
                    f"--featuresFolders {featuresFolders} "
                    f"--output {output} "
                    f"--imagePairsList {imagePairsList} "
                    "--knownPosesGeometricErrorMax 5 "
                    f"--verboseLevel {self.verboseLevel} "
                    "--describerTypes sift "
                    "--photometricMatchingMethod ANN_L2 "
                    "--geometricEstimator acransac "
                    "--geometricFilterType fundamental_matrix "
                    "--distanceRatio 0.8 "
                    "--maxIteration 2048 "
                    "--geometricError 0.0 "
                    "--maxMatches 0 "
                    "--savePutativeMatches False "
                    "--guidedMatching False "
                    "--matchFromKnownCameraPoses False "
                    "--exportDebugFiles True")

        # When there are more than 20 images, send them in groups
        if self.num_of_images > imagesPerGroup:
            numberOfGroups = math.ceil(self.num_of_images / imagesPerGroup)
            for i in range(numberOfGroups):
                cmd = f"{cmd_line} --rangeStart {i * imagesPerGroup} --rangeSize {imagesPerGroup} "
                print(f"------- group {i} / {numberOfGroups} --------")
                print(cmd)
                os.system(cmd)

        else:
            print(cmd_line)
            os.system(cmd_line)

    def run_5_structureFromMotion(self):
        """
        Task for structure from motion using AliceVision.

        This function reconstructs the 3D structure from images using AliceVision's incrementalSfm tool.
        It uses the camera initialization file, feature extraction, and feature matching results to compute
        camera poses and sparse point clouds.

        Command line execution:
        - AliceVision incrementalSfm tool
        """
        task = "\\tasks\\5_structureFromMotion"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 5/13 STRUCTURE FROM MOTION ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\\sfm.abc\""
        outputViewsAndPoses = f"\"{self.project_path + task}\\cameras.sfm\""
        extraInfoFolder = f"\"{self.project_path + task}\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_FeatureExtraction\""
        matchesFolders = f"\"{self.project_path}\\tasks\\4_featureMatching\""

        # Command line for structure from motion using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_incrementalSfm.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--outputViewsAndPoses {outputViewsAndPoses} "
                    f"--extraInfoFolder {extraInfoFolder} "
                    f"--featuresFolders {featuresFolders} "
                    f"--matchesFolders {matchesFolders} "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_6_prepareDenseScene(self):
        """
        Task for preparing a dense scene using AliceVision.

        This function prepares a dense scene for depth map estimation using AliceVision's prepareDenseScene tool.
        It uses the camera poses and sparse point clouds generated from the structure from motion step.

        Command line execution:
        - AliceVision prepareDenseScene tool
        """
        task = "\\tasks\\6_PrepareDenseScene"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 6/13 PREPARE DENSE SCENE ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\""

        # Command line for preparing a dense scene using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_prepareDenseScene.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_7_depthMap(self, groupSize=6, downscale=2):
        """
        Task for generating a depth map using AliceVision.

        Parameters:
        - groupSize (int): Number of images processed per batch.
        - downscale (int): Factor to downscale the images.

        This function generates depth maps using AliceVision's depthMapEstimation tool.
        It processes the structure from motion (SfM) results and prepares dense scenes
        for depth map estimation.

        It iterates over batches of images based on the provided group size, generating
        depth maps for each batch. The downscale parameter controls the level of image
        downsampling to reduce processing time and memory usage.

        Command line execution:
        - AliceVision depthMapEstimation tool
        """
        task = "\\tasks\\7_DepthMap"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 7/13 DEPTH MAP ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\""
        imagesFolder = f"\"{self.project_path}\\tasks\\6_PrepareDenseScene\""

        # Command line for generating a depth map using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_depthMapEstimation.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--imagesFolder {imagesFolder} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--downscale {str(downscale)}")

        numberOfBatches = int(math.ceil(self.num_of_images / groupSize))

        for i in range(numberOfBatches):
            groupStart = groupSize * i
            currentGroupSize = min(groupSize, self.num_of_images - groupStart)
            if groupSize > 1:
                print(f"DepthMap Group {i} of {numberOfBatches} : {groupStart} to {currentGroupSize}")
                cmd = f"{cmd_line} --rangeStart {str(groupStart)} --rangeSize {str(groupSize)}"
                print(cmd)
                os.system(cmd)

    def run_8_depthMapFilter(self):
        """
        Task for filtering depth maps using AliceVision.

        This function filters depth maps to refine the quality using AliceVision's depthMapFilter tool.
        It takes the generated depth maps and applies filtering techniques to enhance accuracy.

        Command line execution:
        - AliceVision depthMapFilter tool
        """
        task = "\\tasks\\8_DepthMapFilter"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 8/13 DEPTH MAP FILTER ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\""
        depthMapsFolder = f"\"{self.project_path}\\tasks\\7_DepthMap\""

        # Command line for filtering the depth map using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_depthMapFiltering.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--depthMapsFolder {depthMapsFolder} "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_9_meshing(self, maxInputPoints=50000000, maxPoints=1000000):
        """
        Task for meshing using AliceVision.

        Parameters:
        - maxInputPoints (int): Maximum number of input points.
        - maxPoints (int): Maximum number of output points.

        This function generates a mesh from dense point cloud data using AliceVision's meshing tool.
        It takes the structure from motion (SfM) results and depth maps, producing a 3D mesh representation
        of the scene.

        Command line execution:
        - AliceVision meshing tool
        """
        task = "\\tasks\\9_Meshing"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 9/13 MESHING ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\\densePointCloud.abc\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""
        depthMapsFolder = f"\"{self.project_path}\\tasks\\8_DepthMapFilter\""

        # Command line for meshing using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_meshing.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--outputMesh {outputMesh} "
                    f"--depthMapsFolder {depthMapsFolder} "
                    f"--maxInputPoints {str(maxInputPoints)} "
                    f"--maxPoints {str(maxPoints)} "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_10_meshFiltering(self, keepLargestMeshOnly="True"):
        """
        Task for filtering mesh using AliceVision.

        Parameters:
        - keepLargestMeshOnly (str): Whether to keep only the largest mesh.

        This function filters the generated mesh to refine its quality using AliceVision's meshFiltering tool.
        It applies various techniques to optimize the mesh structure and reduce noise.

        Command line execution:
        - AliceVision meshFiltering tool
        """
        task = "\\tasks\\10_MeshFiltering"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 10/13 MESH FILTERING ════════════════════════════════\033[0m")
        inputMesh = f"\"{self.project_path}\\tasks\\9_Meshing\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        # Command line for filtering the mesh using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_meshFiltering.exe "
                    f"--inputMesh {inputMesh} "
                    f"--outputMesh {outputMesh} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--keepLargestMeshOnly {keepLargestMeshOnly}")

        print(cmd_line)
        os.system(cmd_line)

    def run_11_meshDecimate(self, simplificationFactor=0.8, maxVertices=15000):
        """
        Task for mesh decimation using AliceVision.

        Parameters:
        - simplificationFactor (float): Factor to simplify the mesh.
        - maxVertices (int): Maximum number of vertices in the output mesh.

        This function reduces the complexity of the mesh using AliceVision's meshDecimation tool.
        It downsamples the mesh vertices while preserving its overall shape and structure.

        Command line execution:
        - AliceVision meshDecimation tool
        """
        task = "\\tasks\\11_MeshDecimate"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 11/13 MESH DECIMATE ════════════════════════════════\033[0m")
        inputMesh = f"\"{self.project_path}\\tasks\\10_MeshFiltering\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        # Command line for decimating the mesh using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_meshDecimate.exe "
                    f"--input {inputMesh} "
                    f"--output {outputMesh} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--simplificationFactor {str(simplificationFactor)} "
                    f"--maxVertices {str(maxVertices)}")

        print(cmd_line)
        os.system(cmd_line)

    def run_12_meshResampling(self, simplificationFactor=0.8, maxVertices=15000):
        """
        Task for mesh resampling using AliceVision.

        Parameters:
        - simplificationFactor (float): Factor to simplify the mesh.
        - maxVertices (int): Maximum number of vertices in the output mesh.

        This function resamples the mesh to achieve a desired resolution using AliceVision's meshResampling tool.

        Command line execution:
        - AliceVision meshResampling tool
        """
        task = "\\tasks\\12_MeshResampling"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 12/13 MESH RESAMPLING ════════════════════════════════\033[0m")
        inputMesh = f"\"{self.project_path}\\tasks\\11_MeshDecimate\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        # Command line for resampling the mesh using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_meshResampling.exe "
                    f"--input {inputMesh} "
                    f"--output {outputMesh} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--simplificationFactor {str(simplificationFactor)} "
                    f"--maxVertices {str(maxVertices)}")

        print(cmd_line)
        os.system(cmd_line)

    def run_13_texturing(self, textureSide=4096, downscale=4, unwrapMethod="Basic"):
        """
        Task for mesh texturing using AliceVision.

        Parameters:
        - textureSide (int): Size of the texture.
        - downscale (int): Factor to downscale the texture images.
        - unwrapMethod (str): Method for UV unwrapping.

        This function applies textures to the mesh using AliceVision's meshTexturing tool.
        It uses the original images and the reconstructed mesh to create a textured 3D model.

        Command line execution:
        - AliceVision meshTexturing tool
        """
        task = "\\tasks\\13_Texturing"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 13/13 TEXTURING ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\9_Meshing\\densePointCloud.abc\""
        imagesFolder = f"\"{self.project_path}\\tasks\\6_PrepareDenseScene" "\""
        inputMesh = f"\"{self.project_path}\\tasks\\12_MeshResampling\\mesh.obj\""
        output = f"\"{self.project_path + task}\""

        # Command line for texturing the mesh using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_texturing.exe "
                    f"--input {_input} "
                    f"--inputMesh {inputMesh} "
                    f"--output {output} "
                    f"--imagesFolder {imagesFolder} "
                    f"--textureSide {str(textureSide)} "
                    f"--downscale {str(downscale)} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--unwrapMethod {unwrapMethod}")

        print(cmd_line)
        os.system(cmd_line)

    def convert_mesh_to_point_cloud(self, method="POINTS", parameter=2000000):
        """
        Convert a textured mesh to a point cloud using CloudCompare.

        Parameters:
        - method (str): Method for sampling the mesh ('POINTS' or 'DENSITY').
            POINTS: the corresponding number of points
            DENSITY: the corresponding surface density
        - parameter (int): Number of points to sample from the mesh.

        This function uses CloudCompare's command line interface to sample a textured mesh
        and export it as a point cloud in PLY format.

        Command line execution:
        - CloudCompare command line tool
        """
        model_path = f"{self.project_path}\\tasks\\13_Texturing\\texturedMesh.obj"
        output_path = f"{self.project_path}\\{os.path.basename(self.project_path)}.ply"

        try:
            cmd = self.cc_cli.new_command()
            cmd.open(model_path)  # Open the textured mesh
            cmd.sample_mesh(method, parameter)  # Sample the mesh to generate a point cloud
            cmd.cloud_export_format(pcc.CLOUD_EXPORT_FORMAT.PLY)  # Set the output format to PLY
            cmd.save_clouds(output_path)  # Save the point cloud to the specified output path
            cmd.execute()  # Execute the command
            cmd.clear()  # Clear the command queue

            print(f"Mesh sampled from .obj to .ply")
            return output_path
        except Exception as e:
            print_err(f"Failed to generate .ply from .obj: {e}")
            return ""

    def run(self):
        """
        Main function to execute all the tasks in sequence.

        This function orchestrates the execution of multiple tasks in sequence:
        camera initialization, feature extraction, image matching, structure from motion,
        dense scene preparation, depth map generation and filtering, meshing, mesh filtering,
        mesh decimation, mesh resampling, mesh texturing, and finally conversion of the textured
        mesh to a point cloud.
        """
        PointCloudGenerator.silent_mkdir(f"{self.project_path}\\tasks")

        # Run all the tasks in sequence
        startTime = time.time()

        self.run_1_cameraInit()
        self.run_2_featureExtraction()
        self.run_3_imageMatching()
        self.run_4_featureMatching()
        self.run_5_structureFromMotion()
        self.run_6_prepareDenseScene()
        self.run_7_depthMap()
        self.run_8_depthMapFilter()
        self.run_9_meshing()
        self.run_10_meshFiltering()
        self.run_11_meshDecimate()
        self.run_12_meshResampling()
        self.run_13_texturing()

        # Convert the final mesh to a point cloud
        point_cloud_path = self.convert_mesh_to_point_cloud()

        endTime = time.time()
        hours, rem = divmod(endTime - startTime, 3600)
        minutes, seconds = divmod(rem, 60)

        print("\033[35m════════════════════════════════ DONE ════════════════════════════════\033[0m")
        print("\033[35mTime elapsed: \033[0m" + "\033[32m{:0>2}:{:0>2}:{:05.2f}\033[0m".format(int(hours), int(minutes),
                                                                                               seconds))
        if point_cloud_path != "":
            print(f"\033[35mPoint cloud successfully generated and saved at \033[32m'{point_cloud_path}'\033[0m")
        print("\033[35m══════════════════════════════════════════════════════════════════════\033[0m")
