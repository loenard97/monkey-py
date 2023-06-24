import PyInstaller.__main__


def build():
    PyInstaller.__main__.run(
        [
            "main.py",
            "--noconfirm",
            "--windowed",
            "--onefile",
        ]
    )


if __name__ == "__main__":
    build()
