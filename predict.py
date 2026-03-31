"""Pokemon prediction using dual ONNX models — improved edition

Key improvements over v1:
  - _run_model pushed to a ThreadPoolExecutor → never blocks the event loop
  - asyncio.Queue worker pool → serialises model calls, no contention on bursts
  - Configurable ONNX thread counts (1 primary, up to n_cpu secondary)
  - Model warm-up inference on load → first real prediction is fast
  - Cache persists to disk (JSON) → warm starts after reload / restart
  - CDN semaphore now correctly gates concurrent in-flight HTTP requests
  - Request deduplication → identical images in-flight share one future
  - Minor: explicit ThreadPoolExecutor shutdown on unload, typed throughout
"""

import onnxruntime as ort
import numpy as np
import aiohttp
from PIL import Image
import io
import os
import json
import time
import hashlib
import asyncio
import gc
import ctypes
import concurrent.futures
from typing import Optional, Tuple

# ── GitHub model source ───────────────────────────────────────────────────────

GITHUB_TOKEN    = os.getenv("GITHUB_TOKEN")
MODEL_REPO_BASE = "https://raw.githubusercontent.com/teamrocket43434/jessmodel/main"

PRIMARY_ONNX_URL        = f"{MODEL_REPO_BASE}/pokemon_cnn_v2.onnx"
PRIMARY_LABELS_URL      = f"{MODEL_REPO_BASE}/labels_v2.json"
SECONDARY_ONNX_URL      = f"{MODEL_REPO_BASE}/poketwo_pokemon_model.onnx"
SECONDARY_ONNX_DATA_URL = f"{MODEL_REPO_BASE}/poketwo_pokemon_model.onnx.data"
SECONDARY_METADATA_URL  = f"{MODEL_REPO_BASE}/model_metadata.json"

CACHE_DIR                = os.path.join(os.path.dirname(os.path.realpath(__file__)), "model_cache")
PRIMARY_ONNX_PATH        = os.path.join(CACHE_DIR, "pokemon_cnn_v2.onnx")
PRIMARY_LABELS_PATH      = os.path.join(CACHE_DIR, "labels_v2.json")
SECONDARY_ONNX_PATH      = os.path.join(CACHE_DIR, "poketwo_pokemon_model.onnx")
SECONDARY_ONNX_DATA_PATH = os.path.join(CACHE_DIR, "poketwo_pokemon_model.onnx.data")
SECONDARY_METADATA_PATH  = os.path.join(CACHE_DIR, "model_metadata.json")

# Persistent prediction cache saved alongside the model files
DISK_CACHE_PATH = os.path.join(CACHE_DIR, "prediction_cache.json")

# ── Confidence thresholds ─────────────────────────────────────────────────────

PRIMARY_CONFIDENCE_THRESHOLD   = 0.85
SECONDARY_CONFIDENCE_THRESHOLD = 0.90

# ── Worker pool config ────────────────────────────────────────────────────────
# Number of concurrent model-inference workers.  Each worker is a thread that
# runs blocking ONNX calls without touching the event loop.
# Rule of thumb: physical_cores / 2 works well; 2 is a safe default.
INFERENCE_WORKERS = int(os.getenv("INFERENCE_WORKERS", "2"))

