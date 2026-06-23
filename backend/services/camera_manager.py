import asyncio
from typing import Dict

class CameraManager:
    def __init__(self):
        self.active_tasks: Dict[int, asyncio.Task] = {}
        self.stop_events: Dict[int, asyncio.Event] = {}

    async def start_camera(self, camera_id: int, rtsp_url: str, area_id: int):
        if camera_id in self.active_tasks:
            await self.stop_camera(camera_id)
            
        from services.video_processor import process_video_stream
        
        stop_event = asyncio.Event()
        self.stop_events[camera_id] = stop_event
        
        task = asyncio.create_task(process_video_stream(camera_id, rtsp_url, area_id, stop_event))
        self.active_tasks[camera_id] = task

    async def stop_camera(self, camera_id: int):
        if camera_id in self.stop_events:
            self.stop_events[camera_id].set()
            task = self.active_tasks.get(camera_id)
            if task:
                await task # Wait for it to finish
            del self.stop_events[camera_id]
            if camera_id in self.active_tasks:
                del self.active_tasks[camera_id]

    async def stop_all(self):
        for camera_id in list(self.active_tasks.keys()):
            await self.stop_camera(camera_id)

camera_manager = CameraManager()
