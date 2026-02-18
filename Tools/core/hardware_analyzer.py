import argparse
import os
import platform
import shutil
import subprocess
import sys
from typing import Any, Dict

import psutil

from Tools.core.shared_db_instance import db


def check_backend_availability():
    """Checks if the DB service is reachable."""
    try:
        db.execute("SELECT 1")
    except Exception:
        print("❌ Error: Database Backend is offline!")
        print("   Please start the backend service first using: uv run manage.py serve")
        sys.exit(1)


def get_cpu_info() -> Dict[str, int]:
    return {
        "physical_cores": psutil.cpu_count(logical=False) or 1,
        "logical_cores": psutil.cpu_count(logical=True) or 1,
    }


def get_ram_info() -> Dict[str, float]:
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
    }


def get_gpu_info() -> Dict[str, Any]:
    gpu_info = {"type": "CPU", "vram_gb": 0.0, "vendor": "Unknown"}

    system = platform.system()
    machine = platform.machine()

    # 1. Apple Silicon Check
    if system == "Darwin" and "arm" in machine.lower():
        gpu_info["type"] = "Apple Silicon (Unified Memory)"
        gpu_info["vendor"] = "Apple"
        # On Apple Silicon, VRAM is effectively system RAM.
        # We'll consider a portion of system RAM as available "VRAM" for AI purposes.
        mem = psutil.virtual_memory()
        gpu_info["vram_gb"] = round(mem.total / (1024**3), 2)
        return gpu_info

    # 2. NVIDIA Check (nvidia-smi)
    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                vram_mb = int(result.stdout.strip().split("\n")[0])  # Take first GPU if multiple
                gpu_info["type"] = "Discrete GPU"
                gpu_info["vendor"] = "NVIDIA"
                gpu_info["vram_gb"] = round(vram_mb / 1024, 2)
                return gpu_info
        except Exception:
            pass

    # 3. AMD Check (rocm-smi) - Linux mainly
    if shutil.which("rocm-smi"):
        try:
            # Output format varies, this is a best-effort attempt
            result = subprocess.run(["rocm-smi", "--showvram"], capture_output=True, text=True)
            if result.returncode == 0:
                # Parsing ROCm output requires regex typically, keeping it simple/safe:
                # If we detect rocm-smi, we assume a capable GPU exists.
                # Getting exact VRAM reliably without regex dependencies is tricky.
                # We'll mark it as AMD and let the user refine if needed.
                gpu_info["type"] = "Discrete GPU"
                gpu_info["vendor"] = "AMD"
                # Conservative guess or 0 to force user check if we can't parse easily
                gpu_info["vram_gb"] = 0.0
                return gpu_info
        except Exception:
            pass

    return gpu_info


