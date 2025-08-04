# Mobile RAG Implementation - Termux Android Setup

This project provides scripts for a Retrieval-Augmented Generation (RAG) workflow. To run this project on an Android device using Termux, follow the steps below.

## Prerequisites
- Android device
- [Termux app](https://f-droid.org/packages/com.termux/) installed from F-Droid (recommended)
- Internet connection

## Installation Steps

### 1. Update and Install Python
```
pkg update && pkg upgrade -y
pkg install python -y
```

### 2. Install pip (if not already installed)
```
pkg install python-pip -y
pkg install python-torch
pkg install python python-numpy pandoc poppler jq
pip install requests


```

### 3. Clone or Download the Project
If you have git:
```
pkg install git -y
git clone <your-repo-url>
cd Mobile_RAG_Implementation
```
Or, download and extract the project folder, then move it to your Termux home directory.

### 4. Install Required Python Packages
If you have a `requirements.txt` file, run:
```
pip install -r requirements.txt
```
If not, manually install required packages (update this list as needed):
```

### 5. Run the Scripts
To create the database:
```
python create_db.py
```
To interact with the database:
```
python ask_db.py
```

## Notes
- If you need additional Python packages, install them using `pip install <package-name>`.
- For advanced usage, refer to the comments in each script.
- If you encounter permission issues, use `chmod +x <script.py>`.

## Troubleshooting
- If you get a `ModuleNotFoundError`, install the missing module with pip.
- For Termux-specific issues, refer to the [Termux Wiki](https://wiki.termux.com/wiki/Main_Page).

---

**Update this README as your project evolves!**
