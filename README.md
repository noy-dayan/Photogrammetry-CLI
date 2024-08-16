# Photogrammetry-CLI

<!---
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
-->
## Table of Contents
<!---
- [Introduction](#introduction)
- [Features](#features)
-->
- [Installation](#installation)
<!---
- [Usage](#usage)
- [Configuration](#configuration)
- [Examples](#examples)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

Briefly describe the purpose of the project. Explain what problem it solves or what functionality it provides.

## Features

- List your key features here
- Highlight any unique aspects of your project
- Mention if the project is still in development or fully functional
-->
## Installation

### Prerequisites
- **Operating System:** Windows (only supported on Windows)
- **Python Version:** Python 3.11 (tested on this version but might work on other 3.x versions)
- **GPU:** NVIDIA GPU with CUDA support (recommended for optimal performance but not necessary)
- Meshroom (see below for setup instructions)

<!---- Required Python packages (listed in `requirements.txt`)-->
<!---
### Install via pip

```bash
pip install -r requirements.txt
```
-->
### Meshroom Setup

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