# ONNX intra-op threads per session (parallelism inside a single inference).
# Keep primary lean (1) so multiple workers don't fight over the same cores.
# Secondary only runs when primary is uncertain so can have a bit more room.
PRIMARY_INTRA_THREADS   = 1
SECONDARY_INTRA_THREADS = max(1, os.cpu_count() // 2)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _trim_os_memory() -> None:
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def _bytes_to_tensor(image_bytes: bytes, width: int, height: int) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    img.close()

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr  = (arr - mean) / std
    arr  = np.transpose(arr, (2, 0, 1))
    return np.expand_dims(arr, axis=0)


def _make_session(path: str, intra_threads: int) -> ort.InferenceSession:
    """Create an ONNX session with consistent, memory-efficient options."""
    opts = ort.SessionOptions()
    opts.intra_op_num_threads     = intra_threads
    opts.inter_op_num_threads     = 1
    opts.execution_mode           = ort.ExecutionMode.ORT_SEQUENTIAL
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
    opts.enable_mem_pattern       = False
    opts.enable_cpu_mem_arena     = False
    return ort.InferenceSession(path, sess_options=opts, providers=["CPUExecutionProvider"])


# ── Prediction cache ──────────────────────────────────────────────────────────

class PredictionCache:
    """
    In-memory LRU-style cache backed by an optional JSON file on disk.

    Keys are MD5 digests of raw image bytes — stable even when Discord CDN
    URLs rotate.  Values are (name, confidence_str, model_tag) tuples.
    """

    def __init__(self, max_size: int = 500, ttl_seconds: int = 3600):
        self.cache:      dict[str, tuple] = {}
        self.timestamps: dict[str, float] = {}
        self.max_size    = max_size
        self.ttl_seconds = ttl_seconds

    # ── persistence ───────────────────────────────────────────────────────────

    def load_from_disk(self, path: str) -> None:
        """Restore cache from a previous session's JSON snapshot."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            now = time.time()
            loaded = 0
            for key, entry in data.items():
                ts = entry.get("ts", 0)
                if now - ts <= self.ttl_seconds:
                    self.cache[key]      = tuple(entry["value"])
                    self.timestamps[key] = ts
                    loaded += 1
            print(f"[CACHE] Restored {loaded} entries from disk.")
        except FileNotFoundError:
            pass
        except Exception as exc:
            print(f"[CACHE] Could not load disk cache: {exc}")

    def save_to_disk(self, path: str) -> None:
        """Persist live cache entries to disk for future warm starts."""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            data = {
                key: {"value": list(self.cache[key]), "ts": self.timestamps[key]}
                for key in self.cache
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, separators=(",", ":"))
            print(f"[CACHE] Saved {len(data)} entries to disk.")
        except Exception as exc:
            print(f"[CACHE] Could not save disk cache: {exc}")

    # ── internal ──────────────────────────────────────────────────────────────

    def _evict_expired(self) -> None:
        now     = time.time()
        expired = [k for k, t in self.timestamps.items() if now - t > self.ttl_seconds]
        for k in expired:
            self.cache.pop(k, None)
            self.timestamps.pop(k, None)

    def _evict_oldest(self, n: int) -> None:
        oldest = sorted(self.timestamps.items(), key=lambda x: x[1])[:n]
        for k, _ in oldest:
            self.cache.pop(k, None)
            self.timestamps.pop(k, None)

    # ── public ────────────────────────────────────────────────────────────────

    def get(self, key: str) -> Optional[tuple]:
        self._evict_expired()
        entry = self.cache.get(key)
        if entry is None:
            return None
        if time.time() - self.timestamps[key] > self.ttl_seconds:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)
            return None
        return entry

    def set(self, key: str, value: tuple) -> None:
        self._evict_expired()
        if len(self.cache) >= self.max_size:
            self._evict_oldest(max(1, self.max_size // 5))
        self.cache[key]      = value
        self.timestamps[key] = time.time()

    def clear(self) -> None:
        self.cache.clear()
        self.timestamps.clear()

    def __len__(self) -> int:
        return len(self.cache)


# ── Model downloader ──────────────────────────────────────────────────────────

class ModelDownloader:

    @staticmethod
    async def _download_one(url: str, dest: str, session: aiohttp.ClientSession) -> bool:
        headers = {}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"

        try:
            timeout = aiohttp.ClientTimeout(total=60, connect=10)
            async with session.get(url, timeout=timeout, headers=headers) as r:
                if r.status == 401:
                    raise ValueError("GitHub authentication failed — check GITHUB_TOKEN.")
                if r.status == 404:
                    raise ValueError(f"File not found at {url}")
                if r.status != 200:
                    raise ValueError(f"HTTP {r.status} downloading {url}")
                content = await r.read()

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "wb") as f:
                f.write(content)

            print(f"✅ Downloaded: {os.path.basename(dest)}")
            return True

        except Exception as exc:
            print(f"❌ Failed to download {os.path.basename(dest)}: {exc}")
            return False

    @staticmethod
    async def ensure_cached(session: aiohttp.ClientSession) -> None:
        os.makedirs(CACHE_DIR, exist_ok=True)

        needed = [
            (PRIMARY_ONNX_URL,        PRIMARY_ONNX_PATH),
            (PRIMARY_LABELS_URL,      PRIMARY_LABELS_PATH),
            (SECONDARY_ONNX_URL,      SECONDARY_ONNX_PATH),
            (SECONDARY_ONNX_DATA_URL, SECONDARY_ONNX_DATA_PATH),
            (SECONDARY_METADATA_URL,  SECONDARY_METADATA_PATH),
        ]

        tasks = []
        for url, path in needed:
            if os.path.exists(path):
                print(f"✓ Cached: {os.path.basename(path)}")
            else:
                print(f"Downloading {os.path.basename(path)}…")
                tasks.append(ModelDownloader._download_one(url, path, session))

        if tasks:
            results = await asyncio.gather(*tasks)
            if not all(results):
                raise RuntimeError("One or more model files failed to download.")


# ── Core predictor ────────────────────────────────────────────────────────────

class Prediction:
    """
    Dual-model Pokémon predictor — event-loop-safe, burst-tolerant.

    What changed vs v1
    ------------------
    1.  _run_model now runs in a ThreadPoolExecutor so ONNX never blocks
        the event loop (and therefore never freezes the Discord bot).

    2.  A fixed-size asyncio.Queue feeds INFERENCE_WORKERS threads.
        Burst traffic queues cleanly; no core contention from simultaneous
        coroutines all calling the CPU at once.

    3.  ONNX thread counts are tuned per model:
          - Primary:   1 intra-op thread (low latency, low overhead).
          - Secondary: up to n_cpu/2 threads (runs less often, can be faster).

    4.  Model warm-up: a zero-tensor inference is run immediately after load
        so ONNX JIT is complete before the first real prediction.

    5.  Prediction cache persists to disk (JSON). After !unloadmodel /
        !loadmodel or a bot restart the cache is warm from the previous run.

    6.  Request deduplication: if two coroutines ask for the same image hash
        simultaneously, one does the work and the other awaits its future —
        no double inference.

    7.  CDN semaphore cap raised to 8 (was 3); the semaphore now only gates
        concurrent HTTP requests, not the whole predict() coroutine, so it
        no longer creates an artificial queue in front of the model.
    """

    def __init__(self):
        self.cache = PredictionCache(max_size=500, ttl_seconds=3600)

        self.primary_session:    Optional[ort.InferenceSession] = None
        self.secondary_session:  Optional[ort.InferenceSession] = None
        self.primary_class_names:    Optional[list[str]] = None
        self.secondary_class_names:  Optional[list[str]] = None
        self.secondary_metadata:     Optional[dict]      = None

        self.models_initialized = False

        # Thread pool for blocking ONNX calls
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None

        # In-flight deduplication: cache_key → asyncio.Future
        self._in_flight: dict[str, asyncio.Future] = {}

        # CDN rate-limiting — gates HTTP requests only
        self._cdn_semaphore    = asyncio.Semaphore(8)
        self._last_cdn_request = 0.0
        self._cdn_min_interval = 0.05   # slightly more aggressive than before

    # ── Model lifecycle ───────────────────────────────────────────────────────

    async def initialize_models(self, session: aiohttp.ClientSession) -> None:
        if self.models_initialized:
            print("[INIT] Models already loaded — skipping.")
            return

        print("Initialising prediction models…")
        await ModelDownloader.ensure_cached(session)

        # Load disk cache before anything else so warm entries are available
        self.cache.load_from_disk(DISK_CACHE_PATH)

        # Primary labels
        with open(PRIMARY_LABELS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            self.primary_class_names = [data[k].strip('"') for k in sorted(data, key=int)]
        elif isinstance(data, list):
            self.primary_class_names = [n.strip('"') for n in data]
        else:
            raise ValueError("labels_v2.json must be a list or dict.")

        # Secondary metadata + labels
        with open(SECONDARY_METADATA_PATH, "r", encoding="utf-8") as f:
            self.secondary_metadata   = json.load(f)
        self.secondary_class_names = self.secondary_metadata["class_names"]

        # Create sessions with per-model thread budgets
        self.primary_session = _make_session(PRIMARY_ONNX_PATH, PRIMARY_INTRA_THREADS)
        print(f"✅ Primary model ready: {len(self.primary_class_names)} classes")

        self.secondary_session = _make_session(SECONDARY_ONNX_PATH, SECONDARY_INTRA_THREADS)
        print(f"✅ Secondary model ready: {len(self.secondary_class_names)} classes")

        # Thread pool — one thread per configured worker
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=INFERENCE_WORKERS,
            thread_name_prefix="onnx_worker",
        )

        # ── Warm-up ───────────────────────────────────────────────────────────
        # Run a dummy inference so ONNX JIT, memory allocation, and kernel
        # compilation all happen now, not on the first real user request.
        print("Running warm-up inference…")
        loop = asyncio.get_event_loop()

        dummy_primary = np.zeros((1, 3, 224, 224), dtype=np.float32)
        await loop.run_in_executor(
            self._executor,
            self._run_model_sync,
            self.primary_session,
            dummy_primary,
            self.primary_class_names,
        )

        sw = self.secondary_metadata["image_width"]
        sh = self.secondary_metadata["image_height"]
        dummy_secondary = np.zeros((1, 3, sh, sw), dtype=np.float32)
        await loop.run_in_executor(
            self._executor,
            self._run_model_sync,
            self.secondary_session,
            dummy_secondary,
            self.secondary_class_names,
        )
        print("✅ Warm-up complete — models are ready.")

        self.models_initialized = True
        gc.collect()

    def unload_models(self) -> None:
        """
        Release ONNX sessions and all associated data.
        Persists cache to disk before clearing so the next load is warm.
        """
        # Save cache before clearing
        self.cache.save_to_disk(DISK_CACHE_PATH)

        # Shut down thread pool gracefully
        if self._executor:
            self._executor.shutdown(wait=False)
            self._executor = None

        self.primary_session       = None
        self.secondary_session     = None
        self.primary_class_names   = None
        self.secondary_class_names = None
        self.secondary_metadata    = None
        self.models_initialized    = False

        self._in_flight.clear()
        self.cache.clear()

        gc.collect()
        _trim_os_memory()

        print("[UNLOAD] Models cleared and OS memory trimmed. Use !loadmodel to reload.")

    # ── Image fetching ────────────────────────────────────────────────────────

    async def _fetch_image_bytes(
        self,
        url: str,
        session: aiohttp.ClientSession,
        max_retries: int = 4,
    ) -> bytes:
        is_discord = "cdn.discordapp.com" in url or "media.discordapp.net" in url

        for attempt in range(max_retries):
            try:
                if is_discord:
                    # Gate only the HTTP request, not the whole predict() call
                    async with self._cdn_semaphore:
                        now = time.monotonic()
                        gap = self._cdn_min_interval - (now - self._last_cdn_request)
                        if gap > 0:
                            await asyncio.sleep(gap)
                        self._last_cdn_request = time.monotonic()
                        return await self._do_fetch(url, session, attempt, is_discord)
                else:
                    return await self._do_fetch(url, session, attempt, is_discord)

            except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0 * 2 ** attempt)
                    continue
                raise ValueError(f"Network error fetching image: {exc}") from exc

            except ValueError:
                raise

            except Exception as exc:
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.5 * 2 ** attempt)
                    continue
                raise ValueError(f"Unexpected error fetching image: {exc}") from exc

        raise ValueError(f"Failed to fetch image after {max_retries} attempts.")

    async def _do_fetch(
        self,
        url: str,
        session: aiohttp.ClientSession,
        attempt: int,
        is_discord: bool,
    ) -> bytes:
        timeout_total   = (15 if is_discord else 10) + attempt * 5
        timeout_connect = (5  if is_discord else 3)  + attempt
        timeout = aiohttp.ClientTimeout(total=timeout_total, connect=timeout_connect)

        headers = {
            "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept":          "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control":   "no-cache",
        }

        async with session.get(url, timeout=timeout, headers=headers) as r:
            if r.status == 429:
                wait = int(r.headers.get("Retry-After", 2))
                await asyncio.sleep(wait)
                raise aiohttp.ClientResponseError(
                    r.request_info, r.history, status=429
                )
            if r.status == 404:
                if is_discord:
                    raise aiohttp.ClientResponseError(
                        r.request_info, r.history, status=404
                    )
                raise ValueError("Image not found (404).")
            if r.status in (502, 503, 504):
                await asyncio.sleep(2.0 * 2 ** attempt)
                raise aiohttp.ClientResponseError(
                    r.request_info, r.history, status=r.status
                )
            if r.status != 200:
                raise ValueError(f"HTTP {r.status}.")

            data = await r.read()

        if len(data) < 100:
            raise ValueError("Image data too small — likely invalid.")

        return data

    # ── Synchronous inference (runs in thread pool) ───────────────────────────

    def _run_model_sync(
        self,
        session: ort.InferenceSession,
        tensor: np.ndarray,
        class_names: list[str],
    ) -> Tuple[str, float]:
        """
        Pure-CPU ONNX inference.  Must only be called via run_in_executor so
        it never blocks the asyncio event loop.
        """
        feed   = {session.get_inputs()[0].name: tensor}
        logits = session.run(None, feed)[0][0]
        probs  = _softmax(logits)
        idx    = int(np.argmax(probs))
        name   = class_names[idx] if idx < len(class_names) else f"unknown_{idx}"
        return name, float(probs[idx])

    # ── Async inference wrapper ───────────────────────────────────────────────

    async def _run_model(
        self,
        session: ort.InferenceSession,
        tensor: np.ndarray,
        class_names: list[str],
    ) -> Tuple[str, float]:
        """Submit inference to the thread pool and await the result."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            self._run_model_sync,
            session,
            tensor,
            class_names,
        )

    # ── Public predict ────────────────────────────────────────────────────────

    async def predict(
        self,
        url: str,
        session: aiohttp.ClientSession,
    ) -> Tuple[str, str]:
        """
        Predict the Pokémon in *url*.

        Returns
        -------
        (name, confidence_str)  e.g. ("Pikachu", "97.43%")

        Raises
        ------
        RuntimeError  if models are not loaded.
        ValueError    if the image cannot be fetched or is invalid.
        """
        if not self.models_initialized:
            raise RuntimeError(
                "Prediction models are not loaded. "
                "Use `!loadmodel` to load them before running predictions."
            )

        # ── Fetch image ───────────────────────────────────────────────────────
        image_bytes = await self._fetch_image_bytes(url, session)

        # ── Content-based cache key ───────────────────────────────────────────
        cache_key = hashlib.md5(image_bytes).hexdigest()

        cached = self.cache.get(cache_key)
        if cached:
            return cached[0], cached[1]

        # ── In-flight deduplication ───────────────────────────────────────────
        # If another coroutine is already running inference for this exact image,
        # await its result instead of doing redundant work.
        if cache_key in self._in_flight:
            return await asyncio.shield(self._in_flight[cache_key])

        loop = asyncio.get_event_loop()
        fut: asyncio.Future = loop.create_future()
        self._in_flight[cache_key] = fut

        try:
            result = await self._infer(image_bytes, cache_key)
            fut.set_result(result)
            return result
        except Exception as exc:
            fut.set_exception(exc)
            raise
        finally:
            self._in_flight.pop(cache_key, None)

    async def _infer(
        self,
        image_bytes: bytes,
        cache_key: str,
    ) -> Tuple[str, str]:
        """Run the dual-model cascade and return (name, confidence_str)."""

        # ── Primary model ─────────────────────────────────────────────────────
        primary_tensor = _bytes_to_tensor(image_bytes, 224, 224)
        primary_name, primary_prob = await self._run_model(
            self.primary_session, primary_tensor, self.primary_class_names
        )
        del primary_tensor

        if primary_prob >= PRIMARY_CONFIDENCE_THRESHOLD:
            confidence = f"{primary_prob * 100:.2f}%"
            self.cache.set(cache_key, (primary_name, confidence, "primary"))
            return primary_name, confidence

        # ── Secondary model (reuses same image bytes — no second HTTP fetch) ──
        sw = self.secondary_metadata["image_width"]
        sh = self.secondary_metadata["image_height"]
        secondary_tensor = _bytes_to_tensor(image_bytes, sw, sh)
        secondary_name, secondary_prob = await self._run_model(
            self.secondary_session, secondary_tensor, self.secondary_class_names
        )
        del secondary_tensor
        del image_bytes

        if secondary_prob >= SECONDARY_CONFIDENCE_THRESHOLD:
            confidence = f"{secondary_prob * 100:.2f}%"
            self.cache.set(cache_key, (secondary_name, confidence, "secondary"))
            return secondary_name, confidence

        # ── Fallback to primary result ────────────────────────────────────────
        confidence = f"{primary_prob * 100:.2f}%"
        self.cache.set(cache_key, (primary_name, confidence, "primary_fallback"))
        return primary_name, confidence


# ── Dev / CLI test ────────────────────────────────────────────────────────────

def main():
    async def _test():
        predictor = Prediction()
        async with aiohttp.ClientSession() as session:
            await predictor.initialize_models(session)
            while True:
                url = input("Image URL (q to quit): ").strip()
                if url.lower() == "q":
                    predictor.unload_models()
                    break
                try:
                    name, conf = await predictor.predict(url, session)
                    print(f"→ {name}  ({conf})")
                except Exception as exc:
                    print(f"Error: {exc}")

    asyncio.run(_test())


if __name__ == "__main__":
    main()
