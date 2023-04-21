from __future__ import annotations


class Link:
    def __init__(
        self,
        display_name: str,
        name: str,
        ip: str,
        zerotier_ip: str,
        port: str,
        path: str = None,
    ) -> Link:
        self._display_name = display_name
        self._name = name
        self._ip = ip
        self._zerotier_ip = zerotier_ip
        self._port = port
        self._path = path

    @staticmethod
    def fromJSON(json: dict) -> Link:
        return Link(
            json["display_name"],
            json["name"],
            json["ip"],
            json["zerotier_ip"],
            json["port"],
            json.get("path", None),
        )

    def getFullUrl(self, zerotier: bool = False) -> str:
        if zerotier:
            return self.zerotier_url

        return self.url

    @property
    def url(self) -> str:
        if self._path is None:
            return f"http://{self._ip}:{self._port}"

        return f"http://{self._ip}:{self._port}/{self._path}"

    @property
    def zerotier_url(self) -> str:
        if self._path is None:
            return f"http://{self._zerotier_ip}:{self._port}"

        return f"http://{self._zerotier_ip}:{self._port}/{self._path}"
