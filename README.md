<p align='center'>
  <img src= 'https://github.com/user-attachments/assets/daefddc1-c954-4be4-826a-cd1d75dfe90d'/>
</p>

[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.11-purple.svg)](https://www.python.org/downloads/)
[![Meshroom Version](https://img.shields.io/badge/meshroom-2023.3.0-purple.svg)](https://github.com/alicevision/Meshroom/releases/tag/v2023.3.0)
[![CloudCompare Version](https://img.shields.io/badge/cloudcompare-2.13.2-purple.svg)](https://github.com/CloudCompare/CloudCompare/releases/tag/v2.13.2)
## Introduction


Photogrammetry-CLI is a powerful command-line tool tailored for photogrammetry workflows. It facilitates the extraction of frames from video files, the generation of point clouds from images, and the combination of point clouds into a unified 3D model. 
Utilizing [Meshroom's AliceVision](https://github.com/alicevision/Meshroom) for the photogrammetry process and [CloudCompare](https://github.com/CloudCompare/CloudCompare) for ICP alignment and mesh-to-cloud conversion, this tool is optimized for Windows, offering a streamlined solution for processing and analyzing 3D data derived from video sources.

## Table of Contents
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Dependencies](#dependencies)
  - [Meshroom's AliceVision Setup](#meshrooms-alicevision-setup)
  - [CloudCompare Setup](#cloudcompare-setup)
- [Usage](#usage)
- [Commands](#commands)
  - [video2images](#video2images)
  - [generatePointCloud](#generatepointcloud)
  - [combinePointClouds](#combinepointclouds)
- [License](#license)
- [Authors](#authors)

## Installation

### Prerequisites
- **Operating System:** Windows (only supported on Windows)
- **Python Version:** Python 3.11 (tested on this version but might work on other 3.x versions)
- **Meshroom's AliceVision:** Required for photogrammetry processing [(refer to setup instructions below)](#meshrooms-alicevision-setup)
- **CloudCompare:** Required for ICP alignment and mesh-to-cloud conversion [(refer to setup instructions below)](#cloudcompare-setup)
- **GPU:** NVIDIA GPU with CUDA support (recommended for optimal performance)

### Dependencies
Before running the CLI, you'll need to install the required Python dependencies. You can do this using pip. First, make sure you have pip installed and updated, then run:
```bash
pip install -r requirements.txt
```

### Meshroom's AliceVision Setup

1. **Download Meshroom Zip File:**
   - Download Meshroom from the following link:  
     [Meshroom v2023.3.0 for Windows 64-bit](https://github.com/alicevision/Meshroom/releases/download/v2023.3.0/Meshroom-2023.3.0-win64.zip)

2. **Extract the Zip File:**
   - Extract the contents of the zip file to a location of your choice.

3. **Move the `aliceVision` Folder:**
   - Locate the `aliceVision` folder inside the extracted Meshroom directory.
   - Drag the `aliceVision` folder to the root of this project’s directory.

4. **Run Configuration Script:**
   - Navigate to the project directory and run the `configure.bat` script to set the `ALICEVISION_ROOT` environment variable:
     
     ```bash
     configure.bat
     ```
   - This script will automatically configure the `ALICEVISION_ROOT` environment variable to point to the `aliceVision` folder.

### CloudCompare Setup

1. **Download CloudCompare Setup File:**
   - Download CloudCompare from the following link:  
     [CloudCompare v2.13.2 for Windows 64-bit](https://cloudcompare-org.danielgm.net/release/CloudCompare_v2.13.2_setup_x64.exe)

2. **Install CloudCompare:**
   - Run the downloaded setup file and install CloudCompare to the following directory:
     `C:\Program Files\CloudCompare`

## Usage
To start using the CLI, simply run the `run.bat` file or execute the `run.py` script directly. This will initiate the CLI and provide access to the available commands.
 ```bash
 run.bat
```

<p align='center'>
  <img src= 'https://github.com/user-attachments/assets/0ed62e4a-a2f0-4d7f-b6f6-40058f886f15'/>
</p>

## Commands

### video2images

Extracts frames from a video file based on structural similarity (SSIM) and overlap criteria.



<p align='center'>
  <img src='https://github.com/user-attachments/assets/27500c89-ce57-43f1-9f7b-047ba14029f9' />
</p>


**Arguments:**
- `<video_path>`: Path to the input video file (must be in `.mp4` format).
- `<project_path>`: Path to the output folder where frames will be saved (a subfolder named `images` will be created).
- `[max_frames]` (optional): Maximum number of frames to extract (default is 100).
- `[max_overlap_percentage]` (optional): Maximum allowed percentage overlap with previous frames (default is 6).
- `[ssim_threshold]` (optional): SSIM threshold below which frames are considered different (default is 0.95).

**Example:**
```bash
video2images "path\\video.mp4" "path\\project\\dir" 200 5 0.90
 ```

### generatePointCloud

Generates a point cloud from the extracted frames using the Meshroom's AliceVision photogrammetry pipeline.

<p align='center'>
  <img src= 'https://github.com/user-attachments/assets/117af2ca-5a9a-45cb-ae13-859d2cb508e9' width='900' height='auto'/>
</p>


**Arguments:**
- `<project_path>`: Path to the project folder containing the images folder.

**Example:**
```bash
generatePointCloud "path\\project\\dir"
 ```

 ### combinePointClouds

Combines two point clouds into a single point cloud using the Iterative Closest Point (ICP) algorithm, assuming the point clouds are roughly aligned and have overlapping regions.

**Arguments:**
- `<cloud1_path>`: Path to the first point cloud file.
- `<cloud2_path>`: Path to the second point cloud file.
- `<output_path>`: Path to the cloud output file.

**Example:**
```bash
combinePointClouds "path\\cloud1.ply" "path\\cloud2.ply" "path\\output.ply"
 ```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## Authors
- [@noy-dayan](https://github.com/noy-dayan) (Project Manager)
- [@AvivShevach](https://github.com/AvivShevach)
- [@neryaRez](https://github.com/neryaRez)
