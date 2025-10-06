from zipfile import ZipFile

from posts.usecases.posts.parsing.file_discoverers.base import FileDiscoverer


class ZIPDiscoverer(FileDiscoverer):
    def __init__(self, n_parser_workers: int) -> None:
        super().__init__()
        self._N_PARSER_WORKERS = n_parser_workers

    def set_file(self, zip_file: ZipFile) -> None:
        self._zip_file = zip_file

    async def discover(self) -> None:
        print("zip 1")
        for filename in self._zip_file.namelist():
            print("zip 2")
            if not filename.lower().endswith((".html", ".htm", "-")):
                continue

            print("zip 3")
            with self._zip_file.open(filename) as f:
                print("zip 4")
                html = f.read().decode("utf-8")
                print(type(html))
                await self.file_q.put(html)

        for _ in range(self._N_PARSER_WORKERS):
            await self.file_q.put(None)
