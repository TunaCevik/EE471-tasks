import os
import argparse
import subprocess

# A dictionary linking your filename keywords to the exact names of your folders
TASK_MAP = {
    "face": "face_landmark_detection",
    "hand": "hand_landmark_detection",
    "class": "image_classification",
    "segment": "image_segmentation",
    "object": "object_detection",
    "pose": "pose_landmark_detection"
}

def determine_task(filename, override_model=None):
    """Determines which task to run based on the override or filename."""
    if override_model:
        if override_model in TASK_MAP:
            return override_model
        else:
            print(f"Error: Invalid model override '{override_model}'. Valid options are: {list(TASK_MAP.keys())}")
            return None

    # Default: Infer from the filename
    lower_filename = filename.lower()
    for keyword in TASK_MAP.keys():
        if keyword in lower_filename:
            return keyword
            
    return None

def main():
    parser = argparse.ArgumentParser(description="Master CLI Router for MediaPipe Vision Tasks")
    parser.add_argument("--input", type=str, nargs='+', required=True, help="Path to input image(s)")
    # Choices restricts the user to only input valid keys from our TASK_MAP
    parser.add_argument("--model", type=str, choices=list(TASK_MAP.keys()), help="Force a specific model (face, hand, class, segment, object, pose)")
    args = parser.parse_args()

    # Get the absolute path of the directory where this master main.py is located
    base_vision_dir = os.path.dirname(os.path.abspath(__file__))

    for image_path in args.input:
        if not os.path.exists(image_path):
            print(f"\n[Warning] File not found: {image_path}")
            continue

        filename = os.path.basename(image_path)
        print(f"\n" + "="*50)
        print(f"Analyzing: {filename}")
        
        # 1. Determine the task
        task_keyword = determine_task(filename, args.model)
        
        if not task_keyword:
            print(f"  -> Skipping: Could not infer task from filename, and no --model override was provided.")
            continue
            
        target_folder = TASK_MAP[task_keyword]
        print(f"  -> Routing to: {target_folder}")

        # 2. Get absolute paths
        # We must use absolute paths because we are about to change the working directory
        abs_image_path = os.path.abspath(image_path)
        target_script_dir = os.path.join(base_vision_dir, target_folder)
        target_script_path = os.path.join(target_script_dir, "main.py")

        # Check if the sub-script actually exists
        if not os.path.exists(target_script_path):
            print(f"  -> Error: Could not find {target_script_path}")
            continue

        # 3. Execute the Sub-Script
        try:
            # We run the sub-script using Python's subprocess module.
            # cwd=target_script_dir forces the terminal to pretend it is inside the subfolder,
            # which guarantees the script will find its local .task or .tflite files!
            result = subprocess.run(
                ["python3", "main.py", "--input", abs_image_path],
                cwd=target_script_dir, 
                text=True,
                capture_output=True
            )
            
            # Print the output from the sub-script
            if result.stdout:
                print(result.stdout.strip())
            
            # Print any errors if the sub-script crashed
            if result.stderr:
                stderr_text = result.stderr.strip()
                
                # result.returncode == 0 means the script actually succeeded!
                if result.returncode == 0:
                    # Classical error GPU not found using CPU downloanding using CPU's external libraries to run model.
                    if "XNNPACK delegate for CPU" in stderr_text or "libEGL warning" in stderr_text:
                        print("\n[Hardware Info]: GPU not found. Using CPU fallback method.")
                    else:
                        print("\n[Sub-Script Warning]:")
                        print(stderr_text)
                else:
                    print("\n[Fatal Sub-Script Error]:")
                    print(stderr_text)
                
        except Exception as e:
            print(f"  -> Failed to execute script: {e}")

if __name__ == "__main__":
    main()