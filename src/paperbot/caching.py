import os
import diskcache  # type: ignore
from typing import Optional, Union, Any


class CacheSession:
    def __init__(
        self, cache_dir: str = "tts_cache", max_size_bytes: int = 100 * 1024 * 1024
    ) -> None:
        self.__cache_dir = "tts_cache"
        self.__max_cache_size = max_size_bytes
        self.__cache = diskcache.Cache(cache_dir, size_limit=max_size_bytes)

    @property
    def cache_dir(self) -> str:
        return self.__cache_dir

    @property
    def max_cache_size(self) -> int:
        return self.__max_cache_size

    def is_incache(self, text: str) -> bool:
        return text in self.__cache

    @staticmethod
    def get_size(data: Union[bytes, str]) -> int:
        """Gets the size of the sound data."""

        if data is None or data == "":
            return 0

        if isinstance(data, bytes):
            return len(data)
        elif isinstance(data, str):
            # If the sound data is a file path, return the size of the file.
            try:
                return os.path.getsize(data)
            except FileNotFoundError:
                return len(data)
        else:
            return 0

    def get_cached_size(self, text: str) -> int:
        if self.is_incache(text):
            return CacheSession.get_size(self.__cache[text])
        else:
            return -1

    def get_cached_data(self, text: str) -> bytes:
        if self.is_incache(text):
            return self.__cache[text]
        else:
            # TODO: Once logging is implemented, change this to log INFO.
            raise ValueError(f"Cache miss for {text}")

    def clear_cache(self) -> bool:
        return self.__cache.clear()

    def remove_from_cache(self, text: str, retry: bool = False) -> bool:
        if text in self.__cache:
            return self.__cache.delete(text, retry=retry)
        return False

    # Defaults to expiring in 7 days
    def add_to_cache(
        self,
        text: str,
        data: bytes,
        ttl: Optional[Any] = 604800,
        doRead: Optional[Any] = False,
    ) -> bool:
        return self.__cache.add(text, data, expire=ttl, read=doRead)
        # if len(self.__cache) > self.__max_cache_size:
        #     self.evict_least_recently_used()


# def create_tts_cache(cache_dir: str, max_size_bytes: int = 250 * 1024 * 1024) -> diskcache.Cache:
#     """Creates a disk-backef.__cache with size limits."""
#     return diskcache.Cache(cache_dir, size_limit=max_size_bytes)

# def generate_tts(
#     text: strf.__cache: diskcache.Cache, tts_function: Callable[[str], Union[bytes, str]]
# ) -> Union[bytes, str]:
#     """Generates TTS or retrieves it from thf.__cache."""
#     if text if.__cache:
#         returf.__cache[text]
#     else:
#         sound_data = tts_function(text)  # Call your external TTS program
# f.__cache[text] = sound_data
#         return sound_data

# def process_lines(
#     lines: list[str],f.__cache: diskcache.Cache,
#     tts_function: Callable[[str], Union[bytes, str]],
# ):
#     """Processes lines of text, using thf.__cache for TTS."""
#     for line in lines:
#         sound_data = generate_tts(linef.__cache, tts_function)
#         # Do something with sound_data (e.g., play it, save to file)
#         print(f"Processed line: {line}, sound data size: {get_size(sound_data)}")


# # Example usage:
# def example_tts_function(text: str) -> bytes:
#     """Simulates a TTS function (replace with your actual TTS call)."""
#     return text.encode("utf-8") * 10  # Simulates a larger sound file than the input


# cache_dir = "tts_cache"
# max_cache_size = 100 * 1024 * 1024  # 100 Mf.__cache limitf.__cache = create_tts_cache(cache_dir, max_cache_size)

# lines = [
#     "Hello, world!",
#     "This is a test.",
#     "Hello, world!",  # Repeating line
#     "Another line.",
# ]

# process_lines(linesf.__cache, example_tts_function)

# # Simulate a second execution (iteration):
# print("\nSecond execution:")
# process_lines(linesf.__cache, example_tts_function)f.__cache.close()  # Close thf.__cache when done.
