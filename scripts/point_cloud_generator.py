import math
import os
import os.path
import time
from pathlib import Path
import pyCloudCompare as pcc


class PointCloudGenerator:
    def __init__(self, project_path):
        self.cc_cli = pcc.CloudCompareCLI()

        self.project_path = project_path  # --> path of the project directory
        self.image_dir_path = f"{self.project_path}\\images"  # --> directory containing the images
        self.bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aliceVision", "bin")) # --> path of the binary files from aliceVision
        self.num_of_images = len([name for name in os.listdir(self.image_dir_path) if os.path.isfile(
            os.path.join(self.image_dir_path, name))])  # --> number of images to process

        self.verboseLevel = "\"error\""  # detail of the logs (error, info, etc)

    @staticmethod
    def silent_mkdir(dir):  # function to create a directory
        try:
            os.mkdir(dir)
        except:
            pass
        return 0

    def run_1_cameraInit(self):
        task = "\\tasks\\1_CameraInit"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 1/13 CAMERA INITIALIZATION -----------------------")

        imageFolder = f"\"{self.image_dir_path}\""
        sensorDatabase = f"\"{str(Path(self.bin_path).parent)}\\share\\aliceVision\\cameraSensors.db\""  # Path to the sensors database, might change in later versions of meshrrom
        output = f"\"{self.project_path + task}\\cameraInit.sfm\""

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
        task = "\\tasks\\2_FeatureExtraction"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 2/13 FEATURE EXTRACTION -----------------------")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\""

        cmd_line = (f"{self.bin_path}\\aliceVision_featureExtraction "
                    f"--input {_input} "
                    f"--output {output} "
                    "--forceCpuExtraction 1")

        # when there are more than 40 images, it is good to send them in groups
        if (self.num_of_images > imagesPerGroup):
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
        task = "\\tasks\\3_ImageMatching"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 3/13 IMAGE MATCHING -----------------------")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_FeatureExtraction\""
        output = f"\"{self.project_path + task}\\imageMatches.txt\""

        cmd_line = (f"{self.bin_path}\\aliceVision_imageMatching.exe "
                    f"--input {_input} "
                    f"--featuresFolders {featuresFolders} "
                    f"--output {output} "
                    f"--tree \"{str(Path(self.bin_path).parent)}\\share\\aliceVision\\vlfeat_K80L3.SIFT.tree\" "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_4_featureMatching(self, imagesPerGroup=20):
        task = "\\tasks\\4_featureMatching"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 4/13 FEATURE MATCHING -----------------------")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_FeatureExtraction\""
        imagePairsList = f"\"{self.project_path}\\tasks\\3_ImageMatching\\imageMatches.txt\""

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

        # when there are more than 20 images, it is good to send them in groups
        if (self.num_of_images > imagesPerGroup):
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
        task = "\\tasks\\5_structureFromMotion"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 5/13 STRUCTURE FROM MOTION -----------------------")

        _input = f"\"{self.project_path}\\tasks\\1_CameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\\sfm.abc\""
        outputViewsAndPoses = f"\"{self.project_path + task}\\cameras.sfm\""
        extraInfoFolder = f"\"{self.project_path + task}\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_FeatureExtraction\""
        matchesFolders = f"\"{self.project_path}\\tasks\\4_featureMatching\""

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
        task = "\\tasks\\6_PrepareDenseScene"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 6/13 PREPARE DENSE SCENE -----------------------")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\""

        cmd_line = (f"{self.bin_path}\\aliceVision_prepareDenseScene.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_7_depthMap(self, groupSize=6, downscale=2):
        task = "\\tasks\\7_DepthMap"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 7/13 DEPTH MAP -----------------------")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\""
        imagesFolder = f"\"{self.project_path}\\tasks\\6_PrepareDenseScene\""

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
        task = "\\tasks\\8_DepthMapFilter"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 8/13 DEPTH MAP FILTER-----------------------")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\""
        depthMapsFolder = f"\"{self.project_path}\\tasks\\7_DepthMap\""

        cmd_line = (f"{self.bin_path}\\aliceVision_depthMapFiltering.exe "
                    f"--input {_input} "
                    f"--output {output} "
                    f"--depthMapsFolder {depthMapsFolder} "
                    f"--verboseLevel {self.verboseLevel}")

        print(cmd_line)
        os.system(cmd_line)

    def run_9_meshing(self, maxInputPoints=50000000, maxPoints=1000000):
        task = "\\tasks\\9_Meshing"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 9/13 MESHING -----------------------")
        _input = f"\"{self.project_path}\\tasks\\5_structureFromMotion\\sfm.abc\""
        output = f"\"{self.project_path + task}\\densePointCloud.abc\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""
        depthMapsFolder = f"\"{self.project_path}\\tasks\\8_DepthMapFilter\""

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
        task = "\\tasks\\10_MeshFiltering"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 10/13 MESH FILTERING -----------------------")
        inputMesh = f"\"{self.project_path}\\tasks\\9_Meshing\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        cmd_line = (f"{self.bin_path}\\aliceVision_meshFiltering.exe "
                    f"--inputMesh {inputMesh} "
                    f"--outputMesh {outputMesh} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--keepLargestMeshOnly {keepLargestMeshOnly}")

        print(cmd_line)
        os.system(cmd_line)

    def run_11_meshDecimate(self, simplificationFactor=0.8, maxVertices=15000):
        task = "\\tasks\\11_MeshDecimate"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 11/13 MESH DECIMATE -----------------------")
        inputMesh = f"\"{self.project_path}\\tasks\\10_MeshFiltering\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        cmd_line = (f"{self.bin_path}\\aliceVision_meshDecimate.exe "
                    f"--input {inputMesh} "
                    f"--output {outputMesh} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--simplificationFactor {str(simplificationFactor)} "
                    f"--maxVertices {str(maxVertices)}")

        print(cmd_line)
        os.system(cmd_line)

    def run_12_meshResampling(self, simplificationFactor=0.8, maxVertices=15000):
        task = "\\tasks\\12_MeshResampling"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 12/13 MESH RESAMPLING -----------------------")
        inputMesh = f"\"{self.project_path}\\tasks\\11_MeshDecimate\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        cmd_line = (f"{self.bin_path}\\aliceVision_meshResampling.exe "
                    f"--input {inputMesh} "
                    f"--output {outputMesh} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--simplificationFactor {str(simplificationFactor)} "
                    f"--maxVertices {str(maxVertices)}")

        print(cmd_line)
        os.system(cmd_line)

    def run_13_texturing(self, textureSide=4096, downscale=4, unwrapMethod="Basic"):
        task = "\\tasks\\13_Texturing"
        PointCloudGenerator.silent_mkdir(self.project_path + task)

        print("----------------------- 13/13 TEXTURING  -----------------------")
        _input = f"\"{self.project_path}\\tasks\\9_Meshing\\densePointCloud.abc\""
        imagesFolder = f"\"{self.project_path}\\tasks\\6_PrepareDenseScene" "\""
        inputMesh = f"\"{self.project_path}\\tasks\\12_MeshResampling\\mesh.obj\""
        output = f"\"{self.project_path + task}\""

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
        model_path = f"{self.project_path}\\tasks\\13_Texturing\\texturedMesh.obj"
        output_path = f"{self.project_path}\\{os.path.basename(self.project_path)}.ply"

        cmd = self.cc_cli.new_command()
        cmd.open(model_path)
        cmd.sample_mesh(method, parameter)
        cmd.cloud_export_format(pcc.CLOUD_EXPORT_FORMAT.PLY)
        cmd.save_clouds(output_path)
        cmd.execute()
        cmd.clear()

        print(f"Mesh sampled from .obj to .ply")

    def run(self):
        PointCloudGenerator.silent_mkdir(f"{self.project_path}\\tasks")

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

        self.convert_mesh_to_point_cloud()

        endTime = time.time()
        hours, rem = divmod(endTime - startTime, 3600)
        minutes, seconds = divmod(rem, 60)

        print(
            "═════════════════════════════════════════════════════════ DONE ═════════════════════════════════════════════════════════")
        print("time elapsed: " + "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
        print(
            "════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════")
