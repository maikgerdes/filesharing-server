import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
NS.update({"w14": "http://schemas.microsoft.com/office/word/2010/wordml"})


def _element_tag(element):
    return element.tag.rsplit("}", 1)[-1]


def _extract_checkbox_state(sdt):
    checked = sdt.find(".//w14:checked", NS)
    if checked is None:
        return None
    value = checked.get("{http://schemas.microsoft.com/office/word/2010/wordml}val")
    if value in {"1", "true", "on"}:
        return "true"
    if value in {"0", "false", "off"}:
        return "false"
    return -1


def _extract_sdt_text(sdt):
    alias = sdt.find("./w:sdtPr/w:alias", NS)
    alias_text = (
        alias.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val")
        if alias is not None
        else ""
    )

    checkbox_state = _extract_checkbox_state(sdt)
    if checkbox_state is not None:
        if alias_text:
            return (f"{alias_text}", f"{checkbox_state}")
        return checkbox_state

    content = sdt.find("./w:sdtContent", NS)
    content_text = _extract_text(content) if content is not None else ""
    if alias_text and content_text:
        return (f"{alias_text}", f"{content_text}")
    return content_text or alias_text


def _extract_text(node):
    if node is None:
        return ""

    parts = []
    for child in list(node):
        tag = _element_tag(child)
        if tag == "t":
            if child.text:
                parts.append(child.text)
        elif tag == "tab":
            parts.append("\t")
        elif tag in {"br", "cr"}:
            parts.append("\n")
        elif tag == "sdt":
            parts.append(_extract_sdt_text(child))
        else:
            parts.append(_extract_text(child))
    return "".join(parts)


def read_doc(path="test.docx"):
    intake_dictionary = {}
    print("\n--- Content Controls & Form Fields (document.xml) ---")
    try:
        with zipfile.ZipFile(path) as z:
            xml = z.read("word/document.xml")
    except Exception as e:
        print("Fehler beim Lesen der docx XML:", e)
        return

    root = ET.fromstring(xml)

    sdt_list = root.findall(".//w:sdt", NS)
    if sdt_list:
        print("\nGefundene Content Controls (sdt):")
        for sdt in sdt_list:
            pair = _extract_sdt_text(sdt)
            if pair:
                intake_dictionary.update({f"{pair[0].strip()}": f"{pair[1].strip()}"})
    return intake_dictionary


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test.docx"
    read_doc(path)
