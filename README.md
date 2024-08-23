# Photogrammetry-CLI

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

## Introduction

Photogrammetry-CLI is a command-line interface tool designed for photogrammetry tasks, including extracting frames from videos, generating point clouds from images, and combining point clouds into a unified model. Utilizing Meshroom's AliceVision for the photogrammetry pipeline, this tool is optimized for Windows and provides an easy way to process and analyze 3D data from video sources.

## Table of Contents
- [Installation](#installation)
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
- **GPU:** NVIDIA GPU with CUDA support (recommended for optimal performance but not necessary)
- **Meshroom's AliceVision:** Required for photogrammetry processing (see setup instructions below)

### Dependencies
Before running the CLI, you'll need to install the required Python dependencies. You can do this using pip. First, make sure you have pip installed and updated, then run:
```bash
pip install -r requirements.txt
```

### Meshroom's AliceVision Setup

1. **Download Meshroom:**
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

## Usage
To start using the CLI, simply run the `run.bat` file or execute the `run.py` script directly. This will initiate the CLI and provide access to the available commands.

## Commands

### video2images

Extracts frames from a video file based on structural similarity (SSIM) and overlap criteria. This command saves the extracted frames to the specified output folder.

**Arguments:**
- `<video_path>`: Path to the input video file (must be in `.mp4` format).
- `<project_path>`: Path to the output folder where frames will be saved (a subfolder named 'images' will be created).
- `[max_frames]` (optional): Maximum number of frames to extract (default is 100).
- `[max_overlap_percentage]` (optional): Maximum allowed percentage overlap with previous frames (default is 6).
- `[ssim_threshold]` (optional): SSIM threshold below which frames are considered different (default is 0.95).

**Example:**
```bash
video2images "path\\video.mp4" "path\\project\\dir" 200 5 0.90
 ```

### generatePointCloud

Generates a point cloud from the extracted frames using the Meshroom's AliceVision photogrammetry pipeline.

**Arguments:**
- `<project_path>`: Path to the project folder containing the images folder.

**Example:**
```bash
generatePointCloud "path\\project\\dir"
 ```

 ### combinePointClouds

Combines two point clouds into a single point cloud using the Iterative Closest Point (ICP) algorithm.

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
