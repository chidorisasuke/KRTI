# KRTI 2024 - Autonomous Drone System

<p align="center">
  <img src="drone design.webp" alt="KRTI Drone" width="500"/>
</p>

<p align="center">
  <strong>4th Place Winner at the National Robot Contest of Indonesia (KRTI) 2024</strong>
</p>

<p align="center">
  This repository contains the complete ROS-based software stack for our autonomous drone, developed for the KRTI 2024 competition.
</p>

---

## About The Project

Our journey for the KRTI 2024 competition began not with the physical drone, but in the virtual world. Using **Gazebo, ROS, and Python**, we first built a high-fidelity simulation to rigorously test every phase of the mission, from indoor maneuvering to complex outdoor flight. This "simulation-first" approach was crucial for tackling the competition's main challenge: integrating multiple advanced features into one seamless operation.

We programmed the drone to perform object detection for payload acquisition, navigate autonomously through a narrow window, and execute a smooth flight transition from an indoor to an outdoor environment. Once our algorithms were proven in the simulation, we began the careful process of implementing the system onto the drone's **Raspberry Pi 4**. After countless hours of coding, calibration, and real-world testing, our drone successfully executed the entire mission with precision, culminating in an accurate payload delivery and securing **4th Place** at the national level.

## Key Features

- **High-Fidelity Simulation:** A complete Gazebo simulation for end-to-end mission testing and validation.
- **Autonomous Navigation:** Capable of complex maneuvering, including traversing through a window.
- **Object Detection:** A lightweight computer vision module for detecting and acquiring payloads.
- **Indoor-to-Outdoor Transition:** Seamless flight path execution between different environments.
- **Precision Payload Delivery:** Autonomous release of objects at designated target locations.

## Technology Stack

- **Frameworks:** ROS (Robot Operating System), Gazebo
- **Languages:** Python, C++
- **Hardware:**
  - Raspberry Pi 4 (Onboard Computer)
  - Flight Controller (e.g., Pixhawk)
  - Camera Sensor

## Getting Started

Follow these instructions to set up the project on a new machine.

### Prerequisites

- **Ubuntu 20.04** (or your ROS-compatible OS)
- **ROS Noetic Ninjemys** installed. If you need to install ROS, you can use a setup script:
  ```sh
  # Make the script executable
  chmod +x tahapan_setup_ros_dekstop.sh
  # Run the script
  sudo ./tahapan_setup_ros_dekstop.sh
  ```

### Installation

1.  **Create a Catkin Workspace:**
    ```sh
    # Create the necessary directories
    mkdir -p ~/your_workspace_name/src
    cd ~/your_workspace_name/
    ```

2.  **Build the Workspace:**
    ```sh
    catkin_make
    ```

3.  **Source the Workspace:**
    ```sh
    source devel/setup.bash
    ```

4.  **Clone the Repository:**
    Navigate to the `src` directory and clone the project.
    ```sh
    cd src/
    # Note: This is a private repository and requires access permission.
    git clone https://github.com/Akasasura/krti2024_pi.git
    ```

5.  **Build the Packages:**
    Return to the root of your workspace and build again.
    ```sh
    cd ~/your_workspace_name/
    catkin_make
    # Or for a cleaner build, use: catkin build
    ```

6.  **Source Again:**
    Always source the `setup.bash` file after a build to recognize new packages.
    ```sh
    source devel/setup.bash
    ```

7.  **Verify Package:**
    Check if ROS can find your new package.
    ```sh
    rospack find krti2024_pi
    ```

## Troubleshooting

If `catkin_make` fails after cloning the repository, it's likely due to a mismatch between the project's original package name and your current setup.

**Problem:** Build fails, cannot find package or dependencies.

**Solution:** You may need to edit the package name in the following files to match the name of the package directory (`krti2024_pi`):

1.  **`package.xml`**: Ensure the `<name>` tag matches the package name.
2.  **`CMakeLists.txt`**: Check the `project(...)` name at the top of the file.
3.  **Any source file (`.cpp`, `.py`)**: Look for custom message or service includes (e.g., `from krti2024_pi.msg import ...`) and ensure the name is correct.
4.  **`setup.py`** (if it exists for Python scripts).

After making changes, clean your workspace and rebuild:
```sh
# From your workspace root (e.g., ~/your_workspace_name/)
rm -rf devel/ build/
catkin_make
```

## Usage

To run the simulation or the main mission, use `roslaunch`.

1.  **Launch the Gazebo Simulation:**
    ```sh
    roslaunch krti2024_pi simulation.launch
    ```
2.  **Run the Main Mission Node:**
    ```sh
    roslaunch krti2024_pi mission.launch
    ```

## Contributing

This was a competition project, but suggestions and improvements are welcome. Please fork the repo and create a pull request.

## License

Distributed under the MIT License. See `LICENSE` file for more information.
