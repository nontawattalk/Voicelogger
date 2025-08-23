from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, Future
from dataclasses import dataclass, field
from typing import Dict, Optional
import uuid, time

@dataclass
class Job:
    id: str
    filename: str
    status: str = "queued"   # queued | running | done | error
    message: str = ""
    result_dir: Optional[str] = None
    created_at: float = field(default_factory=time.time)

class JobQueue:
    def __init__(self, max_workers: int = 2):
        self.exec = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, Job] = {}
        self.futures: Dict[str, Future] = {}

    def submit(self, fn, *, filename: str, **kwargs) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, filename=filename, status="queued")
        self.jobs[job_id] = job

        def wrapper():
            job.status = "running"
            try:
                outdir = fn(**kwargs)
                job.result_dir = outdir
                job.status = "done"
                job.message = "Completed"
            except Exception as e:
                job.status = "error"
                job.message = str(e)

        self.futures[job_id] = self.exec.submit(wrapper)
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

queue = JobQueue()
