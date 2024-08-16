import vtk, os

import dicom_reader

STANDARD = [
    {
        "name": 'air',
        "range": [-1000],
        "color": [[0, 0, 0]]
    },
    {
        "name": 'lung',
        "range": [-600, -400],
        "color": [[194 / 255, 105 / 255, 82 / 255]]
    },
    {
        "name": 'fat',
        "range": [-100, -60],
        "color": [[194 / 255, 166 / 255, 115 / 255]]
    },
    {
        "name": 'soft tissue',
        "range": [40, 80],
        "color": [[102 / 255, 0, 0], [153 / 255, 0, 0]] # red
    },
    {
        "name": 'bone',
        "range": [400, 1000],
        "color": [[255 / 255, 217 / 255, 163 / 255]] # ~ white
    }
]

def to_rgb_points(colormap):
    rgb_points = []
    for item in colormap:
        crange = item["range"]
        color = item["color"]
        for idx, r in enumerate(crange):
            if len(color) == len(crange):
                rgb_points.append([r] + color[idx])
            else:
                rgb_points.append([r] + color[0])
    return rgb_points

class Volume:
    def __init__(self) -> None:
        self.colors = vtk.vtkNamedColors()
        self.initialize()

    def initialize(self) -> None:
        self.reader = vtk.vtkDICOMImageReader()
        self.mapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
        self.volumeProperty = vtk.vtkVolumeProperty()
        self.scalarOpacity = vtk.vtkPiecewiseFunction()
        self.colorTransferFunction = vtk.vtkColorTransferFunction()
        self.volume = vtk.vtkVolume()
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindowInteractor = vtk.vtkRenderWindowInteractor()
        self.interactorStyle = vtk.vtkInteractorStyleTrackballCamera()
        self.renderWindowInteractor.SetInteractorStyle(self.interactorStyle)
        self.setupRenderWindow()

    def setupRenderWindow(self) -> None:
        self.renderWindow.SetSize(1000, 500)
        self.renderWindow.AddRenderer(self.renderer)
        self.renderWindow.SetInteractor(self.renderWindowInteractor)

    def setLighting(self, ambientValue: float = 0.1, diffuseValue: float = 0.9, specularValue: float = 0.2, specularPower: float = 10) -> None:
        self.volumeProperty.SetAmbient(ambientValue)
        self.volumeProperty.SetDiffuse(diffuseValue)
        self.volumeProperty.SetSpecular(specularValue)
        self.volumeProperty.SetSpecularPower(specularPower)

    def colorMapping(self) -> None:
        rgb_points = to_rgb_points(STANDARD)
        for rgb_point in rgb_points:
            self.colorTransferFunction.AddRGBPoint(rgb_point[0], rgb_point[1], rgb_point[2], rgb_point[3])
        self.volumeProperty.SetColor(self.colorTransferFunction)

    def scalarOpacityMapping(self) -> None:
        self.scalarOpacity.AddPoint(184.129411764706, 0)
        self.scalarOpacity.AddPoint(2271.070588235294, 1)
        self.volumeProperty.SetScalarOpacity(self.scalarOpacity)
    
    def show(self, directory: str) -> None:
        self.reader.SetDirectoryName(directory)
        self.reader.Update()
        imageData = self.reader.GetOutput()

        self.mapper.UseJitteringOn()
        self.mapper.SetBlendModeToComposite()
        self.mapper.SetInputData(imageData)

        self.volumeProperty.SetInterpolationTypeToLinear()
        self.colorMapping()
        self.scalarOpacityMapping()

        self.volumeProperty.ShadeOn()
        self.setLighting(0.1, 0.9, 0.2, 10)

        self.volume.SetMapper(self.mapper)
        self.volume.SetProperty(self.volumeProperty)

        self.renderer.AddVolume(self.volume)
        self.renderWindow.Render()
    
        self.renderWindowInteractor.Start()

if __name__ == "__main__":
    test = "/home/itadmin/truong/viewer server/viewer-core/server3d/data/1.2.840.113619.2.415.3.2831155460.426.1717906512.373/1.2.840.113619.2.415.3.2831155460.426.1717906512.378/data"
    directory = "/home/itadmin/truong/dicom/79f8a530-24ddc3f3-c163e5d0-96faead7-25bd5f3a/2408059658 LE VAN CAT 1974M/604662 CHUP CONG HUONG TU NAO MACH NAO XOANG/MR Ax DWI B1000"

    patientsGroup = dicom_reader.yGetDicomGroups(directory)
    for patientGroup in patientsGroup:
        group_keys = patientGroup.groups_dict.keys()
        if group_keys == 1:
            print("hello")
            break
        for group_key in group_keys:
            if group_key[4] == 0:
                fileNameList = patientGroup.groups_dict.get(group_key).GetFilenameList()
                for fileName in fileNameList:
                    os.remove(fileName)

    volume = Volume()
    volume.show(directory)
