# Build Shop Manager Pro Qt as a Standalone App

This guide packages the desktop Qt app (`shop_manager_pro_qt.py`) into a single executable that runs without installing Python or any libraries on the target machine.

## Windows (recommended)

1. From the repository root, run:

   `powershell -ExecutionPolicy Bypass -File .\build_qt_win.ps1`

2. Output executable:

   `dist\ShopManagerPro.exe`

The script bundles `PyQt6` and dependencies, and includes the `locales` folder.

## macOS

Build on macOS (you must build on the target OS):

```
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name ShopManagerPro --add-data "locales:locales" shop_manager_pro_qt.py
```

Output app: `dist/ShopManagerPro`

## Linux

Build on Linux:

```
python -m pip install pyinstaller
pyinstaller --noconfirm --clean --onefile --windowed --name ShopManagerPro --add-data "locales:locales" shop_manager_pro_qt.py
```

Output binary: `dist/ShopManagerPro`

## Notes

- Cross-OS packaging requires building on each OS (Windows/Mac/Linux) due to native bundling differences.
- If you add new data assets, include them via `--add-data` or a `.spec` file.
- For code signing or notarization (macOS/Windows), perform those steps after building.
