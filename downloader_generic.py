import requests
import threading
import os
import time
from concurrent.futures import ThreadPoolExecutor

class SegmentedFileDownloader:
    def __init__(self, num_threads=8):
        self.num_threads = num_threads
        self._cancel_requested = False
        self.download_thread = None
        self.current_filename = None
        self.temp_dir = None

    def cancel(self):
        self._cancel_requested = True

    def download(self, url, output_path, progress_callback=None, completion_callback=None, error_callback=None, title_callback=None):
        self._cancel_requested = False
        
        def run():
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept-Encoding': 'identity'
                }

                # 1. Get File Info & Resolve Redirects
                try:
                    head = requests.head(url, allow_redirects=True, timeout=10, headers=headers)
                    if head.status_code >= 400:
                        raise Exception(f"HTTP Error: {head.status_code}")
                    
                    # Use the final URL after redirects for actual downloading
                    resolved_url = head.url 
                    total_size = int(head.headers.get('content-length', 0))
                    filename = self._get_filename(resolved_url, head)

                except Exception as e:
                    # Fallback to GET stream if HEAD fails (some servers deny HEAD)
                    # or if HEAD failed for other reasons
                    print(f"HEAD request failed: {e}. Retrying with GET...")
                    r = requests.get(url, stream=True, timeout=10, allow_redirects=True, headers=headers)
                    r.raise_for_status()
                    
                    resolved_url = r.url
                    total_size = int(r.headers.get('content-length', 0))
                    filename = self._get_filename(resolved_url, r)
                    r.close()

                full_path = os.path.join(output_path, filename)
                self.current_filename = full_path
                
                if title_callback:
                    title_callback(filename)
                
                # Check if resume capability is possible (server supports ranges)
                ranges_supported = head.headers.get('Accept-Ranges') == 'bytes' or total_size > 0
                
                if not ranges_supported or total_size == 0:
                    self._download_single_thread(resolved_url, full_path, total_size, progress_callback)
                else:
                    self._download_segmented(resolved_url, full_path, total_size, progress_callback)
                    
                if not self._cancel_requested:
                    if completion_callback:
                        completion_callback(filename)
                else:
                    raise Exception("Download cancelled by user")

            except Exception as e:
                # print(f"Generic Download Error: {e}")
                if "cancelled" in str(e).lower():
                    if error_callback: error_callback("Cancelled")
                    self._cleanup()
                else:
                    if error_callback: error_callback(str(e))
                    self._cleanup()

        self.download_thread = threading.Thread(target=run)
        self.download_thread.start()

    def _get_filename(self, url, response):
        # Try content-disposition
        if "Content-Disposition" in response.headers:
            import re
            fname = re.findall("filename=(.+)", response.headers["Content-Disposition"])
            if fname:
                return fname[0].strip().strip('"')
        # Fallback to URL
        return os.path.basename(url.split("?")[0])

    def _download_single_thread(self, url, filepath, total_size, progress_callback):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Encoding': 'identity'
        }
        with requests.get(url, stream=True, headers=headers) as r:
            r.raise_for_status()
            downloaded = 0
            start_time = time.time()
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if self._cancel_requested:
                        return
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            self._report_progress(downloaded, total_size, start_time, progress_callback)

    def _download_segmented(self, url, filepath, total_size, progress_callback):
        chunk_size = total_size // self.num_threads
        futures = []
        self.downloaded_bytes = 0
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # Temp directory for parts
        self.temp_dir = filepath + "_parts"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            for i in range(self.num_threads):
                start = i * chunk_size
                end = start + chunk_size - 1 if i < self.num_threads - 1 else total_size - 1
                part_file = os.path.join(self.temp_dir, f"part_{i}")
                futures.append(executor.submit(self._download_chunk, url, start, end, part_file, total_size, progress_callback))

            # Wait for all
            for f in futures:
                if f.exception() or self._cancel_requested:
                    raise f.exception() or Exception("Cancelled")

        # Merge
        if not self._cancel_requested:
            with open(filepath, 'wb') as outfile:
                for i in range(self.num_threads):
                    part_file = os.path.join(self.temp_dir, f"part_{i}")
                    with open(part_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            # Cleanup parts
            import shutil
            shutil.rmtree(self.temp_dir)

    def _download_chunk(self, url, start, end, part_path, total_size, progress_callback):
        headers = {
            'Range': f'bytes={start}-{end}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
             'Accept-Encoding': 'identity'
        }
        # Check if part exists to resume (simple) - for now overwrite
        with requests.get(url, headers=headers, stream=True) as r:
            with open(part_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if self._cancel_requested:
                        return
                    if chunk:
                        f.write(chunk)
                        with self.lock:
                            self.downloaded_bytes += len(chunk)
                            if progress_callback:
                                self._report_progress(self.downloaded_bytes, total_size, self.start_time, progress_callback)

    def _report_progress(self, downloaded, total, start_time, callback):
        elapsed = time.time() - start_time
        speed = downloaded / elapsed if elapsed > 0 else 0
        speed_str = f"{speed / 1024 / 1024:.2f} MiB/s"
        
        percent = downloaded / total if total > 0 else 0
        eta = (total - downloaded) / speed if speed > 0 else 0
        eta_str = f"{int(eta)}s"
        
        callback(percent, speed_str, eta_str)

    def _cleanup(self):
        try:
            if self.current_filename and os.path.exists(self.current_filename):
                os.remove(self.current_filename)
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
        except:
            pass
