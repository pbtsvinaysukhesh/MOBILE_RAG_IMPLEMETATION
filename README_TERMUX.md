# Mobile RAG Implementation - Termux Android Setup Guide

This guide will help you set up and run the Mobile RAG Implementation project on an Android device using the Termux app.

## Prerequisites
- Android device
- [Termux app](https://f-droid.org/packages/com.termux/) (install from F-Droid for best compatibility)
- Stable internet connection


## Step 1: Update and Install Required Packages
Open Termux and run the following commands:

```sh
pkg update && pkg upgrade -y
pkg install python git clang -y
```

## Step 2: Install and Run Ollama (for Embeddings)
Ollama is required to generate embeddings. As of now, Ollama does not natively support Android/Termux. You must run Ollama on a separate machine (Linux, macOS, or Windows) and make it accessible to your Android device over the network.

**On your PC or server:**

1. Follow the official instructions to install Ollama: [Ollama Installation Guide](https://ollama.com/download)
2. Start the Ollama server:
   ```sh
   ollama serve
   ```
3. Make sure your Android device and the Ollama server are on the same network.
4. Update the `OLLAMA_EMBED_URL` in your scripts (if needed) to point to your PC/server's IP address, e.g.:
   ```python
   OLLAMA_EMBED_URL = "http://<PC-IP>:11434/api/embeddings"
   ```

**Note:** Running Ollama directly on Android/Termux is not supported. You must use a remote Ollama server.

## Step 3: Clone the Repository
Replace `<repo-url>` with your repository URL:

```sh
git clone <repo-url>
cd Mobile_RAG_Implementation
```

## Step 4: Install Python Dependencies
If you have a `requirements.txt` file, run:

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

If not, manually install required packages (update this list as needed):

```sh
pip install openai
```

## Step 5: Run the Scripts
You can now run the Python scripts as needed. For example:

```sh
python create_db.py
python ask_db.py
```

## Notes
- Some Python packages may not work on Termux due to architecture limitations. Test your scripts and check for errors.
- If you need additional packages, install them using `pip install <package-name>`.
- For advanced usage (e.g., Flask, FastAPI), you may need to install extra dependencies.

## Troubleshooting
- If you encounter permission errors, try running `termux-setup-storage` and grant storage permissions.
- For issues with pip, try `pip install --upgrade pip`.

## Useful Termux Commands
- `termux-setup-storage` – Access device storage
- `pkg install <package>` – Install additional packages
- `pip install <package>` – Install Python packages

---

For more help, refer to the [Termux Wiki](https://wiki.termux.com/wiki/Main_Page) or the official documentation of the packages you are using.
