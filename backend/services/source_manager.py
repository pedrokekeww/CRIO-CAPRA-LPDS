import asyncio
from typing import Dict
from .sources.base import BaseSource
from .sources.rtsp import RTSPSource
from .sources.webcam import WebcamSource
from .sources.video_file import VideoFileSource
from .sources.passive import PassiveSource
import schemas

class SourceManager:
    def __init__(self):
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.stop_events: Dict[int, asyncio.Event] = {}
        self.sources: Dict[int, BaseSource] = {}
        self.latest_frames: Dict[int, bytes] = {}

    async def start_source(self, source_id: int, source_data: schemas.VideoSource):
        if source_id in self.active_tasks:
            await self.stop_source(source_id)
            
        from .video_processor import process_video_stream
        
        # Instantiate correct adapter
        source_impl = None
        if source_data.source_type == "RTSP":
            source_impl = RTSPSource(source_data.rtsp_url)
        elif source_data.source_type == "WEBCAM":
            source_impl = WebcamSource(source_data.device_index or 0)
        elif source_data.source_type == "VIDEO_FILE":
            source_impl = VideoFileSource(source_data.file_path, source_data.loop_enabled, source_data.playback_speed)
        elif source_data.source_type == "SCREEN_SHARE":
            source_impl = PassiveSource(is_single_image=False)
        elif source_data.source_type == "IMAGE":
            source_impl = PassiveSource(is_single_image=True)
            
        if not source_impl:
            print(f"Unknown source type: {source_data.source_type}")
            return
            
        self.sources[source_id] = source_impl
        
        stop_event = asyncio.Event()
        self.stop_events[source_id] = stop_event
        
        task = asyncio.create_task(process_video_stream(source_id, source_data.area_id, source_impl, stop_event))
        self.active_tasks[source_id] = task

    async def stop_source(self, source_id: int):
        if source_id in self.stop_events:
            self.stop_events[source_id].set()
            task = self.active_tasks.get(source_id)
            if task:
                await task # Wait for it to finish
            del self.stop_events[source_id]
            if source_id in self.active_tasks:
                del self.active_tasks[source_id]
            if source_id in self.sources:
                del self.sources[source_id]

    async def stop_all(self):
        for source_id in list(self.active_tasks.keys()):
            await self.stop_source(source_id)
            
    def get_source(self, source_id: int) -> BaseSource:
        return self.sources.get(source_id)

source_manager = SourceManager()