def calculate_optimal_settings() -> Dict[str, Any]:
    cpu = get_cpu_info()
    ram = get_ram_info()
    gpu = get_gpu_info()

    settings = {}
    explanations = {}

    # 1. CPU Threads
    # Reserve 2 cores for System/DB/UI, minimum 1 for AI
    recommended_threads = max(1, cpu["physical_cores"] - 2)
    settings["ai_num_thread"] = recommended_threads
    explanations["ai_num_thread"] = f"Physical Cores ({cpu['physical_cores']}) - 2 (System Reserve)"

    # 2. Context Size (num_ctx)
    total_mem = ram["total_gb"]
    if total_mem >= 32:
        settings["ai_num_ctx"] = 8192
        explanations["ai_num_ctx"] = "High RAM (>32GB) allows large context"
    elif total_mem >= 16:
        settings["ai_num_ctx"] = 4096
        explanations["ai_num_ctx"] = "Medium RAM (>16GB) allows standard context"
    else:
        settings["ai_num_ctx"] = 2048
        explanations["ai_num_ctx"] = "Low RAM (<16GB) restricts context size"

    # 3. GPU Offload (num_gpu) & Acceleration Mode
    
    layer_size_mb = 180 
    model_overhead_mb = 1024 
    
    if gpu["type"] == "Apple Silicon (Unified Memory)":
        settings["ai_acceleration_mode"] = "gpu"
        settings["ai_num_gpu"] = 99
        explanations["ai_acceleration_mode"] = "Apple Silicon detected (Unified Memory)"
        explanations["ai_num_gpu"] = "Full offload to Neural Engine"
    elif gpu["vendor"] == "NVIDIA":
        vram_mb = gpu["vram_gb"] * 1024
        
        if vram_mb >= 8192: 
            settings["ai_acceleration_mode"] = "gpu"
            settings["ai_num_gpu"] = 99
            explanations["ai_acceleration_mode"] = f"NVIDIA GPU with ample VRAM ({gpu['vram_gb']}GB)"
            explanations["ai_num_gpu"] = "Full offload possible"
        elif vram_mb >= 2048:
            available_for_layers = vram_mb - model_overhead_mb
            if available_for_layers > 0:
                possible_layers = int(available_for_layers / layer_size_mb)
                settings["ai_acceleration_mode"] = "hybrid"
                settings["ai_num_gpu"] = max(1, possible_layers)
                explanations["ai_acceleration_mode"] = f"NVIDIA GPU with limited VRAM ({gpu['vram_gb']}GB)"
                explanations["ai_num_gpu"] = f"Partial offload: ~{possible_layers} layers fit in VRAM"
            else:
                settings["ai_acceleration_mode"] = "cpu"
                settings["ai_num_gpu"] = 0
                explanations["ai_acceleration_mode"] = "NVIDIA GPU VRAM too low for model overhead"
                explanations["ai_num_gpu"] = "Fallback to CPU"
        else:
            settings["ai_acceleration_mode"] = "cpu"
            settings["ai_num_gpu"] = 0
            explanations["ai_acceleration_mode"] = "NVIDIA GPU VRAM too low (<2GB)"
            explanations["ai_num_gpu"] = "Fallback to CPU"
            
    elif gpu["vendor"] == "AMD":
        settings["ai_acceleration_mode"] = "hybrid" 
        settings["ai_num_gpu"] = 20 
        explanations["ai_acceleration_mode"] = "AMD GPU detected (ROCm)"
        explanations["ai_num_gpu"] = "Conservative offload estimation"
    else:
        settings["ai_acceleration_mode"] = "cpu"
        settings["ai_num_gpu"] = 0
        explanations["ai_acceleration_mode"] = "No supported dedicated GPU detected"
        explanations["ai_num_gpu"] = "CPU only execution"

    return settings, explanations


def apply_settings(settings: Dict[str, Any]):
    """Writes settings to DuckDB registry."""
    print("\n💾 Applying Optimized Settings...")
    for key, value in settings.items():
        # UPSERT into registry.settings
        db.execute(
            """
            INSERT INTO registry.settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            [key, str(value)],
        )
        print(f"   ✅ Set {key} = {value}")
    print("\n✨ Settings saved to DuckDB registry successfully.")


def run_optimization():
    parser = argparse.ArgumentParser(description="WoW Toolkit Hardware Optimizer")
    parser.add_argument("-y", "--yes", action="store_true", help="Automatically apply settings")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Calculate only, do not save")
    args = parser.parse_args()

    check_backend_availability()
    print("\n🔍 Analyzing Hardware...")
    
    cpu = get_cpu_info()
    print(f"   - CPU: {cpu['physical_cores']} Physical Cores ({cpu['logical_cores']} Logical)")
    
    ram = get_ram_info()
    print(f"   - RAM: {ram['total_gb']} GB Total ({ram['available_gb']} GB Available)")
    
    gpu = get_gpu_info()
    print(f"   - GPU: {gpu['vendor']} ({gpu['type']}) - VRAM: {gpu['vram_gb']} GB")

    recommendations, explanations = calculate_optimal_settings()
    
    print("\n💡 Recommended Settings:")
    
    # Helper for printing aligned
    def print_rec(label, key):
        val = recommendations[key]
        expl = explanations.get(key, "")
        if isinstance(val, str):
            val = val.upper()
        print(f"   - {label:<15} {val:<10}  ({expl})")

    print_rec("Mode:", "ai_acceleration_mode")
    print_rec("Threads:", "ai_num_thread")
    print_rec("Context Size:", "ai_num_ctx")
    print_rec("GPU Layers:", "ai_num_gpu")

    if args.dry_run:
        print("\n🚫 Dry run mode active. No changes made.")
        sys.exit(0)

    if args.yes:
        apply_settings(recommendations)
    else:
        # Check if we are in an interactive terminal
        if not sys.stdin.isatty():
            print("\n⚠️  Non-interactive mode detected. Use -y to apply settings automatically.")
            sys.exit(1)

        # Interactive Prompt
        try:
            print("\n❓ Do you want to apply these settings? [Y/n] ", end="", flush=True)
            response = sys.stdin.readline().strip().lower()
            if response in ["", "y", "yes"]:
                apply_settings(recommendations)
            else:
                print("\n❌ Cancelled by user. No changes made.")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user.")
            sys.exit(0)


if __name__ == "__main__":
    run_optimization()
