from pathlib import Path

from PIL import Image

from scripts.compare_visual_evidence import difference_ratio


def test_visual_difference_ignores_masked_native_widget_area(tmp_path: Path) -> None:
    reference = Image.new("RGB", (4, 4), "white")
    actual = reference.copy()
    actual.putpixel((0, 0), (0, 0, 0))
    mask = Image.new("L", (4, 4), 0)
    mask.putpixel((0, 0), 255)
    reference_path = tmp_path / "reference.png"
    actual_path = tmp_path / "actual.png"
    mask_path = tmp_path / "mask.png"
    reference.save(reference_path)
    actual.save(actual_path)
    mask.save(mask_path)

    assert difference_ratio(reference_path, actual_path) > 0
    assert difference_ratio(reference_path, actual_path, mask_path) == 0
