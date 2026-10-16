"""Connected Google Drive export boundary -- no Drive API calls or credential handling.

A trusted orchestration layer obtains bytes and revision metadata through its
user-authorized connector, then passes the snapshot here. Read-only by design.
"""
from dataclasses import dataclass
import re
from fcf.kernel import FCFError, observed_source

_DRIVE_ID = re.compile(r"^[A-Za-z0-9_-]{8,200}$")


@dataclass
class DriveExportReader:
    def capture_export(self, *, project_id: str, file_id: str, revision_id: str,
                       exported_bytes: bytes, export_mime_type: str):
        if not _DRIVE_ID.fullmatch(file_id):
            raise FCFError("invalid Drive file identifier")
        if not isinstance(revision_id, str) or not revision_id.strip():
            raise FCFError("Drive revision or source version required")
        record = observed_source(project_id=project_id,
                                 source_system="google_drive",
                                 source_uri=f"gdrive://files/{file_id}",
                                 revision=revision_id,
                                 content=exported_bytes,
                                 mime_type=export_mime_type)
        return record, exported_bytes
