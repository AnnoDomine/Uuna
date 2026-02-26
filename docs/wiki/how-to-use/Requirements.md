# 💻 System Requirements

[⬅️ Back to Home](../Home.md)

To run the Grand WoW Library and its AI agents effectively, your system should meet the following specifications.

## Hardware

> ℹ️ **Note**: All specifications below are based on the default model: **Qwen 2.5 7B** (or Qwen 3 8B) running at **Q4_K_M** quantization. Larger models (e.g., Llama 3 70B) will require significantly more VRAM/RAM.

- **Storage**: 50GB+ (The Unified DuckDB Archive is highly compressed but stores millions of rows).
- **RAM**: 16GB minimum (32GB recommended for large-scale indexing).
- **CPU**: Multi-core processor with AVX2 support (Essential for local LLM execution).
- **GPU (Optional but Recommended)**:
  - **NVIDIA**: 8GB+ VRAM for partial offloading, 12GB+ for full offloading (Qwen 8B).
  - **Apple Silicon**: M1/M2/M3 chips are supported natively via Unified Memory.
  - **AMD**: Supported on Linux via ROCm.

## ⚡ Auto-Optimization

The toolkit includes a built-in hardware analyzer that automatically configures the AI client for optimal performance on your specific machine. It detects CPU cores, RAM, and GPU VRAM to calculate the best thread count, context window, and GPU offloading strategy.

### Usage

```bash
# Analyze and interactive apply
uv run manage.py optimize

# Analyze and dry-run (see what would change)
uv run manage.py optimize -n

# Analyze and auto-apply (useful for scripts)
uv run manage.py optimize -y
```

### Example Output

```text
🚀 Running Hardware Optimization...

🔍 Analyzing Hardware...
   - CPU: 12 Physical Cores (24 Logical)
   - RAM: 30.91 GB Total (18.83 GB Available)
   - GPU: NVIDIA (Discrete GPU) - VRAM: 11.99 GB

💡 Recommended Settings:
   - Mode:           GPU         (NVIDIA GPU with ample VRAM (11.99GB))
   - Threads:        10          (Physical Cores (12) - 2 (System Reserve))
   - Context Size:   4096        (Medium RAM (>16GB) allows standard context)
   - GPU Layers:     99          (Full offload possible)

❓ Do you want to apply these settings? [Y/n]
```

## Software & Environment

- **Operating System**: Linux (Ubuntu/Debian recommended) or macOS.
- **Python**: Version 3.12 or higher.
- **AI Backend**: [Ollama](https://ollama.ai/) (Required for local LLM execution).
- **Database**: DuckDB (Handled automatically via Python).
- **Memory Cache**: Redis (Optional, used for high-performance agent communication).
