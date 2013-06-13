import wx
import os
import cPickle

"This is my python test program."
#test

class SketchWindow(wx.Window):

    def __init__(self, parent, ID): 
        wx.Window.__init__(self, parent, ID) 
        self.SetBackgroundColour("White") 
        self.color = "Red" 
        self.thickness = 3 
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID) 
        self.lines = [] 
        self.curLine = [] 
        self.pos = (0, 0) 
        self.InitBuffer()
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown) 
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp) 
        self.Bind(wx.EVT_MOTION, self.OnMotion) 
        self.Bind(wx.EVT_SIZE, self.OnSize) 
        self.Bind(wx.EVT_IDLE, self.OnIdle) 
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def ClearBuffer(self):
        self.SetLinesData([])
        
    def InitBuffer(self): 
        size = self.GetClientSize() 
        self.buffer = wx.EmptyBitmap(size.width, size.height) 
        dc = wx.BufferedDC(None, self.buffer) 
        dc.SetBackground(wx.Brush(self.GetBackgroundColour())) 
        dc.Clear() 
        self.DrawLines(dc) 
        self.reInitBuffer = False
        
    def GetLinesData(self): 
        return self.lines[:]
    
    def SetLinesData(self, lines): 
        self.lines = lines[:] 
        self.InitBuffer() 
        self.Refresh()
        
    def OnLeftDown(self, event): 
        self.curLine = [] 
        self.pos = event.GetPositionTuple() 
        self.CaptureMouse()
        
    def OnLeftUp(self, event): 
        if self.HasCapture(): 
            self.lines.append((self.color, 
            self.thickness, 
            self.curLine)) 
            self.curLine = [] 
            self.ReleaseMouse()

    def OnMotion(self, event): 
        if event.Dragging() and event.LeftIsDown(): 
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer) 
            self.drawMotion(dc, event)
        event.Skip()

    def drawMotion(self, dc, event): 
        dc.SetPen(self.pen) 
        newPos = event.GetPositionTuple() 
        coords = self.pos + newPos 
        self.curLine.append(coords) 
        dc.DrawLine(*coords) 
        self.pos = newPos

    def OnSize(self, event): 
        self.reInitBuffer = True
        
    def OnIdle(self, event): 
        if self.reInitBuffer: 
            self.InitBuffer() 
            self.Refresh(False)
            
    def OnPaint(self, event): 
        dc = wx.BufferedPaintDC(self, self.buffer)
        
    def DrawLines(self, dc): 
        for colour, thickness, line in self.lines: 
            pen = wx.Pen(colour, thickness, wx.SOLID) 
            dc.SetPen(pen) 
            for coords in line: 
                dc.DrawLine(*coords)

    def SetColor(self, color): 
        self.color = color 
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)
        
    def SetThickness(self, num): 
        self.thickness = num 
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)

