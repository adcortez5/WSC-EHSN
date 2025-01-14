# All works in this code have been curated by ECCC and licensed under the GNU General Public License v3.0.
# Read more: https://www.gnu.org/licenses/gpl-3.0.en.html

import wx
import os
import sys
import wx.lib.scrolledpanel as scrolled

class AttachFileFolderBox(scrolled.ScrolledPanel):
    def __init__(self, parent, func, *args, **kwargs):
        super(AttachFileFolderBox, self).__init__(*args, **kwargs)
        self.parent = parent
        self.func = func
        self.manager = None
        self.barSize = (545, -1)
        self.buttonSize = (30, 24)
        self.browseSize = (-1, 24)
        self.labelSize = (190, -1)
        self.buttonList = []
        self.addrList = []
        self.labelList = []
        self.browseList = []
        self.columnList = []
        self.typeList = []
        self.type = ["File", "Folder"]

        # Counts for files and folders
        self.file_count = 0
        self.folder_count = 0

        self.InitUI()

    def InitUI(self):

        self.layoutSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.layoutSizer)
        self.tableSizer = wx.BoxSizer(wx.VERTICAL)
        self.column = wx.BoxSizer(wx.HORIZONTAL)

        self.columnList.append(wx.BoxSizer(wx.HORIZONTAL))

        self.buttonList.append(wx.Button(self, label="-", size=self.buttonSize))
        self.typeList.append(wx.ComboBox(self, style=wx.CB_DROPDOWN|wx.TE_READONLY, choices=self.type))
        self.typeList[-1].SetValue("Folder")
        self.addrList.append(wx.TextCtrl(self, size=self.barSize))
        self.browseList.append(wx.Button(self, label="Browse", size=self.browseSize))
        self.labelList.append(wx.TextCtrl(self, size=self.labelSize, style=wx.TE_READONLY))

        self.buttonList[-1].Bind(wx.EVT_BUTTON, self.add_remove)
        self.browseList[-1].Bind(wx.EVT_BUTTON, self.Browse)

        self.columnList[-1].Add(self.buttonList[-1])
        self.columnList[-1].Add(self.typeList[-1])
        self.columnList[-1].Add(self.addrList[-1])
        self.columnList[-1].Add(self.browseList[-1])
        self.columnList[-1].Add(self.labelList[-1])

        self.tableSizer.Add(self.columnList[-1])

        self.addButton = wx.Button(self, label="+", size=self.buttonSize)
        self.addButton.Bind(wx.EVT_BUTTON, self.add_remove)
        self.column.Add(self.addButton)

        self.layoutSizer.Add(self.tableSizer)
        self.layoutSizer.Add(self.column)
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT)

    def add(self):
        self.columnList.append(wx.BoxSizer(wx.HORIZONTAL))
        self.buttonList.append(wx.Button(self, label="-", size=self.buttonSize))
        self.typeList.append(wx.ComboBox(self, style=wx.CB_DROPDOWN | wx.TE_READONLY, choices=self.type))
        self.typeList[-1].SetValue("Folder")
        self.addrList.append(wx.TextCtrl(self, size=self.barSize))
        self.browseList.append(wx.Button(self, label="Browse", size=self.browseSize))
        self.labelList.append(wx.TextCtrl(self, size=self.labelSize, style=wx.TE_READONLY))

        self.buttonList[-1].Bind(wx.EVT_BUTTON, self.add_remove)
        self.browseList[-1].Bind(wx.EVT_BUTTON, self.Browse)
        self.columnList[-1].Add(self.buttonList[-1])
        self.columnList[-1].Add(self.typeList[-1])
        self.columnList[-1].Add(self.addrList[-1])
        self.columnList[-1].Add(self.browseList[-1])
        self.columnList[-1].Add(self.labelList[-1])

        self.tableSizer.Add(self.columnList[-1])
        self.layoutSizer.Layout()

        self.Update()

    def add_remove(self, evt):
        if evt.GetEventObject().GetLabel() == "+":
            self.columnList.append(wx.BoxSizer(wx.HORIZONTAL))
            self.buttonList.append(wx.Button(self, label="-", size=self.buttonSize))
            self.typeList.append(wx.ComboBox(self, style=wx.CB_DROPDOWN | wx.TE_READONLY, choices=self.type))
            self.typeList[-1].SetValue("Folder")
            self.addrList.append(wx.TextCtrl(self, size=self.barSize))
            self.browseList.append(wx.Button(self, label="Browse", size=self.browseSize))
            self.labelList.append(wx.TextCtrl(self, size=self.labelSize, style=wx.TE_READONLY))

            self.buttonList[-1].Bind(wx.EVT_BUTTON, self.add_remove)
            self.browseList[-1].Bind(wx.EVT_BUTTON, self.Browse)
            self.columnList[-1].Add(self.buttonList[-1])
            self.columnList[-1].Add(self.typeList[-1])
            self.columnList[-1].Add(self.addrList[-1])
            self.columnList[-1].Add(self.browseList[-1])
            self.columnList[-1].Add(self.labelList[-1])

            self.tableSizer.Add(self.columnList[-1])
            self.updateLabels()
            self.layoutSizer.Layout()

            self.Update()

        elif evt.GetEventObject().GetLabel() == "-":
            id = self.buttonList.index(evt.GetEventObject())
            self.buttonList[id].Destroy()
            self.typeList[id].Destroy()
            self.addrList[id].Destroy()
            self.browseList[id].Destroy()
            self.labelList[id].Destroy()
            del self.columnList[id]
            del self.buttonList[id]
            del self.typeList[id]
            del self.addrList[id]
            del self.browseList[id]
            del self.labelList[id]
            self.updateLabels()

            self.layoutSizer.Layout()
            self.Update()
        self.parent.Layout()

    # Update the displayed file labels for the window
    def updateLabels(self):

        # Set the counts for files and folders back to zero
        self.file_count = 0
        self.folder_count = 0

        # Get the station number
        stnNum = self.parent.parent.genInfo.stnNumCmbo.GetValue()
        if stnNum.isspace():
            stnNum = ''
        
        # Get the date
        dateVal = self.parent.parent.genInfo.datePicker.GetValue().Format(self.parent.fm)

        # Iterate over every entered path
        # And increment the count and set the label based on whether it is a folder or a file
        for id in range(len(self.addrList)):
            if self.typeList[id].GetValue() == "Folder" and self.addrList[id].GetValue() != "":
                self.folder_count += 1
                self.labelList[id].ChangeValue(stnNum + "_" + dateVal + "_M" + str(self.folder_count))
            elif self.addrList[id].GetValue() != "":
                self.file_count += 1
                self.labelList[id].ChangeValue(stnNum + "_" + dateVal + "_M" + str(self.file_count))

    def Browse(self, evt):
        id = self.browseList.index(evt.GetEventObject())
        if self.typeList[id].GetValue() == "Folder":
            DirOpenDialog = wx.DirDialog(self, "Select the Folder", self.parent.getRootPath(),
                                         style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
            if DirOpenDialog.ShowModal() == wx.ID_CANCEL:
                DirOpenDialog.Destroy()
                return

            # Set the root path of the parent to be the new root path
            self.parent.setRootPath(os.path.dirname(DirOpenDialog.GetPath()))

            self.addrList[id].ChangeValue(DirOpenDialog.GetPath())

            DirOpenDialog.Destroy()
            self.updateLabels()

        else:
            fileOpenDialog = wx.FileDialog(self, "Select the File", self.parent.getRootPath(), '',
                                           self.func,
                                           style=wx.FD_OPEN | wx.FD_CHANGE_DIR)
            if fileOpenDialog.ShowModal() == wx.ID_CANCEL:
                fileOpenDialog.Destroy()
                return

            filepath = fileOpenDialog.GetPath()
            fileOpenDialog.Destroy()

            # Get the extension of the file
            name, extension = os.path.splitext(filepath)

            # If the discharge measurement file is a pdf, then display a warning to the user
            if extension == '.pdf':
                info = wx.MessageDialog(self, 'The Discharge Measurement File type cannot be PDF.', 'Incorect file type',
                                    wx.OK | wx.ICON_ERROR)
                info.ShowModal()
                return
            else:
                
                # Set the root path of the parent to be the new root path
                self.parent.setRootPath(os.path.dirname(filepath))

                self.addrList[id].ChangeValue(filepath)
                self.updateLabels()

    def returnFilePath(self):
        fileList = []
        for x in range(len(self.addrList)):
            if self.typeList[x].GetValue() == "File" and self.addrList[x].GetValue() != "":
                fileList.append(self.addrList[x].GetValue())
        return fileList

    def returnFolderPath(self):
        folderList = []
        for x in range(len(self.addrList)):
            if self.typeList[x].GetValue() == "Folder" and self.addrList[x].GetValue() != "":
                folderList.append(self.addrList[x].GetValue())
        return folderList

    def returnPath(self):
        pathList = []
        for x in range(len(self.addrList)):
            if self.addrList[x].GetValue() != "":
                pathList.append(self.addrList[x].GetValue())
        return pathList


def main():
    app = wx.App()

    frame = wx.Frame(None, size=(850, 600))
    AttachFileFolderBox(wx.Frame, "DEBUG", frame)

    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()