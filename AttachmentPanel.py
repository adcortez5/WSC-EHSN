# All works in this code have been curated by ECCC and licensed under the GNU General Public License v3.0.
# Read more: https://www.gnu.org/licenses/gpl-3.0.en.html

import wx
import os
import sys
import shutil
from zipfile import ZipFile
from ElectronicFieldNotesGUI import *
from AttachmentTitle import *
from AttachTag import *
from AttachBox import *
from AttachFileFolderBox import *
from AttachFolderBox import *
from AttachPhotoBox import *
import ntpath
import tempfile
from os import chdir
from os import environ
from os.path import join
from os.path import dirname
import wx.lib.scrolledpanel as scrolled
from shutil import make_archive, copytree, rmtree

def valid(path):
    if path != None and path != "" and not path.isspace():
        return True
    return False

class AttachmentPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, mode, lang, *args, **kwargs):
        super(AttachmentPanel, self).__init__(*args, **kwargs)
        self.parent = parent
        self.mode = mode
        self.lang = lang
        self.indent = (30, -1)
        self.noteIndent = (200, -1)
        self.barSize = (741, -1)
        self.tagSize = (160, -1)
        self.zipSpace = (900, -1)
        self.missingStnNumMessage = "Station Number is missing"
        self.missingStnNumTitle = "Missing Station Number"
        self.nonexistentMessage = " does not exist"
        self.nonexistentTitle = "Target file does not exist"
        self.successMessage = "Field Visit Package successfully created and zipped at: "
        self.exitMessage = "You can now safely exit eHSN; your xml is already saved within the FV Package."
        self.successTitle = "File successfully zipped"
        self.errorMessage = "FV PACKAGE creation has failed"
        self.errorTitle = "Create Failure"
        self.missingZipTitle = "Missing Zip Folder"
        self.missingZipMessage = "Zip Folder not Found"
        self.reviewMessage = "The notes are not reviewed"
        self.reviewTitle = "Missing Review"
        self.rootPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.originalPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.mmtFilesTitle = "Select the MMT Files Folder"
        self.loggerFilesTitle = "Select the Logger Files Folder"
        self.zipTitle = "Field Visit Package (zip file) save location"
        #self.createConfirm = "Are you sure you want to save the FV Package to the FV PACKAGE SAVE LOCATION?"
        self.fm = "%Y%m%d"
        self.zipPath = ""
        self.zipName = ""
        self.InitUI()

    def InitUI(self):
        self.layout = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.layout)

        sizerList = []
        for i in range(10):
            sizerList.append(wx.BoxSizer(wx.HORIZONTAL))

        spaceList = []
        for x in range(10):
            spaceList.append(wx.StaticText(self, label=""))
        note = wx.StaticText(self, label="The Field Visit Package (ZIP file) will include the eHSN xml and pdf, as well as the below attachments.")

        TitlePanel = AttachmentTitle(self.mode, self)
        Txt1 = AttachTag("Logger Folders", "", self, size=self.tagSize)
        self.attachBox1 = AttachFolderBox(self, "*", self, size=(955, 125), style=wx.SIMPLE_BORDER)

        Txt2 = AttachTag("Logger Data Files", "", self, size=self.tagSize)
        self.attachBox2 = AttachBox(self, "LoggerData", self, size=(955, 100), style=wx.SIMPLE_BORDER)

        Txt3 = AttachTag("Logger Diagnostic Files", "", self, size=self.tagSize)
        self.attachBox3 = AttachBox(self, "LoggerDiagnostic", self, size=(955, 100), style=wx.SIMPLE_BORDER)

        Txt4 = AttachTag("Logger Program Files", "", self, size = self.tagSize)
        self.attachBox4 = AttachBox(self, "LoggerProgram", self, size=(955, 100), style=wx.SIMPLE_BORDER)

        Txt5 = AttachTag("Discharge Measurement", "Files or Folder", self, size = self.tagSize)
        self.attachBox5 = AttachFileFolderBox(self, "*", self, size=(955, 100), style=wx.SIMPLE_BORDER)

        Txt6 = AttachTag("Discharge Measurement", "Summary Files", self, size = self.tagSize)
        self.attachBox6 = AttachBox(self, "DischargeSummary", self, size=(955, 100), style=wx.SIMPLE_BORDER)

        Txt7 = AttachTag("Photos and Drawings", "(.jpg, .DWG, etc.)", self, size=self.tagSize)
        self.attachBox7 = AttachPhotoBox(self, "*", self, size=(955, 200), style=wx.SIMPLE_BORDER)

        self.zipAddr = wx.TextCtrl(self, size=self.barSize)
        self.zipAddr.SetValue(self.rootPath)
        # Hide the text field 
        self.zipAddr.Hide()

        self.zipper = wx.Button(self, label="CREATE FV PACKAGE")
        self.zipper.Bind(wx.EVT_BUTTON, self.Zip)
        # Hide the create fv package button
        self.zipper.Hide()

        sizerList[0].Add(self.noteIndent)
        sizerList[0].Add(note)

        sizerList[1].Add(self.indent)
        sizerList[1].Add(Txt1, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[1].Add(self.attachBox1)

        sizerList[2].Add(self.indent)
        sizerList[2].Add(Txt2, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[2].Add(self.attachBox2)

        sizerList[3].Add(self.indent)
        sizerList[3].Add(Txt3, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[3].Add(self.attachBox3)

        sizerList[4].Add(self.indent)
        sizerList[4].Add(Txt4, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[4].Add(self.attachBox4)

        sizerList[5].Add(self.indent)
        sizerList[5].Add(Txt5, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[5].Add(self.attachBox5)

        sizerList[6].Add(self.indent)
        sizerList[6].Add(Txt6, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[6].Add(self.attachBox6)

        sizerList[7].Add(self.indent)
        sizerList[7].Add(Txt7, 1, wx.EXPAND | wx.ALL, 5)
        sizerList[7].Add(self.attachBox7)

        sizerList[8].Add(self.zipSpace)
        sizerList[8].Add(self.zipper)

        # Hidden text field
        sizerList[9].Add(self.zipAddr)

        self.layout.Add(TitlePanel, 0, wx.EXPAND | wx.ALL, 3)
        for i in range(10):
            self.layout.Add(spaceList[i])
            self.layout.Add(sizerList[i])
        
        self.SetupScrolling()
        self.ShowScrollbars(wx.SHOW_SB_DEFAULT, wx.SHOW_SB_DEFAULT)

    # Get the saved root path
    # Used by AttachFolderBox, AttachBox, AttachFileFolderBox, and AttachPhotoBox
    def getRootPath(self):
        return self.rootPath

    # Set a new root path
    # Used by AttachFolderBox, AttachBox, AttachFileFolderBox, and AttachPhotoBox
    def setRootPath(self, new_path):
        self.rootPath = new_path

    # Create the FV package zip file
    def Zip(self, evt, openSaveDialog=True):

        stnNum = self.parent.genInfo.stnNumCmbo.GetValue()
        if stnNum == "" or stnNum.isspace():
            info = wx.MessageDialog(None, self.missingStnNumMessage, self.missingStnNumTitle,
                                    wx.OK)
            info.ShowModal()
            return
        
        date = self.parent.genInfo.datePicker.GetValue().Format(self.fm)

        self.zipName = stnNum + "_" + date + "_FV" + ".zip"

        if openSaveDialog:
            FileSaveDialog = wx.FileDialog(self, self.zipTitle, self.originalPath, self.zipName, 'FV Package (*.zip)|*.zip',
                                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR)

            if FileSaveDialog.ShowModal() == wx.ID_CANCEL:
                FileSaveDialog.Destroy()
                return

            self.zipName = FileSaveDialog.GetFilename()
            self.zipPath = os.path.dirname(os.path.abspath(FileSaveDialog.GetPath()))
            self.zipAddr.ChangeValue(self.zipPath)

            FileSaveDialog.Destroy()

        if not self.parent.partyInfo.reviewedCB.GetValue():
            info = wx.MessageDialog(None, self.reviewMessage, self.reviewTitle,
                                    wx.OK)
            info.ShowModal()
            return

        zipPath = self.zipAddr.GetValue()
        if zipPath == "" or zipPath.isspace() or not os.path.exists(zipPath):
            info = wx.MessageDialog(None, self.missingZipMessage, self.missingZipTitle,
                                    wx.OK)
            info.ShowModal()
            return

        #dlg = wx.MessageDialog(None, self.createConfirm, 'Create Confirmation', wx.YES_NO)
        #res = dlg.ShowModal()
        #if res != wx.ID_YES:
        #    return

        Tag = stnNum + "_" + date + "_FV"
        filePath = "c:\\temp\\eHSN\\"
        boxList = [self.attachBox1, self.attachBox2, self.attachBox3, self.attachBox4, self.attachBox5, self.attachBox6, self.attachBox7]
        pathList = []
        for box in boxList:
            pathList.append(box.returnPath())

        pdfPath = os.path.join(filePath, Tag+".pdf")
        xmlPath = os.path.join(filePath, Tag+".xml")

        for pathGroup in pathList:
            for path in pathGroup:
                if path != "" and not os.path.exists(path) and not path.isspace():
                    info = wx.MessageDialog(None, "File Address: " + path + self.nonexistentMessage, self.nonexistentTitle,
                                            wx.OK)
                    info.ShowModal()
                    return

        loggerDownload = self.attachBox2.returnPath()
        loggerDiagnostic = self.attachBox3.returnPath()
        loggerProgram = self.attachBox4.returnPath()
        loggerFolder = self.attachBox1.returnPath()
        mmtPdf = self.attachBox6.returnPath()
        mmtFile = self.attachBox5.returnFilePath()
        mmtFolder = self.attachBox5.returnFolderPath()

        SIT = self.attachBox7.returnSIT()
        STR = self.attachBox7.returnSTR()
        COL = self.attachBox7.returnCOL()
        CBL = self.attachBox7.returnCBL()
        EQP = self.attachBox7.returnEQP()
        CDT = self.attachBox7.returnCDT()
        HSN = self.attachBox7.returnHSN()

        dir_temp = tempfile.mkdtemp()

        # Logger data files
        count = 0
        for i in range(len(loggerDownload)):
            if valid(loggerDownload[i]):
                count += 1
                name, extension = os.path.splitext(loggerDownload[i])
                rename = stnNum + "_" + date + "_LG" + str(count) + extension
                shutil.copy(loggerDownload[i], dir_temp + "\\" + rename)
                loggerDownload[i] = dir_temp + "\\" + rename
        # Logger diagnostic files
        count = 0
        for i in range(len(loggerDiagnostic)):
            if valid(loggerDiagnostic[i]):
                count += 1
                name, extension = os.path.splitext(loggerDiagnostic[i])
                rename = stnNum + "_" + date + "_LD" + str(count) + extension
                shutil.copy(loggerDiagnostic[i], dir_temp + "\\" + rename)
                loggerDiagnostic[i] = dir_temp + "\\" + rename
        # Logger program files
        count = 0
        for i in range(len(loggerProgram)):
            if valid(loggerProgram[i]):
                count += 1
                name, extension = os.path.splitext(loggerProgram[i])
                rename = stnNum + "_" + date + "_LP" + str(count) + extension
                shutil.copy(loggerProgram[i], dir_temp + "\\" + rename)
                loggerProgram[i] = dir_temp + "\\" + rename
        # Discharge measurement summary files
        count = 0
        for i in range(len(mmtPdf)):
            if valid(mmtPdf[i]):
                count += 1
                name, extension = os.path.splitext(mmtPdf[i])
                rename = stnNum + "_" + date + "_M" + str(count) + extension
                shutil.copy(mmtPdf[i], dir_temp + "\\" + rename)
                mmtPdf[i] = dir_temp + "\\" + rename
        # Discharge measurement files
        count = 0
        for i in range(len(mmtFile)):
            if valid(mmtFile[i]):
                count += 1
                name, extension = os.path.splitext(mmtFile[i])
                rename = stnNum + "_" + date + "_M" + str(count) + extension
                shutil.copy(mmtFile[i], dir_temp + "\\" + rename)
                mmtFile[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(SIT)):
            if valid(SIT[i]):
                count += 1
                name, extension = os.path.splitext(SIT[i])
                rename = stnNum + "_" + date + "_SIT" + str(count) + extension
                shutil.copy(SIT[i], dir_temp + "\\" + rename)
                SIT[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(STR)):
            if valid(STR[i]):
                count += 1
                name, extension = os.path.splitext(STR[i])
                rename = stnNum + "_" + date + "_STR" + str(count)  + extension
                shutil.copy(STR[i], dir_temp + "\\" + rename)
                STR[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(COL)):
            if valid(COL[i]):
                count += 1
                name, extension = os.path.splitext(COL[i])
                rename = stnNum + "_" + date + "_COL" + str(count) + extension
                shutil.copy(COL[i], dir_temp + "\\" + rename)
                COL[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(CBL)):
            if valid(CBL[i]):
                count += 1
                name, extension = os.path.splitext(CBL[i])
                rename = stnNum + "_" + date + "_CBL" + str(count) + extension
                shutil.copy(CBL[i], dir_temp + "\\" + rename)
                CBL[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(EQP)):
            if valid(EQP[i]):
                count += 1
                name, extension = os.path.splitext(EQP[i])
                rename = stnNum + "_" + date + "_EQP" + str(count) + extension
                shutil.copy(EQP[i], dir_temp + "\\" + rename)
                EQP[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(CDT)):
            if valid(CDT[i]):
                count += 1
                name, extension = os.path.splitext(CDT[i])
                rename = stnNum + "_" + date + "_CDT" + str(count) + extension
                shutil.copy(CDT[i], dir_temp + "\\" + rename)
                CDT[i] = dir_temp + "\\" + rename
        # Photos and drawings
        count = 0
        for i in range(len(HSN)):
            if valid(HSN[i]):
                count += 1
                name, extension = os.path.splitext(HSN[i])
                rename = stnNum + "_" + date + "_HSN" + str(count) + extension
                shutil.copy(HSN[i], dir_temp + "\\" + rename)
                HSN[i] = dir_temp + "\\" + rename

        self.parent.manager.ExportAsXML(xmlPath, None)
        try:
            self.parent.manager.ExportAsPDFWithoutOpen(pdfPath, self.parent.viewStyleSheetFilePath)
        except:
            info = wx.MessageDialog(self, self.parent.savePDFErrorMsg, self.parent.savePDFErrorTitle,
                                    wx.OK | wx.ICON_ERROR)
            info.ShowModal()
            return

        try:
            zipfile = ZipFile(zipPath + "\\" + self.zipName, 'w')
            zipfile.write(pdfPath, Tag + "\\" + ntpath.basename(pdfPath))
            zipfile.write(xmlPath, ntpath.basename(xmlPath))
    
            for path in loggerDownload:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in loggerDiagnostic:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in loggerProgram:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in mmtPdf:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in mmtFile:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            
            # Discharge measurement folders
            count = 0
            for folder in mmtFolder:
                if valid(folder):
                    count += 1
                    # Copy the full folder into a new folder of the same name and save the zipped folder in the temp directory
                    # This is done so the zipped folder contains a folder instead of loose files
                    zip_folder_name = stnNum + "_" + date + "_M" + str(count)
                    os.mkdir(filePath + zip_folder_name)
                    copytree(folder, filePath + zip_folder_name + '\\' + zip_folder_name)
                    make_archive(filePath + zip_folder_name, 'zip', filePath + zip_folder_name)
                    # Add this zipped folder to the main zip
                    zipfile.write(filePath + zip_folder_name + '.zip', Tag + "\\" + zip_folder_name + '.zip')
                    # Remove the folder zip and copied folder from temp
                    if os.path.exists(filePath + zip_folder_name + '.zip'):
                        os.remove(filePath + zip_folder_name + '.zip')
                    if os.path.exists(filePath + zip_folder_name):
                        try:
                            rmtree(filePath + zip_folder_name)
                        except Exception as e:
                            print('Unable to delete temp folder')
                            print(str(e))
            # Logger folders
            count = 0
            for folder in loggerFolder:
                if valid(folder):
                    count += 1
                    # Copy the full folder into a new folder of the same name and save the zipped folder in the temp directory
                    # This is done so the zipped folder contains a folder instead of loose files
                    zip_folder_name = stnNum + "_" + date + "_LG" + str(count)
                    os.mkdir(filePath + zip_folder_name)
                    copytree(folder, filePath + zip_folder_name + '\\' + zip_folder_name)
                    make_archive(filePath + zip_folder_name, 'zip', filePath + zip_folder_name)
                    # Add this zipped folder to the main zip
                    zipfile.write(filePath + zip_folder_name + '.zip', Tag + "\\" + zip_folder_name + '.zip')
                    # Remove the folder zip and copied folder from temp
                    if os.path.exists(filePath + zip_folder_name + '.zip'):
                        os.remove(filePath + zip_folder_name + '.zip')
                    if os.path.exists(filePath + zip_folder_name):
                        try:
                            rmtree(filePath + zip_folder_name)
                        except Exception as e:
                            print('Unable to delete temp folder')
                            print(str(e))
            for path in SIT:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in STR:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in COL:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in CBL:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in EQP:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in CDT:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))
            for path in HSN:
                if valid(path):
                    zipfile.write(path, Tag + "\\" + ntpath.basename(path))

            zipfile.close()
            if openSaveDialog:
                info = wx.MessageDialog(None, self.successMessage + zipPath + '\n' + self.exitMessage, self.successTitle, wx.OK)
            else:
                info = wx.MessageDialog(None, self.successMessage + zipPath, self.successTitle, wx.OK)

            self.zipPath = zipPath + "\\" + self.zipName
            info.ShowModal()
        except Exception as e:
            print(type(e))
            print(e)
            info = wx.MessageDialog(None, self.errorMessage, self.errorTitle, wx.OK)
            info.ShowModal()
        
        if os.path.exists(pdfPath):
            os.remove(pdfPath)
        if os.path.exists(xmlPath):
            os.remove(xmlPath)

def main():
    app = wx.App()
    frame = wx.Frame(None, size=(1200, 650))
    AttachmentPanel(wx.Frame, "debug", wx.LANGUAGE_FRENCH, frame)
    frame.Centre()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