class SketchFrame(wx.Frame):
    
    def __init__(self, parent): 
        wx.Frame.__init__(self, parent, -1, "Sketch Frame", 
        size=(800,600))
        self.filename = ""
        self.title = "Sketch Frame" 
        self.sketch = SketchWindow(self, -1)
        self.initStatusBar()
        self.createMenuBar()
        self.createToolBar()        
        self.sketch.Bind(wx.EVT_MOTION, self.OnSketchMotion)

    def createToolBar(self):
        toolbar = self.CreateToolBar()
        #toolbar = self.CreateToolBar( wx.TB_TEXT | wx.TB_3DBUTTONS, -1 )
        
        for each in self.toolbarData():
            self.createSimpleTool(toolbar, *each)
        toolbar.AddSeparator()
        for each in self.toolbarColorData():
            if each == "Other":
                bmp = self.MakeBitmap("White")
                tool = toolbar.AddSimpleTool(wx.NewId(), bmp, "Other")
                self.Bind(wx.EVT_MENU, self.OnOtherColor, tool)
            else:
                self.createColorTool(toolbar, each)
        toolbar.AddSeparator()
        
        toolbar.Realize()
        
    def createSimpleTool(self, toolbar, label, filename, helpstr, handler):
        if not label:
            toolbar.AddSeparator()
        else:
            #bmp = wx.Image(filename, wx.BITMAP_TYPE_BMP).ConvertToBitmap()
            bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_BMP)
            tool = toolbar.AddSimpleTool(wx.NewId(), bmp, label, helpstr)
            self.Bind(wx.EVT_MENU, handler, tool)

    def createColorTool(self, toolbar, color):
        bmp = self.MakeBitmap(color)
        tool = toolbar.AddSimpleTool(wx.NewId(), bmp, color)
        self.Bind(wx.EVT_MENU, self.OnColor, tool)
        
    def MakeBitmap(self, color):
        bmp = wx.EmptyBitmap(32, 32)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(color))
        dc.Clear()
        dc.SelectObject(wx.NullBitmap)
        return bmp

    def toolbarData(self):
        return (("New", "new.bmp", "Create a new file", self.OnNew),
                ("", "", "", ""),
                ("Open", "open.bmp", "Open a exist file", self.OnOpen),
                ("", "", "", ""),
                ("Save", "save.bmp", "Save file", self.OnSave)
                )

    def toolbarColorData(self):
        return ("Black", "Red", "Green", "Blue", "Other")



    wildcard = "Sketch files (*.sketch)|*.sketch|Bitmap files (*.bmp)|*.bmp|All files (*.*)|*.*"

    def ReadFile(self): 
        if self.filename: 
            try:
                print self.filename
                f = open(self.filename, 'r') 
                data = cPickle.load(f) 
                f.close() 
                self.sketch.SetLinesData(data) 
            except cPickle.UnpicklingError: 
                wx.MessageBox("%s is not a sketch file." 
                    % self.filename, "oops!", 
                    style=wx.OK|wx.ICON_EXCLAMATION)
                
    def SaveFile(self): 
        if self.filename: 
            data = self.sketch.GetLinesData() 
            f = open(self.filename, 'w') 
            cPickle.dump(data, f) 
            f.close()

    def OnNew(self, event):
        #dlg = wx.MessageDialog(None, 'You really want to close?', 'MessageDialog', wx.ICON_INFORMATION)
        #result = dlg.ShowModal()
        self.sketch.ClearBuffer()
        self.SetTitle('Unnamed title') 
        
    def OnOpen(self, event):
        dlg = wx.FileDialog(self, "Open sketch file...", os.getcwd(), wildcard=self.wildcard, style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK: 
            self.filename = dlg.GetPath()
            self.ReadFile() 
            self.SetTitle(self.title + ' -- ' + self.filename) 
        dlg.Destroy()

    def OnSave(self, event):
        #if not self.filename: 
            self.OnSaveAs(event) 
        #else: 
        #    self.SaveFile()
            
    def OnSaveAs(self, event): 
        dlg = wx.FileDialog(self, "Save sketch as...", 
            os.getcwd(), 
            style=wx.SAVE | wx.OVERWRITE_PROMPT, 
            wildcard=self.wildcard) 
        if dlg.ShowModal() == wx.ID_OK: 
            filename = dlg.GetPath() 
            if not os.path.splitext(filename)[1]: 
                filename = filename + '.sketch' 
            self.filename = filename 
            self.SaveFile() 
            self.SetTitle(self.title + ' -- ' + self.filename) 
        dlg.Destroy()
    
    def initStatusBar(self):
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(2)
        self.statusbar.SetStatusWidths([-1, -2])
        
    def menuData(self): 
        return [("&File", ( 
                    ("&New", "New Sketch file", self.OnNew), 
                    ("&Open", "Open sketch file", self.OnOpen), 
                    ("&Save", "Save sketch file", self.OnSave), 
                    ("", "", ""),
                    
                    ("&Color", ( 
                        ("&Black", "", self.OnColor, 
                        wx.ITEM_RADIO), 
                        ("&Red", "", self.OnColor, 
                        wx.ITEM_RADIO), 
                        ("&Green", "", self.OnColor, 
                        wx.ITEM_RADIO), 
                        ("&Blue", "", self.OnColor, 
                        wx.ITEM_RADIO),
                        ("Other Colors", "", self.OnOtherColor,
                            wx.ITEM_RADIO))),
                    ("", "", ""), 
                    ("&Quit", "Quit", self.OnCloseWindow)))]
     
    def createMenuBar(self):
        menuBar = wx.MenuBar()
        for eachMenuData in self.menuData():
            menuLabel = eachMenuData[0]
            menuItems = eachMenuData[1]
            menuBar.Append(self.CreateMenuItems(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
        #set default color
        menu = menuBar.GetMenu(menuBar.FindMenu("File"))
        itemId = menu.FindItem("Blue")
        menu.Check(itemId, True)
        item = menuBar.FindItemById(itemId)
        color = item.GetLabel()
        self.sketch.SetColor(color)

        
    def CreateMenuItems(self, menuItems):
        menu = wx.Menu()
        for eachMenuItems in menuItems:
            if len(eachMenuItems) == 3:
                label = eachMenuItems[0]
                StatusStr = eachMenuItems[1]
                handler = eachMenuItems[2]
                if not label:
                    menu.AppendSeparator()
                else:
                    menuItem = menu.Append(wx.NewId(), label, StatusStr, wx.ITEM_NORMAL)
                    self.Bind(wx.EVT_MENU, handler, menuItem)
            elif len(eachMenuItems) == 4:
                label = eachMenuItems[0]
                StatusStr = eachMenuItems[1]
                handler = eachMenuItems[2]
                menuStyle = eachMenuItems[3]
                if not label:
                    menu.AppendSeparator()
                else:
                    menuItem = menu.Append(wx.NewId(), label, StatusStr, menuStyle)
                    self.Bind(wx.EVT_MENU, handler, menuItem)
            elif len(eachMenuItems)== 2:
                label = eachMenuItems[0]
                subMenu = self.CreateMenuItems(eachMenuItems[1])
                menu.AppendMenu(wx.NewId(), label, subMenu)
        return menu

    def OnColor(self, event):
        menubar = self.GetMenuBar()
        itemId = event.GetId()
        item = menubar.FindItemById(itemId)
        if item:
            color = item.GetLabel()
        else: #search tool bar if couldn't find item in menubar
            toolbar = self.GetToolBar()
            item = toolbar.FindById(itemId)
            color = item.GetShortHelp()
            self.sketch.SetColor(color)

    def OnOtherColor(self, event): 
        dlg = wx.ColourDialog(self) 
        dlg.GetColourData().SetChooseFull(True) 
        if dlg.ShowModal() == wx.ID_OK: 
            self.sketch.SetColor(dlg.GetColourData().GetColour()) 
        dlg.Destroy() 
    
    def OnCloseWindow(self):
        pass
    
    def OnSketchMotion(self, event):
        self.statusbar.SetStatusText('The status bar.', 0)
        self.statusbar.SetStatusText('Position: ' + str(event.GetPositionTuple()), 1)
        event.Skip()

class SketchApp(wx.App):

    def OnInit(self):
        bmp = wx.Bitmap("StartUp.bmp", wx.BITMAP_TYPE_BMP)
        wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN |
                wx.SPLASH_TIMEOUT, 2000, None, -1)
        wx.Yield()
        self.frame = SketchFrame(None)
        self.frame.Show()

        return True
        
if __name__ == '__main__': 
    app = SketchApp() 
    app.MainLoop() 
        
