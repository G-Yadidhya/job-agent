from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

from src.models import Job


class CSVExporter:
    def __init__(self, output_path: str, timestamp_output: bool = False):
        self.output_path = Path(output_path)
        self.timestamp_output = timestamp_output

        if self.output_path.suffix:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            self.output_path.mkdir(parents=True, exist_ok=True)

    def export(self, jobs: List[Job], timestamped: bool = None) -> str:
        if timestamped is None:
            timestamped = self.timestamp_output

        output_path = self.output_path
        if timestamped:
            if not output_path.suffix:
                output_path = output_path / f"jobs-{datetime.utcnow():%Y%m%d-%H%M%S}.csv"
            else:
                output_path = output_path.with_name(
                    f"{output_path.stem}-{datetime.utcnow():%Y%m%d-%H%M%S}{output_path.suffix}"
                )
        elif not output_path.suffix:
            output_path = output_path / "jobs.csv"

        rows = [job.to_dict() for job in jobs]
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        return str(output_path)
