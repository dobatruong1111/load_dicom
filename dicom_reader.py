import gdcm, os

import constants as const
import utils as utils
import dicom as dicom
import dicom_grouper as dicom_grouper

tag_labels = {}
main_dict = {}
dict_file = {}

class LoadDicom:
    def __init__(self, grouper, filepath):
        self.grouper = grouper
        self.filepath = utils.decode(filepath, const.FS_ENCODE)
        self.run()

    def run(self):
        grouper = self.grouper
        reader = gdcm.ImageReader()
        try:
            reader.SetFileName(utils.encode(self.filepath, const.FS_ENCODE))
        except TypeError:
            reader.SetFileName(self.filepath)
        if reader.Read():
            file = reader.GetFile()
            # Retrieve data set
            dataSet = file.GetDataSet()
            # Retrieve header
            header = file.GetHeader()
            stf = gdcm.StringFilter()
            stf.SetFile(file)

            data_dict = {}

            tag = gdcm.Tag(0x0008, 0x0005)
            ds = reader.GetFile().GetDataSet()
            image_helper = gdcm.ImageHelper()
            data_dict["spacing"] = image_helper.GetSpacingValue(reader.GetFile())
            if ds.FindDataElement(tag):
                data_element = ds.GetDataElement(tag)
                if data_element.IsEmpty():
                    encoding_value = "ISO_IR 100"
                else:
                    encoding_value = str(ds.GetDataElement(tag).GetValue()).split("\\")[0]

                if encoding_value.startswith("Loaded"):
                    encoding = "ISO_IR 100"
                else:
                    try:
                        encoding = const.DICOM_ENCODING_TO_PYTHON[encoding_value]
                    except KeyError:
                        encoding = "ISO_IR 100"
            else:
                encoding = "ISO_IR 100"

            # Iterate through the Header
            iterator = header.GetDES().begin()
            while not iterator.equal(header.GetDES().end()):
                dataElement = iterator.next()
                if not dataElement.IsUndefinedLength():
                    tag = dataElement.GetTag()
                    data = stf.ToStringPair(tag)
                    stag = tag.PrintAsPipeSeparatedString()

                    group = str(tag.GetGroup())
                    field = str(tag.GetElement())

                    tag_labels[stag] = data[0]

                    if not group in data_dict.keys():
                        data_dict[group] = {}

                    if not (utils.VerifyInvalidPListCharacter(data[1])):
                        data_dict[group][field] = utils.decode(data[1], encoding)
                    else:
                        data_dict[group][field] = "Invalid Character"

            # Iterate through the Data set
            iterator = dataSet.GetDES().begin()
            while not iterator.equal(dataSet.GetDES().end()):
                dataElement = iterator.next()
                if not dataElement.IsUndefinedLength():
                    tag = dataElement.GetTag()
                    data = stf.ToStringPair(tag)
                    stag = tag.PrintAsPipeSeparatedString()

                    group = str(tag.GetGroup())
                    field = str(tag.GetElement())

                    tag_labels[stag] = data[0]

                    if not group in data_dict.keys():
                        data_dict[group] = {}

                    if not (utils.VerifyInvalidPListCharacter(data[1])):
                        data_dict[group][field] = utils.decode(data[1], encoding, "replace")
                    else:
                        data_dict[group][field] = "Invalid Character"

            img = reader.GetImage()

            # ------ Verify the orientation --------------------------------

            direc_cosines = img.GetDirectionCosines()
            orientation = gdcm.Orientation()
            try:
                _type = orientation.GetType(tuple(direc_cosines))
            except TypeError:
                _type = orientation.GetType(direc_cosines)
            label = orientation.GetLabel(_type)

            # ---------- Refactory --------------------------------------
            data_dict["invesalius"] = {"orientation_label": label}

            # -------------------------------------------------------------
            dict_file[self.filepath] = data_dict
            print(f"dict_file: {dict_file}")

            # ---------- Verify is DICOMDir -------------------------------
            is_dicom_dir = 1
            try:
                if data_dict[str(0x002)][str(0x002)] != "1.2.840.10008.1.3.10":
                    is_dicom_dir = 0
            except KeyError:
                is_dicom_dir = 0

            if not (is_dicom_dir):
                parser = dicom.Parser()
                parser.SetDataImage(dict_file[self.filepath], self.filepath)

                dcm = dicom.Dicom()
                dcm.SetParser(parser)
                grouper.AddFile(dcm)

def yGetDicomGroups(directory, recursive=True, gui=True):
    """
    Return all full paths to DICOM files inside given directory.
    """
    nfiles = 0
    # Find total number of files
    if recursive:
        for dirpath, dirnames, filenames in os.walk(directory):
            nfiles += len(filenames)
    else:
        dirpath, dirnames, filenames = os.walk(directory)
        nfiles = len(filenames)

    counter = 0
    grouper = dicom_grouper.DicomPatientGrouper()
    if recursive:
        for dirpath, dirnames, filenames in os.walk(directory):
            for name in filenames:
                filepath = os.path.join(dirpath, name)
                counter += 1
                if gui:
                    # yield (counter, nfiles)
                    pass
                LoadDicom(grouper, filepath)
    else:
        dirpath, dirnames, filenames = os.walk(directory)
        for name in filenames:
            filepath = str(os.path.join(dirpath, name))
            counter += 1
            if gui:
                # yield (counter, nfiles)
                pass
    # yield grouper.GetPatientsGroups()
    return grouper.GetPatientsGroups()

def GetDicomGroups(directory, recursive=True):
    return next(yGetDicomGroups(directory, recursive, gui=False))

if __name__ == "__main__":
    directory = "/home/itadmin/truong/dicom/79f8a530-24ddc3f3-c163e5d0-96faead7-25bd5f3a/2408059658 LE VAN CAT 1974M/604662 CHUP CONG HUONG TU NAO MACH NAO XOANG/MR Ax DWI B1000"
    
    patientsGroups = yGetDicomGroups(directory)
    print(type(patientsGroups))
    