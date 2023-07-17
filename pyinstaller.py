import PyInstaller.__main__


def build() -> None:
    PyInstaller.__main__.run(
        [
            "monkey.py",
            "--noconfirm",
            "--windowed",
            "--onefile",
        ]
    )


if __name__ == "__main__":
    build()
