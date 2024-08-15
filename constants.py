import sys

# PATHS
FS_ENCODE = sys.getfilesystemencoding()

# Correlaction extracted from pyDicom
DICOM_ENCODING_TO_PYTHON = {
    "None": "iso8859",
    None: "iso8859",
    "": "iso8859",
    "ISO_IR 6": "iso8859",
    "ISO_IR 100": "latin_1",
    "ISO 2022 IR 87": "iso2022_jp",
    "ISO 2022 IR 13": "iso2022_jp",
    "ISO 2022 IR 149": "euc_kr",
    "ISO_IR 192": "UTF8",
    "GB18030": "GB18030",
    "ISO_IR 126": "iso_ir_126",
    "ISO_IR 127": "iso_ir_127",
    "ISO_IR 138": "iso_ir_138",
    "ISO_IR 144": "iso_ir_144",
}
