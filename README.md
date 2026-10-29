# Takcas Prime: Autonomous IT Factory

A multi-agent system that generates, reviews, and tests Python code on a low-end Android tablet (8 GB RAM) using Termux and Ollama.

## Architecture
- **Coder**: Writes code based on a task.
- **Analyzer**: Simplifies and refactors the code.
- **Critics (Logic, Syntax, Coder)**: Check the code from different angles.
- **Judge**: Fixes errors and adds basic `assert` tests.
- **Smart Sandbox**: Blocks dangerous commands, runs code in isolation, and verifies tests.

## Optimization for Low-End Hardware
Running neural networks on an 8 GB tablet is challenging. We solved OOM (Out Of Memory) crashes by:
1. **Ollama HTTP API**: Switched from CLI to API with `num_ctx: 2048` to limit memory usage.
2. **Smart Memory Guard**: Replaced aggressive `pkill` with a custom memory manager that waits for the OS to free RAM.
3. **Self-Healing Pipeline**: If a model times out, the Director retries with feedback.
4. **Strict Prompts**: Forced models to use local URLs (`127.0.0.1:11434`) instead of cloud APIs.

## Tech Stack
Python 3 / Ollama (Qwen2.5-Coder, Qwen2.5) / Termux (Android) / Flask / SQLite

## Results
The factory successfully generated and tested a thread-safe TTL cache with LRU eviction, background cleaner, and callback outside the lock. 
**Test passed successfully!** (Hits: 53, Misses: 107, Evictions: 105, Callback under lock: False)
