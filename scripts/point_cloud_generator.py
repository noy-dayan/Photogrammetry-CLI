import math
import os
import os.path
import shlex
import time
import pyCloudCompare as pcc
from pathlib import Path
from utils import *


class PointCloudGenerator:
    """
    A class to handle the process of generating point clouds from images using AliceVision and CloudCompare.

    This class orchestrates the process of:
    1. Camera Initialization
    2. Feature Extraction
    3. Image Matching
    4. Feature Matching
    5. Incremental Structure from Motion (SfM)
    6. Preparing the Dense Scene
    7. Depth Map Estimation
    8. Depth Map Filtering
    9. Meshing
    10. Mesh Filtering
    11. Texturing
    12. Converting the Mesh to a Point Cloud

    Attributes:
    - project_path (str): Path to the project directory.
    - bin_path (str): Path to the directory containing AliceVision binaries.
    - cc_cli (CloudCompareCLI): Instance of the CloudCompare command line interface.
    - verboseLevel (int): Level of verbosity for command line tools.
    - num_of_images (int): Number of images used for processing.

    Methods:
    - run_1_cameraInit: Initializes the camera parameters.
    - run_2_featureExtraction: Extracts features from the images.
    - run_3_imageMatching: Matches features between images.
    - run_4_featureMatching: Matches features between images based on previously matched images.
    - run_5_incrementalSfM: Performs incremental Structure from Motion.
    - run_6_prepareDenseScene: Prepares a dense scene from the SfM output.
    - run_7_depthMapEstimation: Estimates depth maps from the prepared dense scene.
    - run_8_depthMapFiltering: Filters depth maps based on various criteria.
    - run_9_meshing: Creates a mesh from the filtered depth maps.
    - run_10_meshFiltering: Filters the generated mesh to remove unwanted artifacts.
    - run_11_texturing: Applies textures to the filtered mesh.
    - convert_mesh_to_cloud: Converts the textured mesh to a point cloud using CloudCompare.
    - run: Executes the entire pipeline from initialization to point cloud generation.

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

    def run_1_cameraInit(self, allowSingleView=True,
                         defaultFieldOfView=45.0):
        """
        Initializes camera parameters for structure-from-motion (SfM) processing using AliceVision's `cameraInit` tool.

        This method processes image metadata, sensor information, and generates `cameraInit.sfm`. It supports multiple cameras and focal lengths, creating groups of intrinsics based on image metadata.

        Parameters:
        - allowSingleView (bool): Whether to allow single-view cameras (default is True).
        - defaultFieldOfView (float): Empirical value for the default field of view in degrees (default is 45.0).

        Input:
        - Image Folder: Directory containing the input images.
        - Sensor Database: Path to the camera sensor width database.

        Output:
        - Output SfMData File: The file path for the generated camera initialization data (`cameraInit.sfm`).

        Details:
        - The UID for each image is based on metadata. If metadata is missing, the image file path is used as a fallback.
        - If multiple cameras are used, it is important to add corresponding serial numbers to the EXIF data to correctly group images by device.
        """

        task = "\\tasks\\1_cameraInit"
        mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 1/11 CAMERA INITIALIZATION ════════════════════════════════\033[0m")

        imageFolder = f"\"{self.image_dir_path}\""
        sensorDatabase = f"\"{str(Path(self.bin_path).parent)}\\share\\aliceVision\\cameraSensors.db\""
        output = f"\"{self.project_path + task}\\cameraInit.sfm\""

        # Command line for camera initialization using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_cameraInit.exe "
                    f"--imageFolder {imageFolder} "
                    f"--sensorDatabase {sensorDatabase} "
                    f"--allowSingleView {allowSingleView} "
                    f"--lensCorrectionProfileSearchIgnoreCameraModel True "
                    f"--defaultFieldOfView {defaultFieldOfView} "
                    f"--groupCameraFallback folder "
                    f"--rawColorInterpretation LibRawWhiteBalancing "
                    f"--viewIdMethod metadata "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output} ")

        print(cmd_line)
        os.system(cmd_line)

    def run_2_featureExtraction(self, imagesPerGroup=40,
                                forceCpuExtraction=True,
                                describerTypes='dspsift',
                                describerPreset='normal',
                                maxThreads=0):
        """
        Extracts features and descriptors from images using AliceVision's `featureExtraction` tool.

        This method performs feature extraction and descriptor computation from images provided in the SfM data file.
        Features are distinctive points in images that are invariant to transformations like rotation, scaling, and translation.
        The extracted features and descriptors are essential for matching and aligning images in 3D reconstruction tasks.

        Parameters:
        - imagesPerGroup (int): Number of images to process per group. If the number of images exceeds this value, they will be
          processed in batches (default is 40).
        - forceCpuExtraction (bool): If `True`, forces feature extraction to use only the CPU. If `False`, it uses GPU if available (default is `True`).
        - describerTypes (str): Types of descriptors used for feature matching. Options include 'sift', 'sift_float', 'sift_upright',
          'akaze', 'akaze_liop', 'akaze_mldb', 'cctag3', 'cctag4', 'sift_ocv', 'akaze_ocv' (default is 'dspsift').
        - describerPreset (str): Configuration preset for the image describer, affecting feature extraction quality and
          speed (options: 'low', 'medium', 'normal', 'high', 'ultra'; default is 'normal').
        - maxThreads (int): Specifies the maximum number of threads for parallel processing. A value of 0 enables automatic
          thread management. The maximum value is 24 (default is 0).

        Output:
        - Creates feature and descriptor files in the specified output folder. The files are typically saved with extensions such as `.feat` and `.desc`.

        Detailed Description:
        - This step extracts distinctive groups of pixels (features) from images, which are invariant to changes in camera viewpoint
          during image acquisition. The most common feature detection method used is the SIFT (Scale-Invariant Feature Transform) algorithm.
        - SIFT extracts discriminative patches from images that can be compared regardless of rotation, translation, or scale. It works
          by computing a pyramid of downscaled images and finding scale-space maxima, which are then used to create feature descriptors.
        - The `describerTypes` parameter allows specifying different feature detection methods. The `describerPreset` parameter controls
          the quality and computation time of the feature extraction process.

        Notes:
        - If the number of images exceeds `imagesPerGroup`, they are processed in batches. Each batch is processed sequentially.
        - GPU acceleration is available if `forceCpuExtraction` is set to `False` and the system supports CUDA.
        """

        task = "\\tasks\\2_featureExtraction"
        mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 2/11 FEATURE EXTRACTION ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_cameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\""

        # Command line for feature extraction using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_featureExtraction.exe "
                    f"--input {_input} "
                    f"--forceCpuExtraction {forceCpuExtraction} "
                    f"--masksFolder \"\" "
                    f"--maskExtension jpg "
                    f"--maskInvert False "
                    f"--describerTypes {describerTypes} "
                    f"--describerPreset {describerPreset} "
                    f"--describerQuality normal "
                    f"--contrastFiltering GridSort "
                    f"--gridFiltering True "
                    f"--workingColorSpace sRGB "
                    f"--maxThreads {maxThreads} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output}")

        # When there are more than 40 images, send them in groups
        if self.num_of_images > imagesPerGroup:
            numberOfGroups = int(math.ceil(self.num_of_images / imagesPerGroup))
            for i in range(numberOfGroups):
                cmd = f"{cmd_line} --rangeStart {i * imagesPerGroup} --rangeSize {imagesPerGroup} "
                print(f"------- group {i + 1} / {numberOfGroups} --------\n{cmd}")
                os.system(cmd)

        else:
            print(cmd_line)
            os.system(cmd_line)

    def run_3_imageMatching(self, weights='\"\"',
                            minNbImages=200,
                            maxDescriptors=500,
                            nbMatches=40):

        """
        Matches images based on extracted features and descriptors using AliceVision's `imageMatching` tool.

        This step identifies which images in the dataset are suitable for matching with each other. It uses image retrieval techniques
        to find images with shared content efficiently, without having to resolve all feature matches in detail. The goal is to simplify
        the image matching process by creating compact image descriptors that facilitate efficient comparison.

        Parameters:
        - weights (str): Path to the weight file for the vocabulary tree. If not provided, weights will be computed on the database
          built with the provided set (default is '""').
        - minNbImages (int): Minimal number of images required to use the vocabulary tree. If the number of images is below this
          threshold, all possible image pairs will be matched (default is 200).
        - maxDescriptors (int): Limit on the number of descriptors loaded per image. A value of 0 means no limit (default is 500).
        - nbMatches (int): Number of matches to retrieve for each image. A value of 0 retrieves all possible matches (default is 40).

        Output:
        - Creates an output file with a list of selected image pairs that are deemed suitable for matching. The file is saved with the
          name 'imageMatches.txt' in the specified output directory.

        Detailed Description:
        - The goal of this step is to find images that capture overlapping or similar areas of the scene. To achieve this, a vocabulary
          tree approach is used, where extracted feature descriptors are classified and compared to a pre-built tree structure.
        - The vocabulary tree allows efficient image retrieval by representing images with a compact descriptor based on the indices of
          tree leaves. This descriptor helps determine if different images share similar content.
        - If the number of images exceeds `minNbImages`, the vocabulary tree is utilized to perform matching. Otherwise, all possible
          image pairs are matched.

        Notes:
        - The `method` parameter specifies the image matching strategy. The default method combines sequential and vocabulary tree
          approaches for improved matching performance.
        - If the number of images is below the `minNbImages` threshold, the matching process will consider all possible image pairs.
        """
        task = "\\tasks\\3_imageMatching"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 3/11 IMAGE MATCHING ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_cameraInit\\cameraInit.sfm\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_featureExtraction\""
        output = f"\"{self.project_path + task}\\imageMatches.txt\""
        tree = f"\"{str(Path(self.bin_path).parent)}\\share\\aliceVision\\vlfeat_K80L3.SIFT.tree\""

        # Command line for image matching using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_imageMatching.exe "
                    f"--input {_input} "
                    f"--featuresFolders {featuresFolders} "
                    f"--method SequentialAndVocabularyTree "
                    f"--tree {tree} "
                    f"--weights {weights} "
                    f"--minNbImages {minNbImages} "
                    f"--maxDescriptors {maxDescriptors} "
                    f"--nbMatches {nbMatches} "
                    f"--nbNeighbors 5 "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output}")

        print(cmd_line)
        os.system(cmd_line)

    def run_4_featureMatching(self, imagesPerGroup=20,
                              describerTypes='dspsift',
                              photometricMatchingMethod='ANN_L2',
                              geometricEstimator='acransac',
                              geometricFilterType='fundamental_matrix',
                              distanceRatio=0.8,
                              maxIteration=2048,
                              maxMatches=0,
                              savePutativeMatches=False,
                              guidedMatching=False,
                              exportDebugFiles=False):

        """
        Matches features between images using AliceVision's `featureMatching` tool.

        This step identifies correspondences between features of candidate image pairs. It involves both photometric and geometric
        matching techniques to find accurate feature correspondences.

        Parameters:
        - imagesPerGroup (int): Number of images to process per group. When there are more images than this value, the images
          are processed in groups (default is 20).
        - describerTypes (str): Types of descriptors used for feature matching. Options include 'sift', 'sift_float', 'sift_upright',
          'akaze', 'akaze_liop', 'akaze_mldb', 'cctag3', 'cctag4', 'sift_ocv', 'akaze_ocv' (default is 'dspsift').
        - photometricMatchingMethod (str): Method for photometric matching. Options include 'BRUTE_FORCE_L2', 'ANN_L2', 'CASCADE_HASHING_L2',
          'FAST_CASCADE_HASHING_L2' for scalar descriptors, and 'BRUTE_FORCE_HAMMING' for binary descriptors (default is 'ANN_L2').
        - geometricEstimator (str): Geometric estimator used for filtering matches. (default is 'acransac').
        - geometricFilterType (str): Type of geometric filter used to validate matches. (default is 'fundamental_matrix').
        - distanceRatio (float): Ratio used to discard non-meaningful matches. A higher value results in stricter matching (default is 0.8).
        - maxIteration (int): Maximum number of iterations for RANSAC algorithm (default is 2048).
        - maxMatches (int): Maximum number of matches to keep. Set to 0 for no limit (default is 0).
        - savePutativeMatches (bool): Whether to save putative matches to disk (default is False).
        - guidedMatching (bool): Whether to use guided matching to improve pairwise correspondences (default is False).
        - exportDebugFiles (bool): Whether to export debug files (e.g., SVG, DOT) for visualization and debugging (default is False).

        Output:
        - Creates an output folder where computed matches will be stored. This folder is specified by the `output` parameter.

        Detailed Description:
        - The purpose of this step is to match features between pairs of images based on extracted descriptors. The matching process is
          divided into photometric and geometric steps.
        - Photometric Matching: Finds candidate matches between images based on feature descriptors. It uses techniques like Approximate
          Nearest Neighbor (ANN) or Cascade Hashing to efficiently match features despite the complexity of descriptor spaces.
        - Geometric Filtering: Refines matches by using geometric constraints. It applies RANSAC to estimate a fundamental or essential
          matrix and filter out incorrect matches based on geometric consistency.
        - The method also includes options for saving intermediate results, performing cross-matching, and using guided matching to enhance
          the matching process.

        Notes:
        - If the number of images exceeds `imagesPerGroup`, the images are processed in batches to manage resource usage effectively.
        - Adjust parameters like `distanceRatio`, `maxIteration`, and `geometricError` to fine-tune the matching process based on dataset characteristics.
        """
        task = "\\tasks\\4_featureMatching"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 4/11 FEATURE MATCHING ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_cameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_featureExtraction\""
        imagePairsList = f"\"{self.project_path}\\tasks\\3_imageMatching\\imageMatches.txt\""

        # Command line for feature matching using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_featureMatching.exe "
                    f"--input {_input} "
                    f"--featuresFolders {featuresFolders} "
                    f"--imagePairsList {imagePairsList} "
                    f"--describerTypes {describerTypes} "
                    f"--photometricMatchingMethod {photometricMatchingMethod} "
                    f"--geometricEstimator {geometricEstimator} "
                    f"--geometricFilterType {geometricFilterType} "
                    f"--distanceRatio {distanceRatio} "
                    f"--maxIteration {maxIteration} "
                    f"--geometricError 0.0 "
                    f"--knownPosesGeometricErrorMax 5.0 "
                    f"--minRequired2DMotion -1.0 "
                    f"--maxMatches {maxMatches} "
                    f"--savePutativeMatches {savePutativeMatches} "
                    f"--crossMatching False "
                    f"--guidedMatching {guidedMatching} "
                    f"--matchFromKnownCameraPoses False "
                    f"--exportDebugFiles {exportDebugFiles} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output}")

        # When there are more than 20 images, send them in groups
        if self.num_of_images > imagesPerGroup:
            numberOfGroups = math.ceil(self.num_of_images / imagesPerGroup)
            for i in range(numberOfGroups):
                cmd = f"{cmd_line} --rangeStart {i * imagesPerGroup} --rangeSize {imagesPerGroup} "
                print(f"------- group {i} / {numberOfGroups} --------\n{cmd}")
                os.system(cmd)

        else:
            print(cmd_line)
            os.system(cmd_line)

    def run_5_incrementalSfM(self, describerTypes='dspsift', localizerEstimator='acransac',
                             observationConstraint='Scale', localizerEstimatorMaxIterations=4096,
                             localizerEstimatorError=0.0, lockScenePreviouslyReconstructed=False,
                             useLocalBA=True, localBAGraphDistance=1,
                             maxNumberOfMatches=0, minNumberOfMatches=0,
                             minInputTrackLength=2, minNumberOfObservationsForTriangulation=2,
                             minAngleForTriangulation=3.0, minAngleForLandmark=2.0,
                             maxReprojectionError=4.0, minAngleInitialPair=5.0,
                             maxAngleInitialPair=40.0, useOnlyMatchesFromInputFolder=False,
                             useRigConstraint=True, lockAllIntrinsics=False, filterTrackForks=False,
                             initialPairA='\"\"', initialPairB='\"\"',
                             interFileExtension='.abc', logIntermediateSteps=False):

        """
        Performs Incremental Structure from Motion (SfM) using AliceVision's `incrementalSfm` tool.

        This method reconstructs 3D points from a series of images by incrementally adding new views and refining the 3D model.
        It utilizes feature extraction, matching, and camera localization to build a sparse 3D point cloud and camera poses.

        Parameters:
        - describerTypes (str): Types of descriptors used for feature extraction. Options include 'sift', 'sift*float', 'sift*upright',
          'akaze', 'akaze*liop', 'akaze*mldb', 'cctag3', 'cctag4', 'siftocv', 'akazeocv' (default is 'dspsift').
        - localizerEstimator (str): Estimator type for localizing cameras. Options include 'acransac', 'ransac', 'lsmeds', 'loransac',
          'maxconsensus' (default is 'acransac').
        - observationConstraint (str): Mode for observation constraint in optimization. Options are 'Basic' for standard reprojection error
          and 'Scale' for reprojection error relative to feature scale (default is 'Scale').
        - localizerEstimatorMaxIterations (int): Maximum number of iterations for the localizer estimator (default is 4096).
        - localizerEstimatorError (float): Maximum allowed error for camera localization. If set to 0, the tool selects a threshold based
          on the estimator (default is 0.0).
        - lockScenePreviouslyReconstructed (bool): Whether to lock previously reconstructed poses and intrinsics (default is False).
        - useLocalBA (bool): Whether to use local Bundle Adjustment (default is True).
        - localBAGraphDistance (int): Graph distance limit for local Bundle Adjustment (default is 1).
        - maxNumberOfMatches (int): Maximum number of matches per image pair (0 means no limit; default is 0).
        - minNumberOfMatches (int): Minimum number of matches per image pair (0 means no limit; default is 0).
        - minInputTrackLength (int): Minimum track length in input data (default is 2).
        - minNumberOfObservationsForTriangulation (int): Minimum number of observations required for triangulating a point (default is 2).
        - minAngleForTriangulation (float): Minimum angle for triangulation (default is 3.0).
        - minAngleForLandmark (float): Minimum angle for landmark visibility (default is 2.0).
        - maxReprojectionError (float): Maximum allowed reprojection error (default is 4.0).
        - minAngleInitialPair (float): Minimum angle for the initial image pair (default is 5.0).
        - maxAngleInitialPair (float): Maximum angle for the initial image pair (default is 40.0).
        - useOnlyMatchesFromInputFolder (bool): Whether to use only matches from the input folder and ignore previously added matches
          (default is False).
        - useRigConstraint (bool): Whether to enable rig constraints for camera calibration (default is True).
        - lockAllIntrinsics (bool): Whether to lock all intrinsic camera parameters (default is False).
        - filterTrackForks (bool): Whether to filter out track forks caused by incoherent matches (default is False).
        - initialPairA (str): Filename of the first image in the initial pair (default is '""').
        - initialPairB (str): Filename of the second image in the initial pair (default is '""').
        - interFileExtension (str): Extension for intermediate files (default is '.abc').
        - logIntermediateSteps (bool): Whether to log intermediate steps of the reconstruction process (default is False).

        Output:
        - Generates an SfM data file containing the 3D reconstruction and camera poses (`sfm.abc`).
        - Creates a file with camera views and poses (`cameras.sfm`).
        - Stores additional reconstruction information in the specified output folder.

        Detailed Description:
        - This step reconstructs the 3D structure of a scene by incrementally adding images and refining the model.
        - Initially, it computes feature matches between image pairs, which are used to create tracks representing 3D points.
        - An initial image pair is selected based on criteria to ensure robust matches and reliable geometric information.
        - The fundamental matrix between the initial image pair is computed, and triangulation is performed to obtain 3D points.
        - New images with sufficient associations are then added, and their poses estimated using Perspective-n-Point (PnP) algorithms
          in a RANSAC framework.
        - Bundle Adjustment used to refine camera poses and 3D point positions, and outliers filtered based on reprojection error
          and observation angles.
        - The process iterates, adding new images and triangulating new points until no more views can be localized.
        """
        task = "\\tasks\\5_incrementalSfM"
        mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 5/11 STRUCTURE FROM MOTION ════════════════════════════════\033[0m")

        _input = f"\"{self.project_path}\\tasks\\1_cameraInit\\cameraInit.sfm\""
        output = f"\"{self.project_path + task}\\sfm.abc\""
        outputViewsAndPoses = f"\"{self.project_path + task}\\cameras.sfm\""
        extraInfoFolder = f"\"{self.project_path + task}\""
        featuresFolders = f"\"{self.project_path}\\tasks\\2_featureExtraction\""
        matchesFolders = f"\"{self.project_path}\\tasks\\4_featureMatching\""

        # Command line for structure from motion using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_incrementalSfm.exe "
                    f"--input {_input} "
                    f"--featuresFolders {featuresFolders} "
                    f"--matchesFolders {matchesFolders} "
                    f"--describerTypes {describerTypes} "
                    f"--localizerEstimator {localizerEstimator} "
                    f"--observationConstraint {observationConstraint} "
                    f"--localizerEstimatorMaxIterations {localizerEstimatorMaxIterations} "
                    f"--localizerEstimatorError {localizerEstimatorError} "
                    f"--lockScenePreviouslyReconstructed {lockScenePreviouslyReconstructed} "
                    f"--useLocalBA {useLocalBA} "
                    f"--localBAGraphDistance {localBAGraphDistance} "
                    f"--nbFirstUnstableCameras 30 "
                    f"--maxImagesPerGroup 30 "
                    f"--bundleAdjustmentMaxOutliers 50 "
                    f"--maxNumberOfMatches {maxNumberOfMatches} "
                    f"--minNumberOfMatches {minNumberOfMatches} "
                    f"--minInputTrackLength {minInputTrackLength} "
                    f"--minNumberOfObservationsForTriangulation {minNumberOfObservationsForTriangulation} "
                    f"--minAngleForTriangulation {minAngleForTriangulation} "
                    f"--minAngleForLandmark {minAngleForLandmark} "
                    f"--maxReprojectionError {maxReprojectionError} "
                    f"--minAngleInitialPair {minAngleInitialPair} "
                    f"--maxAngleInitialPair {maxAngleInitialPair} "
                    f"--useOnlyMatchesFromInputFolder {useOnlyMatchesFromInputFolder} "
                    f"--useRigConstraint {useRigConstraint} "
                    f"--rigMinNbCamerasForCalibration 20 "
                    f"--lockAllIntrinsics {lockAllIntrinsics} "
                    f"--minNbCamerasToRefinePrincipalPoint 3 "
                    f"--filterTrackForks {filterTrackForks} "
                    f"--computeStructureColor True "
                    f"--useAutoTransform True "
                    f"--initialPairA {initialPairA} "
                    f"--initialPairB {initialPairB} "
                    f"--interFileExtension {interFileExtension} "
                    f"--logIntermediateSteps {logIntermediateSteps} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output} "
                    f"--outputViewsAndPoses {outputViewsAndPoses} "
                    f"--extraInfoFolder {extraInfoFolder}")

        print(cmd_line)
        os.system(cmd_line)

    def run_6_prepareDenseScene(self, imagesPerGroup=40,
                                outputFileType='exr',
                                saveMetadata=True,
                                saveMatricesTxtFiles=False,
                                evCorrection=False):
        """
        Prepares the dense scene by undistorting images and generating EXR images using AliceVision's `prepareDenseScene` tool.

        This method corrects image distortions and generates undistorted images in the specified format. It also optionally saves
        metadata and matrix information, and applies exposure correction if needed.

        Parameters:
        - imagesPerGroup (int): Number of images to process per group. If the total number of images exceeds this value, they will be
          processed in batches (default is 40).
        - outputFileType (str): File format for the undistorted images. Options include 'jpg', 'png', 'tif', 'exr' (default is 'exr').
        - saveMetadata (bool): Whether to save projections and intrinsics information in the metadata of the output images. Applicable only
          for .exr images (default is True).
        - saveMatricesTxtFiles (bool): Whether to save projections and intrinsics information in text files (default is False).
        - evCorrection (bool): Whether to apply correction on images' Exposure Value (default is False).

        Output:
        - Generates a MVS configuration file (`mvs.ini`) for further processing.
        - Creates undistorted images in the specified output file format.
        - Optionally saves projections and intrinsics information as metadata or text files.
        """

        task = "\\tasks\\6_prepareDenseScene"
        mkdir(self.project_path + task)

        print(
            "\033[35m════════════════════════════════ 6/11 PREPARE DENSE SCENE ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_incrementalSfM\\sfm.abc\""
        output = f"\"{self.project_path + task}\""

        # Command line for preparing a dense scene using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_prepareDenseScene.exe "
                    f"--input {_input} "
                    f"--maskExtension jpg "
                    f"--outputFileType {outputFileType} "
                    f"--saveMetadata {saveMetadata} "
                    f"--saveMatricesTxtFiles {saveMatricesTxtFiles} "
                    f"--evCorrection {evCorrection} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output}")

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

    def run_7_depthMapEstimation(self, groupSize=12, downscale=2):
        """
        Generates depth maps for each camera using AliceVision's `depthMapEstimation` tool.

        This method computes depth maps by estimating the depth value of each pixel for all cameras resolved by SfM. It uses the SGM (Semi-Global Matching) approach to ensure accurate depth estimation.

        Parameters:
        - groupSize (int): Number of images to process per group. If the total number of images exceeds this value, they will be
          processed in batches (default is 12).
        - downscale (int): Image downscale factor to speed up the depth map estimation. Valid values are 1, 2, 4, 8, 16 (default is 2).

        Output:
        - Generates depth maps for the input images and saves them to the specified output folder.

        Detailed Description:
        - The depth map estimation step retrieves the depth value for each pixel across all cameras that have been resolved by SfM.
        - The SGM (Semi-Global Matching) method is used to compute depth maps. This approach involves selecting a number of nearest cameras around each image and estimating depth values by analyzing similarity between patches in the images.
        - The process creates a volume of depth candidates for each pixel and computes similarity using Zero Mean Normalized Cross-Correlation (ZNCC).
        - Filtering is applied to reduce noise and ensure consistency between depth maps from different cameras.
        - The `downscale` parameter controls the level of downscaling applied to images, which affects the resolution and computation time of depth map estimation.

        Notes:
        - The depth maps are generated in parallel and then filtered to ensure consistency across multiple cameras.
        - The process can handle large numbers of images by processing them in batches.
        """
        task = "\\tasks\\7_depthMapEstimation"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 7/11 DEPTH MAP ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_incrementalSfM\\sfm.abc\""
        output = f"\"{self.project_path + task}\""
        imagesFolder = f"\"{self.project_path}\\tasks\\6_prepareDenseScene\""

        # Command line for generating a depth map using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_depthMapEstimation.exe "
                    f"--input {_input} "
                    f"--imagesFolder {imagesFolder} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--downscale {downscale} "
                    f"--output {output}")

        numberOfBatches = int(math.ceil(self.num_of_images / groupSize))

        for i in range(numberOfBatches):
            groupStart = groupSize * i
            currentGroupSize = min(groupSize, self.num_of_images - groupStart)
            if groupSize > 1:
                print(f"DepthMap Group {i} of {numberOfBatches} : {groupStart} to {currentGroupSize}")
                cmd = f"{cmd_line} --rangeStart {str(groupStart)} --rangeSize {str(groupSize)}"
                print(cmd)
                os.system(cmd)

    def run_8_depthMapFiltering(self, groupSize=24,
                                nNearestCams=10,
                                minNumOfConsistentCams=3,
                                minNumOfConsistentCamsWithLowSimilarity=4,
                                pixSizeBall=0,
                                pixSizeBallWithLowSimilarity=0,
                                computeNormalMaps=False):
        """
        Filters depth maps to ensure consistency and remove inaccuracies using AliceVision's `depthMapFiltering` tool.

        This method processes depth maps to eliminate inconsistencies and isolate occluded areas, ensuring that depth information is reliable and accurate.

        Parameters:
        - groupSize (int): Number of images to process per group. If the total number of images exceeds this value, they will be
          processed in batches (default is 24).
        - nNearestCams (int): Number of nearest cameras used for filtering depth maps (default is 10, range 0-20).
        - minNumOfConsistentCams (int): Minimum number of consistent cameras required for a depth map to be considered valid (default is 3, range 0-10).
        - minNumOfConsistentCamsWithLowSimilarity (int): Minimum number of consistent cameras needed for pixels with low similarity (default is 4, range 0-10).
        - pixToleranceFactor (float): Tolerance factor for filtering depth maps in pixels (default is 2.0).
        - pixSizeBall (int): Size of the filtering ball in pixels for general depth map filtering (default is 0).
        - pixSizeBallWithLowSimilarity (int): Size of the filtering ball in pixels for depth maps with low similarity (default is 0).
        - computeNormalMaps (bool): Whether to compute normal maps during the filtering process (default is False).

        Output:
        - Generates filtered depth maps and saves them to the specified output folder.
        """
        task = "\\tasks\\8_depthMapFiltering"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 8/11 DEPTH MAP FILTER ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_incrementalSfM\\sfm.abc\""
        output = f"\"{self.project_path + task}\""
        depthMapsFolder = f"\"{self.project_path}\\tasks\\7_depthMapEstimation\""

        # Command line for filtering the depth map using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_depthMapFiltering.exe "
                    f"--input {_input} "
                    f"--depthMapsFolder {depthMapsFolder} "
                    f"--minViewAngle 2.0 "
                    f"--maxViewAngle 70.0 "
                    f"--nNearestCams {nNearestCams} "
                    f"--minNumOfConsistentCams {minNumOfConsistentCams} "
                    f"--minNumOfConsistentCamsWithLowSimilarity {minNumOfConsistentCamsWithLowSimilarity} "
                    f"--pixToleranceFactor 2.0 "
                    f"--pixSizeBall {pixSizeBall} "
                    f"--pixSizeBallWithLowSimilarity {pixSizeBallWithLowSimilarity} "
                    f"--computeNormalMaps {computeNormalMaps} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output}")

        numberOfBatches = int(math.ceil(self.num_of_images / groupSize))

        for i in range(numberOfBatches):
            groupStart = groupSize * i
            currentGroupSize = min(groupSize, self.num_of_images - groupStart)
            if groupSize > 1:
                print(f"DepthMapFiltering Group {i} of {numberOfBatches} : {groupStart} to {currentGroupSize}")
                cmd = f"{cmd_line} --rangeStart {str(groupStart)} --rangeSize {str(groupSize)}"
                print(cmd)
                os.system(cmd)

    def run_9_meshing(self, estimateSpaceFromSfM=True, estimateSpaceMinObservations=3,
                      estimateSpaceMinObservationAngle=10.0, maxInputPoints=50000000,
                      maxPoints=5000000, maxPointsPerVoxel=1000000,
                      minStep=2, partitioning='singleBlock', repartition='multiResolution',
                      angleFactor=15.0, simFactor=15.0,
                      pixSizeMarginInitCoef=2.0, pixSizeMarginFinalCoef=4.0,
                      voteMarginFactor=4.0, contributeMarginFactor=2.0,
                      simGaussianSizeInit=10.0, simGaussianSize=10.0,
                      minAngleThreshold=1.0, refineFuse=True, addLandmarksToTheDensePointCloud=False,
                      colorizeOutput=False, saveRawDensePointCloud=False):

        """
        Generates a mesh from SfM point clouds or depth maps using AliceVision's `meshing` tool.

        This method creates a dense geometric surface representation of the scene by fusing depth maps into a global octree, performing 3D Delaunay tetrahedralization,
        and applying a voting procedure to compute weights on cells. The final mesh is obtained by applying
        a Graph Cut Max-Flow algorithm to optimally cut the volume and then refining the mesh to remove artifacts.

        Parameters:
        - estimateSpaceFromSfM (bool): Whether to estimate the 3D space from the SfM (default is True).
        - estimateSpaceMinObservations (int): Minimum number of observations required for SfM space estimation (default is 3).
        - estimateSpaceMinObservationAngle (float): Minimum angle between two observations for SfM space estimation (default is 10.0).
        - maxInputPoints (int): Maximum number of input points loaded from depth map images (default is 50,000,000).
        - maxPoints (int): Maximum number of points at the end of depth maps fusion (default is 5,000,000).
        - maxPointsPerVoxel (int): Maximum number of points per voxel (default is 1,000,000).
        - minStep (int): Minimum step used to load depth values from depth maps (default is 2).
        - partitioning (str): Method for partitioning the depth map data. Options include 'singleBlock' and 'auto' (default is 'singleBlock').
        - repartition (str): Method for repartitioning the data. Options include 'multiResolution' and 'regularGrid' (default is 'multiResolution').
        - angleFactor (float): Factor for angle-based processing (default is 15.0).
        - simFactor (float): Factor for similarity-based processing (default is 15.0).
        - pixSizeMarginInitCoef (float): Initial coefficient for pixel size margin (default is 2.0).
        - pixSizeMarginFinalCoef (float): Final coefficient for pixel size margin (default is 4.0).
        - voteMarginFactor (float): Factor for voting margin (default is 4.0).
        - contributeMarginFactor (float): Factor for contribution margin (default is 2.0).
        - simGaussianSizeInit (float): Initial size of Gaussian filter for similarity (default is 10.0).
        - simGaussianSize (float): Size of Gaussian filter for similarity (default is 10.0).
        - minAngleThreshold (float): Minimum angle threshold for processing (default is 1.0).
        - refineFuse (bool): Whether to refine the depth map fusion with new pixel sizes defined by angle and similarity scores (default is True).
        - voteFilteringForWeaklySupportedSurfaces (bool): Whether to apply vote filtering for weakly supported surfaces (default is True).
        - addLandmarksToTheDensePointCloud (bool): Whether to add SfM landmarks to the dense point cloud (default is False).
        - invertTetrahedronBasedOnNeighborsNbIterations (int): Number of iterations for inverting tetrahedrons based on neighbor counts (default is 10).
        - colorizeOutput (bool): Whether to colorize the output dense point cloud and mesh (default is False).
        - saveRawDensePointCloud (bool): Whether to save the raw dense point cloud before cut and filtering (default is False).

        Output:
        - Output dense point cloud file in SfMData format (densePointCloud.abc).
        - Output mesh file in OBJ format (mesh.obj).

        Detailed Description:
        - The meshing process starts by fusing all depth maps into a global octree, where compatible depth values are merged.
        - 3D Delaunay tetrahedralization is then performed, followed by a complex voting procedure to compute weights on cells and facets.
        - A Graph Cut Max-Flow algorithm is applied to extract the mesh surface, and bad cells on the surface are filtered.
        - Finally, Laplacian filtering is applied to remove local artifacts, and the mesh can be simplified if needed.
        - Optionally, additional features like colorizing the output and adding landmarks can be enabled.
        """

        task = "\\tasks\\9_meshing"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 9/11 MESHING ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\5_incrementalSfM\\sfm.abc\""
        output = f"\"{self.project_path + task}\\densePointCloud.abc\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""
        depthMapsFolder = f"\"{self.project_path}\\tasks\\8_depthMapFiltering\""

        # Command line for meshing using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_meshing.exe "
                    f"--input {_input} "
                    f"--depthMapsFolder {depthMapsFolder} "
                    f"--estimateSpaceFromSfM {estimateSpaceFromSfM} "
                    f"--estimateSpaceMinObservations {estimateSpaceMinObservations} "
                    f"--estimateSpaceMinObservationAngle {estimateSpaceMinObservationAngle} "
                    f"--maxInputPoints {maxInputPoints} "
                    f"--maxPoints {maxPoints} "
                    f"--maxPointsPerVoxel {maxPointsPerVoxel} "
                    f"--minStep {minStep} "
                    f"--partitioning {partitioning} "
                    f"--repartition {repartition} "
                    f"--angleFactor {angleFactor} "
                    f"--simFactor {simFactor} "
                    f"--minVis 2 "
                    f"--pixSizeMarginInitCoef {pixSizeMarginInitCoef} "
                    f"--pixSizeMarginFinalCoef {pixSizeMarginFinalCoef} "
                    f"--voteMarginFactor {voteMarginFactor} "
                    f"--contributeMarginFactor {contributeMarginFactor} "
                    f"--simGaussianSizeInit {simGaussianSizeInit} "
                    f"--simGaussianSize {simGaussianSize} "
                    f"--minAngleThreshold {minAngleThreshold} "
                    f"--refineFuse {refineFuse} "
                    f"--helperPointsGridSize 10 "
                    f"--nPixelSizeBehind 4.0 "
                    f"--fullWeight 1.0 "
                    f"--voteFilteringForWeaklySupportedSurfaces True "
                    f"--addLandmarksToTheDensePointCloud {addLandmarksToTheDensePointCloud} "
                    f"--invertTetrahedronBasedOnNeighborsNbIterations 10 "
                    f"--minSolidAngleRatio 0.2 "
                    f"--nbSolidAngleFilteringIterations 2 "
                    f"--colorizeOutput {colorizeOutput} "
                    f"--maxNbConnectedHelperPoints 50 "
                    f"--saveRawDensePointCloud {saveRawDensePointCloud} "
                    f"--exportDebugTetrahedralization False "
                    f"--seed 0 "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output} "
                    f"--outputMesh {outputMesh}")

        print(cmd_line)
        os.system(cmd_line)

    def run_10_meshFiltering(self, filterLargeTrianglesFactor=60.0,
                             keepLargestMeshOnly='True',
                             smoothingIterations=5,
                             smoothingLambda=1.0):

        """
        Filters unwanted elements from the mesh using AliceVision's `meshFiltering` tool.

        This method removes large triangles, performs mesh smoothing, and optionally keeps only the largest connected mesh component.

        Parameters:
        - filterLargeTrianglesFactor (float): Factor to determine if a triangle is considered large.
          A triangle is deemed large if one edge is larger than N times the average edge length. Set to zero to disable (default is 60.0).
        - keepLargestMeshOnly (str): Whether to keep only the largest connected component of the mesh. Options are 'True' or 'False' (default is 'True').
        - smoothingIterations (int): Number of iterations for the smoothing process (default is 5).
        - smoothingLambda (float): Lambda parameter for smoothing (default is 1.0).

        Output:
        - Output filtered mesh file in OBJ format (mesh.obj).
        """

        task = "\\tasks\\10_meshFiltering"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 10/11 MESH FILTERING ════════════════════════════════\033[0m")
        inputMesh = f"\"{self.project_path}\\tasks\\9_meshing\\mesh.obj\""
        outputMesh = f"\"{self.project_path + task}\\mesh.obj\""

        # Command line for filtering the mesh using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_meshFiltering.exe "
                    f"--inputMesh {inputMesh} "
                    f"--smoothingSubset all "
                    f"--smoothingBoundariesNeighbours 0 "
                    f"--smoothingIterations {smoothingIterations} "
                    f"--smoothingLambda {smoothingLambda} "
                    f"--filteringSubset all "
                    f"--filteringIterations 1 "
                    f"--filterLargeTrianglesFactor {filterLargeTrianglesFactor} "
                    f"--filterTrianglesRatio 0.0 "
                    f"--keepLargestMeshOnly {keepLargestMeshOnly} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--outputMesh {outputMesh}")

        print(cmd_line)
        os.system(cmd_line)

    def run_11_texturing(self, textureSide=8192,
                         downscale=2,
                         outputMeshFileType='obj',
                         colorMappingFileType='jpg',
                         unwrapMethod='Basic',
                         fillHoles=True,
                         padding=5,
                         bestScoreThreshold=0.1,
                         angleHardThreshold=90.0,
                         forceVisibleByAllVertices=False,
                         flipNormals=False,
                         visibilityRemappingMethod='PullPush'):

        """
        Applies texturing to the 3D mesh using AliceVision's `texturing` tool.

        This method generates UV maps and applies textures to the mesh, creating high-resolution texture maps.

        Parameters:
        - textureSide (int): Size of the output texture (in pixels). Options include 1024, 2048, 4096, 8192, 16384 (default is 8192).
        - downscale (int): Downscale factor for the textures. Options include 1, 2, 4, 8 (default is 2).
        - inputRefMesh (str): Optional reference mesh for texturing. Default is empty.
        - outputMeshFileType (str): File type for the output mesh. Options include 'obj' (default).
        - colorMappingFileType (str): File type for the color mapping textures. Options include 'jpg', 'png', 'tiff', 'exr' (default is 'jpg').
        - unwrapMethod (str): Method used for unwrapping the mesh if UV coordinates are not present. Options include 'Basic', 'LSCM', 'ABF' (default is 'Basic').
        - useUDIM (bool): Whether to use UDIMs for texturing (default is True).
        - padding (int): Padding size for the texture edges in pixels (default is 5).
        - bestScoreThreshold (float): Threshold for filtering based on the best score (default is 0.1).
        - angleHardThreshold (float): Hard threshold for filtering based on angle (default is 90.0).
        - forceVisibleByAllVertices (bool): Ensure triangle visibility based on the union of all vertex visibility (default is False).
        - flipNormals (bool): Option to flip face normals if needed (default is False).
        - visibilityRemappingMethod (str): Method for remapping visibilities from the reconstruction to the input mesh. Options include 'Pull', 'Push', 'PullPush' (default is 'PullPush').
        - fillHoles (bool): Whether to fill holes in the texture (default is True).

        Output:
        - Output folder for the textured mesh, including:
          - Output Mesh (OBJ file format) - `texturedMesh.obj`
          - Output Material (MTL file format) - `texturedMesh.mtl`
          - Output Textures (PNG files) - `texture_*.png`

        Detailed Description:
        - The texturing process creates high-resolution textures for the 3D mesh, generating UV maps and applying textures based on the input images.
        - The unwrap method determines how UV coordinates are created if not already present, with different methods offering various optimizations.
        - Texture quality can be adjusted by changing the `textureSide` and `downscale` parameters. Higher values result in better quality but longer processing times.
        - Various options for visibility, normal flipping, and color space correction help refine the final texturing result.

        Notes:
        - Abnormal program termination: memory exhausted -> you don´t have enough Ram to finish, Reduce the Texture Side and/or increase the Downscale factor
        """

        task = "\\tasks\\11_texturing"
        mkdir(self.project_path + task)

        print("\033[35m════════════════════════════════ 11/11 TEXTURING ════════════════════════════════\033[0m")
        _input = f"\"{self.project_path}\\tasks\\9_meshing\\densePointCloud.abc\""
        imagesFolder = f"\"{self.project_path}\\tasks\\6_prepareDenseScene" "\""
        inputMesh = f"\"{self.project_path}\\tasks\\10_meshFiltering\\mesh.obj\""
        output = f"\"{self.project_path + task}\""

        # Command line for texturing the mesh using AliceVision
        cmd_line = (f"{self.bin_path}\\aliceVision_texturing.exe "
                    f"--input {_input} "
                    f"--inputMesh {inputMesh} "
                    f"--imagesFolder {imagesFolder} "
                    f"--textureSide {textureSide} "
                    f"--downscale {downscale} "
                    f"--inputRefMesh \'\' "
                    f"--outputMeshFileType {outputMeshFileType} "
                    f"--colorMappingFileType {colorMappingFileType} "
                    f"--unwrapMethod {unwrapMethod} "
                    f"--useUDIM True "
                    f"--padding {padding} "
                    f"--multiBandDownscale 4 "
                    f"--multiBandNbContrib 1 5 10 0 "
                    f"--useScore True "
                    f"--bestScoreThreshold {bestScoreThreshold} "
                    f"--angleHardThreshold {angleHardThreshold} "
                    f"--workingColorSpace sRGB "
                    f"--outputColorSpace AUTO "
                    f"--correctEV True "
                    f"--forceVisibleByAllVertices {forceVisibleByAllVertices} "
                    f"--flipNormals {flipNormals} "
                    f"--visibilityRemappingMethod {visibilityRemappingMethod} "
                    f"--subdivisionTargetRatio 0.8 "
                    f"--fillHoles {fillHoles} "
                    f"--verboseLevel {self.verboseLevel} "
                    f"--output {output}")

        print(cmd_line)
        os.system(cmd_line)

    def convert_mesh_to_cloud(self, method='POINTS', parameter=1_000_000):
        """
        Convert a textured mesh to a point cloud using CloudCompare.

        Parameters:
        - method (str): Method for sampling the mesh ('POINTS' or 'DENSITY').
            POINTS: the corresponding number of points
            DENSITY: the corresponding surface density
        - parameter (int): Number of points to sample from the mesh.

        This function uses CloudCompare's command line interface to sample a textured mesh
        and export it as a point cloud in PLY format.
        """
        model_path = f"{self.project_path}\\tasks\\11_texturing\\texturedMesh.obj"
        output_path = shlex.quote(
            f"{self.project_path}\\{os.path.basename(self.project_path)}_{number_to_shortcut(parameter)}.ply")

        cmd = self.cc_cli.new_command()
        cmd.silent()
        cmd.open(model_path)  # Open the textured mesh
        cmd.sample_mesh(method, parameter)  # Sample the mesh to generate a point cloud
        cmd.cloud_export_format(pcc.CLOUD_EXPORT_FORMAT.PLY)  # Set the output format to PLY
        cmd.save_clouds(output_path)  # Save the point cloud to the specified output path
        cmd.execute()  # Execute the command
        cmd.clear()  # Clear the command queue

        print(f"Converted mesh to point cloud with {method}:{parameter}")

    def run(self):
        """
        Main function to execute all the tasks in sequence.

        This function orchestrates the execution of multiple tasks in sequence:
        camera initialization, feature extraction, image matching, structure from motion,
        dense scene preparation, depth map generation and filtering, meshing, mesh filtering,
        mesh texturing, and finally conversion of the textured
        mesh to a point cloud.
        """
        try:
            mkdir(f"{self.project_path}\\tasks")

            # Create the full file path
            stats_file_path = f"{self.project_path}\\gpc_stats.txt"
            mesh_file_path = f"{self.project_path}\\tasks\\11_texturing\\texturedMesh.obj"

            # Reset file content
            clear_file(stats_file_path)

            # Run all the tasks in sequence, write elapsed time of each task into gpc_stats.txt
            start_time = time.time()

            append_file(stats_file_path, f"cameraInit : {measure_run_time(self.run_1_cameraInit)[0]}")
            append_file(stats_file_path, f"featureExtraction : {measure_run_time(self.run_2_featureExtraction, forceCpuExtraction=False)[0]}")
            append_file(stats_file_path, f"imageMatching : {measure_run_time(self.run_3_imageMatching)[0]}")
            append_file(stats_file_path, f"featureMatching : {measure_run_time(self.run_4_featureMatching)[0]}")
            append_file(stats_file_path, f"incrementalSfM : {measure_run_time(self.run_5_incrementalSfM)[0]}")
            append_file(stats_file_path, f"prepareDenseScene : {measure_run_time(self.run_6_prepareDenseScene)[0]}")
            append_file(stats_file_path, f"depthMapEstimation : {measure_run_time(self.run_7_depthMapEstimation)[0]}")
            append_file(stats_file_path, f"depthMapFiltering : {measure_run_time(self.run_8_depthMapFiltering)[0]}")
            append_file(stats_file_path, f"meshing : {measure_run_time(self.run_9_meshing)[0]}")
            append_file(stats_file_path, f"meshFiltering : {measure_run_time(self.run_10_meshFiltering)[0]}")
            append_file(stats_file_path, f"texturing : {measure_run_time(self.run_11_texturing, textureSide=4096, downscale=4)[0]}")

            try:

                # Convert the final mesh to a point cloud, write elapsed time of each convertion into gpc_stats.txt
                append_file(stats_file_path, f"════════════════════════════════════\n"
                                            f"meshToCloud : {measure_run_time(self.convert_mesh_to_cloud, parameter=count_faces_in_obj(mesh_file_path))[0]}")

                end_time = time.time()
                hours, rem = divmod(end_time - start_time, 3600)
                minutes, seconds = divmod(rem, 60)
                elapsed_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
                print("\033[35m════════════════════════════════ DONE ════════════════════════════════\033[0m")
                print("\033[35mTime elapsed: \033[0m" + f"\033[32m{elapsed_time}\033[0m")
                print(f"\033[35mPoint cloud successfully generated and saved")
                print("\033[35m══════════════════════════════════════════════════════════════════════\033[0m")

            except Exception as e:
                end_time = time.time()
                hours, rem = divmod(end_time - start_time, 3600)
                minutes, seconds = divmod(rem, 60)
                elapsed_time = "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)

                print("\033[35m════════════════════════════════ DONE ════════════════════════════════\033[0m")
                print("\033[35mTime elapsed: \033[0m" + f"\033[32m{elapsed_time}\033[0m")
                print_err(f"Failed to generate .ply from .obj: {e}")
                print("\033[35m══════════════════════════════════════════════════════════════════════\033[0m")

            append_file(stats_file_path, f"════════════════════════════════════\n"
                                        f"totalElapsedTime : {elapsed_time}")

        except Exception as e:
            print_err(e)
