"""Docker sandbox backend implementation."""

from __future__ import annotations

import io
import tarfile
from typing import TYPE_CHECKING

from nami_deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
)
from nami_deepagents.backends.sandbox import BaseSandbox

if TYPE_CHECKING:
    import docker
    from docker.models.containers import Container


class DockerBackend(BaseSandbox):
    """Docker backend implementation conforming to SandboxBackendProtocol.

    This implementation inherits all file operation methods from BaseSandbox
    and implements execute(), download_files(), and upload_files() using Docker's API.
    """

    def __init__(self, container: Container) -> None:
        """Initialize the DockerBackend with a Docker container instance.

        Args:
            container: Active Docker Container instance
        """
        self._container = container
        self._timeout = 30 * 60  # 30 minutes default timeout

    @property
    def id(self) -> str:
        """Unique identifier for the sandbox backend."""
        return self._container.id[:12]  # Use short container ID

    def execute(self, command: str) -> ExecuteResponse:
        """Execute a command in the Docker container and return ExecuteResponse.

        Args:
            command: Full shell command string to execute

        Returns:
            ExecuteResponse with combined output, exit code, and truncation flag
        """
        try:
            # Execute command in container
            exec_result = self._container.exec_run(
                cmd=["bash", "-c", command],
                stdout=True,
                stderr=True,
                stdin=False,
                tty=False,
                demux=False,  # Combine stdout and stderr
            )

            # Decode output
            output = exec_result.output.decode("utf-8") if exec_result.output else ""

            return ExecuteResponse(
                output=output,
                exit_code=exec_result.exit_code,
                truncated=False,  # Docker doesn't provide truncation info
            )

        except Exception as e:
            # Return error as output
            return ExecuteResponse(
                output=f"Error executing command: {e}",
                exit_code=1,
                truncated=False,
            )

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Download multiple files from the Docker container.

        Uses Docker's get_archive() API to retrieve files.

        Args:
            paths: List of file paths to download

        Returns:
            List of FileDownloadResponse objects, one per input path
        """
        responses = []

        for path in paths:
            try:
                # Get archive from container
                bits, stat = self._container.get_archive(path)

                # Extract file content from tar archive
                tar_stream = io.BytesIO()
                for chunk in bits:
                    tar_stream.write(chunk)
                tar_stream.seek(0)

                # Open tar archive and extract file
                with tarfile.open(fileobj=tar_stream, mode="r") as tar:
                    # Get the first (and should be only) member
                    members = tar.getmembers()
                    if members:
                        member = members[0]
                        file_obj = tar.extractfile(member)
                        if file_obj:
                            content = file_obj.read()
                            responses.append(
                                FileDownloadResponse(
                                    path=path,
                                    content=content,
                                    error=None,
                                )
                            )
                        else:
                            responses.append(
                                FileDownloadResponse(
                                    path=path,
                                    content=b"",
                                    error=f"Could not extract file: {path}",
                                )
                            )
                    else:
                        responses.append(
                            FileDownloadResponse(
                                path=path,
                                content=b"",
                                error=f"File not found in archive: {path}",
                            )
                        )

            except Exception as e:
                responses.append(
                    FileDownloadResponse(
                        path=path,
                        content=b"",
                        error=f"Error downloading file: {e}",
                    )
                )

        return responses

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """Upload multiple files to the Docker container.

        Uses Docker's put_archive() API to upload files.

        Args:
            files: List of (path, content) tuples to upload

        Returns:
            List of FileUploadResponse objects, one per input file
        """
        responses = []

        for path, content in files:
            try:
                # Create tar archive in memory
                tar_stream = io.BytesIO()
                with tarfile.open(fileobj=tar_stream, mode="w") as tar:
                    # Create file info
                    tarinfo = tarfile.TarInfo(name=path.split("/")[-1])
                    tarinfo.size = len(content)

                    # Add file to archive
                    tar.addfile(tarinfo, io.BytesIO(content))

                tar_stream.seek(0)

                # Determine target directory
                directory = "/".join(path.split("/")[:-1]) or "/"

                # Upload archive to container
                self._container.put_archive(
                    path=directory,
                    data=tar_stream.read(),
                )

                responses.append(FileUploadResponse(path=path, error=None))

            except Exception as e:
                responses.append(
                    FileUploadResponse(
                        path=path,
                        error=f"Error uploading file: {e}",
                    )
                )

        return responses
