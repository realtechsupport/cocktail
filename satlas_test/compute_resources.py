import os
import platform
import subprocess
import psutil

def check_gpu():
    try:
        # Check for NVIDIA GPU
        nvidia_smi = subprocess.check_output(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader']).decode('utf-8').strip()
        if nvidia_smi:
            return f"GPU detected: {nvidia_smi}"
        else:
            return "No NVIDIA GPU detected"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "NVIDIA GPU tools not found"

def check_cpu():
    cpu_info = {
        'processor': platform.processor(),
        'architecture': platform.machine(),
        'cores': psutil.cpu_count(logical=False),
        'threads': psutil.cpu_count(logical=True)
    }
    return f"CPU detected: {cpu_info['processor']} ({cpu_info['architecture']}) - {cpu_info['cores']} cores, {cpu_info['threads']} threads"

def check_cloud_run():
    if 'K_SERVICE' in os.environ:
        return ("1 - Running on Google Cloud Run")
    else:
        return ("0 - Not running on Google Cloud Run")
