import hashlib
import pytest
import tempfile

from PySide.QtGui import QAction, QFileDialog


def get_bmp_sha1(filename):
    """
    Get the sha1 hash of the pixel data in a bmp file.

    This is used to check if two bitmaps are identical.
    """
    bitmap_data_offset = 0x36  # skip the BMP header (it's not standard across all platforms)

    with open(filename, 'rb') as f:
        contents = f.read()
        bitmap_data = contents[bitmap_data_offset:]
        bitmap_hash = hashlib.sha1(bitmap_data)

        return bitmap_hash.hexdigest()


def test_screenshot(qtbot, mock):
    """
    Run Ristar for 7000 frames and check if the video output (screenshot) is correct.
    """
    from kiwi import MainWindow, render_filters
    window = MainWindow()
    qtbot.addWidget(window)

    window.display.set_zoom_level(QAction('1x', window))
    mock.patch.object(QFileDialog, 'getOpenFileName', return_value=('./tests/ristar/Ristar (UE) [!].zip', '*.zip'))
    window.display.open_file()

    for i in range(7000):
        window.display.frame()

    assert window.display.frames == 7000

    for scale_factor in ('1x', '2x', '3x', '4x'):
        for render_filter in render_filters:
            window.display.set_zoom_level(QAction(scale_factor, window))
            window.display.set_render_filter(QAction(render_filter, window))

            for i in range(5):
                window.display.frame()

            filename_suffix = '-{}-{}.bmp'.format(scale_factor, render_filter.lower())

            _, filename = tempfile.mkstemp(suffix=filename_suffix)
            window.display.save_screenshot(filename)

            assert get_bmp_sha1(filename) == get_bmp_sha1('./tests/ristar/ristar-screenshot'+filename_suffix)
