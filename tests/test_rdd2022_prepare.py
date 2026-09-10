from pathlib import Path

from scripts.prepare_rdd2022 import convert_annotation, split_for


def test_convert_rdd2022_annotation(tmp_path: Path):
    xml = tmp_path / "sample.xml"
    xml.write_text(
        """<annotation>
        <filename>sample.jpg</filename>
        <size><width>1000</width><height>500</height></size>
        <object><name>D40</name><bndbox><xmin>100</xmin><ymin>50</ymin><xmax>300</xmax><ymax>250</ymax></bndbox></object>
        <object><name>D00</name><bndbox><xmin>500</xmin><ymin>100</ymin><xmax>700</xmax><ymax>200</ymax></bndbox></object>
        </annotation>""",
        encoding="utf-8",
    )
    labels = convert_annotation(xml)
    assert len(labels) == 2
    assert labels[0].startswith("3 ")
    assert labels[1].startswith("0 ")


def test_split_is_deterministic():
    assert split_for("India/train/abc.xml") == split_for("India/train/abc.xml")
    assert split_for("India/train/abc.xml") in {"train", "val", "test"}
