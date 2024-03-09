from PyQt5 import QtCore,QtGui,QtWidgets
from functools import partial 
import time
import numpy as np
from h5py import h5p
import h5py
from functools import reduce
import os
import sys
app = QtWidgets.QApplication(sys.argv)
clipboard = app.clipboard()

class DirectoryWindow(QtWidgets.QWidget):
    def __init__(self,path,buttonlistfuns,hookclick=None,*args,**kwargs):
        super(DirectoryWindow,self).__init__(*args,**kwargs)
        self.currentpath=path 
        self.home = path 
        self.buttonlistfuns = buttonlistfuns# this is a two column list of text(1str) and functions to call buttons at the top
        self.hookclick=hookclick
        self.build()
    
    def build(self):
        self.listwindow = QtWidgets.QListWidget()
        self.listwindow.itemDoubleClicked.connect(self.downdir)
        self.updirectory = QtWidgets.QPushButton(text='Up Directory')
        self.updirectory.clicked.connect(self.updir)
        self.gotogtsaxsfolder = QtWidgets.QPushButton(text='Home')
        self.gotogtsaxsfolder.clicked.connect(self.homedir)
        self.searchedit = QtWidgets.QLineEdit(text='')
        self.searchedit.editingFinished.connect(self.rebuildlist)
        self.pathText = QtWidgets.QLabel(text=self.currentpath)
        if self.hookclick:self.listwindow.itemPressed.connect(self.hookclick)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.pathText)
        self.listwindow.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setLayout(layout)
        widget=QtWidgets.QWidget()
        hlayout = QtWidgets.QHBoxLayout()
        widget.setLayout(hlayout)
        hlayout.addWidget(self.updirectory)
        hlayout.addWidget(self.gotogtsaxsfolder)
        hlayout.addWidget(self.searchedit)
        layout.addWidget(widget)
        self.hwidgets = []
        self.btns = []
        for i in range(len(self.buttonlistfuns)):
            if i==0:
                widget=QtWidgets.QWidget()
                glayout = QtWidgets.QGridLayout()
                widget.setLayout(glayout)
                self.hwidgets.append(widget)
                
            if i<4:
                btn = QtWidgets.QPushButton(text=self.buttonlistfuns[i][0])
                btn.clicked.connect(self.buttonlistfuns[i][1])
                glayout.addWidget(btn,0,i)
                self.btns.append(btn)
            
            if i==4:pass
                #widget=QtWidgets.QWidget()
                #glayout = QtWidgets.QGridLayout()
                #widget.setLayout(glayout)
                #self.hwidgets.append(widget)
                
            if i<8 and i>3:
                btn = QtWidgets.QPushButton(text=self.buttonlistfuns[i][0])
                btn.clicked.connect(self.buttonlistfuns[i][1])
                glayout.addWidget(btn,1,i-4)
                self.btns.append(btn)
        for h in self.hwidgets:layout.addWidget(widget)
        ls = __file__.split('/')
        ls.pop(-1)
        modpath = ''
        for l in ls:modpath+=l+'/'
        modpath=modpath[0:-1]
        #self.listwindow.itemClicked.connect(self.)
        for p in self.entries:
            if os.path.isdir(os.path.join(self.currentpath,p)):
                icon = QtGui.QIcon(os.path.join(modpath,'directory.png'))
                item = QtWidgets.QListWidgetItem(icon,p)
            else:
                icon = QtGui.QIcon(os.path.join(modpath,'file.png'))
                item = QtWidgets.QListWidgetItem(icon,p)
            self.listwindow.addItem(item)
        layout.addWidget(self.listwindow)
   
    def filetime(self,entry):
        time = os.stat(os.path.join(self.currentpath,entry))
        return time.st_mtime
    
    def homedir(self,btn):
        self.currentpath = self.home
        
        self.rebuildlist()
    def updir(self,btn):
        dirs = self.currentpath.split('/')
        dirs.pop(-1)
        self.currentpath = ''
       
        for d in dirs:self.currentpath+=d+'/'
        self.currentpath = self.currentpath[0:-1]
        
        self.rebuildlist()
    def downdir(self,item):
        self.currentpath += '/'+item.text()
        self.rebuildlist()
    def rebuildlist(self):
        self.pathText.setText(self.currentpath)
        
        i=0
        self.listwindow.clear()
        ls = __file__.split('/')
        ls.pop(-1)
        modpath = ''
        for l in ls:modpath+=l+'/'
        modpath=modpath[0:-1]
        for p in self.entries:
            if os.path.isdir(os.path.join(self.currentpath,p)):
                icon = QtGui.QIcon(os.path.join(modpath,'directory.png'))
                item = QtWidgets.QListWidgetItem(icon,p)
            else:
                icon = QtGui.QIcon(os.path.join(modpath,'file.png'))
                item = QtWidgets.QListWidgetItem(icon,p)
            self.listwindow.addItem(item)
        if self.hookclick:self.hookclick()
    @property 
    def entries(self):
        ret= sorted(os.listdir(self.currentpath),key=self.filetime,reverse=True)
        srchstrings = str(self.searchedit.text()).split('.*')
        for s in srchstrings:
            ret = list(filter(lambda x: str(x).count(s)>0, ret))
        #print(len(ret))
        return ret
class DLineEdit(QtWidgets.QLineEdit):
    def __init__(self,parfun,*args,**kwargs):
        super(DLineEdit,self).__init__(*args,**kwargs)
        self.parfun=parfun
    def contextMenuEvent(self, event):    
        menu = QtWidgets.QMenu(self)
        adlis = self.parfun()
        for addr in adlis:
            pastaction = QtWidgets.QAction(addr,self)
            parfun=partial(self.pastaddress,addr)
            pastaction.triggered.connect(parfun)
            quitAction = menu.addAction(pastaction)
        action = menu.exec_(self.mapToGlobal(event.pos()))
        print(self.parfun())
        print(event)
    def pastaddress(self,keyaddr):
        self.setText(keyaddr)
class Dict2Widget(QtWidgets.QWidget):
    def __init__(self,inputdict,functiondict,parent,checkboxdict = dict(),
                 minmaxdict=dict(),customwidgetdict=dict(),Hstack = False,**kwargs):
        super(Dict2Widget,self).__init__(**kwargs)
        #self.inputdict = dict(sorted(inputdict.items(),key=self.sortparams))
        #self.functiondict = dict(sorted(functiondict.items(),key=self.sortparams))
        self.inputdict = dict(inputdict)
        self.functiondict = dict(functiondict)
        self.lineeditcolor = ['brown','white']
        self.comboboxcolor = ['darkred','white']
        self.labelcolor = ['greenyellow','black']
        self.floatcolor = ['aquamarine','black']
        self.pdictaddresscolors = [['red','black'],['tomato','black'],['salmon','black'],['fuchsia','black']]
        self.rclkpos = QtCore.QPoint()
        self.lclkpos = QtCore.QPoint()
        self.widgetdict = dict()
        self.playoutdict = dict()
        self.customwidgetdict=customwidgetdict
        self.minmaxdict = minmaxdict
        self.checkboxdict = checkboxdict
        self.parent = parent
        self.keylist = str('')
        self.colorlayout = dict()
        self.oldsizey = self.size().height()
        si = QtWidgets.QSizePolicy();si.Expanding
        self.setMaximumSize(QtCore.QSize(1000000,10000))
        self.Hstack = Hstack
        #self.setSizePolicy(si.Policy.Expanding,si.Policy.Expanding)
        self.build()
    def mousePressEvent(self, ev):
        #print('right click')
        #print(ev.button())
        if ev.button()==2:
            self.rclkpos = ev.pos()
            pos = QtCore.QPoint()
            #print(self.pos())
            pos.setX(self.parent.pos().x()+self.pos().x()+self.rclkpos.x())
            pos.setY(self.parent.pos().y()+self.pos().y()+self.rclkpos.y())
            #self.layout.addWidget(self.popmenu)
            #QtWidgets.qApp.processEvents()
            
            self.popmenu.show()
            self.popmenu.move(pos)
        else:
            self.lclkpos = ev.pos()
        return QtWidgets.QWidget.mousePressEvent(self, ev)
    def sortparams(self,x):
        #print(x)
        if x[0].count('Start')>0:return 1000
        elif x[0].count('End')>0:return 0
        else:return(ord(x[0][0]))
    def subwidgetsfrompkey(self,pkey,pdict,widglist = []):
        for key in sorted(pdict.keys()):
            item = pdict[key]
            if isinstance(item, dict):
                widglist.append(pkey+';'+key+';')
                self.subwidgetsfrompkey(pkey+';'+key,item,widglist)
            else:
                widglist.append(pkey+';'+key+';')
        return widglist
    def rebuildall(self):
        for k,w in list(self.widgetdict.items()):
            tup = self.widgetdict.pop(k)
            self.oldsizey-=tup[1].size().height()
            tup[0].setParent(None)
            tup[1].setParent(None)
            
            tup[2].takeAt(0)
            tup[2].takeAt(0)
            if tup[3]!=False:
                tup[3].setParent(None)
                #tup[3].takeAt(0)
            if len(tup)>4:
                if tup[4]!=None:
                    tup[4].setParent(None)
                    #tup[4].takeAt(0)
                    tup[5].setParent(None)
                    #tup[5].takeAt(0)
            del tup
        self.build()
    def deletewidgetsfrompkey(self,pkey,pdict):
        self.oldsizey = 0
        keys =  self.subwidgetsfrompkey(pkey,pdict,[])
        for key,item in list(self.widgetdict.items()):
            mkey = key.split(';')[1]
            if mkey=='ShapeParams':
                pass
        for k in keys:
            if k in self.widgetdict:
                tup = self.widgetdict.pop(k)
                self.oldsizey-=tup[1].size().height()
                tup[0].setParent(None)
                tup[1].setParent(None)
                
                tup[2].takeAt(0)
                tup[2].takeAt(0)
                if tup[3]!=False:
                    tup[3].setParent(None)
                    #tup[3].takeAt(0)
                if len(tup)>4:
                    if tup[4]!=None:
                        tup[4].setParent(None)
                        #tup[4].takeAt(0)
                        tup[5].setParent(None)
                        #tup[5].takeAt(0)
                del tup
    def rebuild(self,newdict,pkey,chk={},mm={}):
        self.inputdict[pkey] = newdict
        layout = self.widgetdict[pkey][2]
        for key in sorted(newdict.keys()):
            item = newdict[key]
            if key in chk:ichk = chk[key]
            else:ichk = False
            if key in mm:imm = mm[key]
            else: imm = None
            self.keylist = pkey
            #print(ichk,imm)
            self.newrow(key,item,layout,ichk,imm)
        self.resize(self.size().width(),self.size().height()+self.oldsizey)
        #self.parent.resize(self.size().width()+100,self.size().height()+self.oldsizey)
    def build(self):
        if self.Hstack:self.layout = QtWidgets.QHBoxLayout()
        else: self.layout = QtWidgets.QVBoxLayout()
        self.playoutdict['Main'] = self.layout
        self.setLayout(self.layout)
        for key in sorted(self.inputdict.keys()):
            item = self.inputdict[key]
            self.keylist = ''
            if key in self.checkboxdict:
                chitem = self.checkboxdict[key]
                minmax = self.minmaxdict[key]
                self.newrow(key, item, self.layout, chk = chitem,mnmx = minmax )
            else:
                self.newrow(key,item,self.layout)
        sizey = len(self.children())*30
        
        self.popmenu = QtWidgets.QMenu(title = 'Action:')
        #for action in self.actions:
        #fun = partial(self.settime,action.text())
        action = QtWidgets.QAction('Copy Address to Clipboard',self.popmenu)
        action.triggered.connect(self.copyaddress)
        self.popmenu.addAction(action)
        #self.resize(self.size().width(),sizey)
    def copyaddress(self,*args):
        #print(args)
        
        clipboard.clear()
        
        revwidg = dict(list(map(lambda x: (x[1][0],x[0]), self.widgetdict.items())))
        #print(revwidg)
        clipboard.setText(revwidg[self.childAt(self.rclkpos)])
        
        
    def newrow(self,key,item,parent,chk = False,mnmx=None):
        if isinstance(item,dict):
            self.colorlayout[self.oldsizey] = np.random.rand(3)[:]*255
            parentkey = str(self.keylist)
            nkeys = len(str(self.keylist+key).split(';'))
            self.keylist+=key+';'
            label = QtWidgets.QLabel(key+' :  ')
            label.setStyleSheet('QLabel {background-color: '+self.pdictaddresscolors[nkeys-1][0]+'; color: '+self.pdictaddresscolors[nkeys-1][1]+';}')
            label.setFixedHeight(50)
            label.setFont(QtGui.QFont('Times'))
            layout = RandColorLayout([200,100,100])
            if self.Hstack:layout.addWidget(label)
            else: parent.addWidget(label)
            #layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
            self.widgetdict[self.keylist] = (label,label,layout,False,None,None)
            for k in sorted(item.keys()):
                i = item[k]
                if isinstance(chk,dict):
                    if k in chk:
                        ci = chk[k]
                    else: ci=False
                else: ci = False
                if isinstance(mnmx,dict):
                    if k in mnmx:
                        mm = mnmx[k]
                    else: mm=None
                else: mm = None
                self.newrow(k,i,layout,chk = ci,mnmx=mm)    
            
            self.keylist = str(parentkey)
            
            parent.addLayout(layout)
        else:
            text = False
            layout = QtWidgets.QHBoxLayout()
            layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetNoConstraint)
            label = QtWidgets.QLabel(key+' :  ')
            label.setStyleSheet('QLabel {background-color: '+self.labelcolor[0]+'; color: '+self.labelcolor[1]+';}')
            label.setFont(QtGui.QFont('Times'))
            label.setFixedHeight(30)
            layout.addWidget(label)
            posdig1 = str(item)
            posdig2 = str(item)[1:]
            isdig = posdig1.isdigit() or posdig2.isdigit()
            #print(key,item)
            if isinstance(item,str) or item==None:
                text = QtWidgets.QLineEdit(str(item))
                text.setStyleSheet('QLineEdit {background-color: '+self.lineeditcolor[0]+'; color: '+self.lineeditcolor[1]+';}')
                if key in self.functiondict:
                    text.editingFinished.connect(self.functiondict[key])
                elif 'Enter' in self.functiondict:
                    #print(key)
                    fun = partial(self.functiondict['Enter'],self.keylist+key+';',text)
                    text.editingFinished.connect(fun)
                self.widgetdict[self.keylist+key+';'] = (label,text,parent,False,None,None)
                layout.addWidget(text)
            
            elif isinstance(item,float)==True or isinstance(item,int) ==True and isdig:
                if key in self.customwidgetdict:
                    #print(key,self.customwidgetdict[key])
                    text=self.customwidgetdict[key]
                else:
                    text = QtWidgets.QLineEdit(str(item))
                    text.setStyleSheet('QLineEdit {background-color: '+self.floatcolor[0]+'; color: '+self.floatcolor[1]+';}')
                if mnmx:
                    #parfun=partial(self.pasteaddress,self.listofcheckedparameters)
                    if isinstance(mnmx, list):
                        
                        if str(mnmx[0]) != 'None':
                            mintext = DLineEdit(self.listofcheckedparameters,str(mnmx[0])) 
                            maxtext = DLineEdit(self.listofcheckedparameters,str(mnmx[1]))
                        else:
                            
                            mintext = DLineEdit(self.listofcheckedparameters,str(item*0.1)) 
                            maxtext = DLineEdit(self.listofcheckedparameters,str(item*10.))
                    else:
                        mintext = DLineEdit(self.listofcheckedparameters,str(item*0.1)) 
                        maxtext = DLineEdit(self.listofcheckedparameters,str(item*10.))
                else:
                    mintext = QtWidgets.QLineEdit(str(item*0.1)) 
                    maxtext = QtWidgets.QLineEdit(str(item*10.))
                checkbox = QtWidgets.QCheckBox()
                if key in self.functiondict:
                    fun = partial(self.functiondict[key],self.keylist+key+';',text)
                    text.editingFinished.connect(fun)
                elif 'Enter' in self.functiondict:
                    fun = partial(self.functiondict['Enter'],self.keylist+key+';',text)
                    text.editingFinished.connect(fun)
                if 'EnterMinMax' in self.functiondict: 
                    minfun = partial(self.functiondict['EnterMinMax'],self.keylist+key+';',mintext,0)
                    maxfun = partial(self.functiondict['EnterMinMax'],self.keylist+key+';',maxtext,1)
                    mintext.editingFinished.connect(minfun)
                    maxtext.editingFinished.connect(maxfun)
                if 'EnterChecked' in self.functiondict:
                    fun = partial(self.functiondict['EnterChecked'],self.keylist+key,checkbox)
                    checkbox.clicked.connect(fun)
                    checkbox.setChecked(chk)
                self.widgetdict[self.keylist+key+';'] = (label,text,parent,checkbox,mintext,maxtext)
                layout.addWidget(text)
                layout.addWidget(checkbox)
                if mnmx:
                    layout.addWidget(mintext)
                    layout.addWidget(maxtext)
                layout.addWidget(text)
          
            elif isinstance(item,list):
                text = QtWidgets.QComboBox()
                text.setStyleSheet('QComboBox {background-color: '+self.comboboxcolor[0]+'; color: '+self.comboboxcolor[1]+';}')
                if key in self.functiondict:
                    fun = partial(self.functiondict[key],text,self.keylist)
                    text.activated.connect(fun)
                elif 'EnterCombo' in self.functiondict:
                    fun = partial(self.functiondict['EnterCombo'],self.keylist+key+';',text)
                    text.activated.connect(fun)
                s = -1
                for i in item[0]:
                    
                    s+=1
                    text.insertItem(s,str(i))
                if any(item[0])==True:
                    item[0] = [str(x) for x in item[0]]
                try:
                    text.setCurrentIndex(item[0].index(item[1]))
                except:text.setCurrentIndex(0)
                layout.addWidget(text)    
                try:
                    self.parent.args.updatestr(self.keylist+key+';', text, 0)
                except:
                    pass
                self.widgetdict[self.keylist+key+';'] = (label,text,parent,False,None,None)
            elif callable(item):
                #print key,item
                text = QtWidgets.QPushButton(text = key)
                text.setStyleSheet('QPushButton {background-color: '+self.lineeditcolor[0]+'; color: '+self.lineeditcolor[1]+';}')
                #if key in self.functiondict:
                text.clicked.connect(item)
                self.widgetdict[self.keylist+key+';'] = (label,text,parent,False,None,None)
                layout.addWidget(text)
            else:#assume item is a widget
                self.widgetdict[self.keylist+key+';'] = (label,item,parent,False,None,None)
                #print(key,item)
                #print(isinstance(item,classmethod))
                #print(item())
                layout.addWidget(item)
            #text.setFixedHeight(30)
            if text:self.oldsizey+=text.sizeHint().height()*3.0
            
            parent.addLayout(layout)
    def paintEvent(self,e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(100,180,255))
        qp.drawRect(0, 0, self.size().width(), self.size().height())
        stepcolor = 0
        for key,item in list(self.widgetdict.items()):
            if len(key.split(';'))==2:
                stepcolor +=10
                qp.setBrush(QtGui.QColor(255-stepcolor,255,255))
                #qp.setBrush(QtGui.QColor(150+stepcolor,150+stepcolor,255-stepcolor))
                if stepcolor>100:stepcolor = 0
                qp.drawRect(item[0].x(), item[0].y(), item[0].width(), item[0].height())
        qp.end
    def returndict(self,key,valtup):
        kls = list(key.split('_'))
        startkey = kls.pop(0)
        sdict = dict()
        retdict = dict()
        retdict[startkey] = sdict
        if len(kls)==0:
            retdict[startkey] = valtup
            return (startkey,valtup)
        elif len(kls)==1:
            endkey = kls.pop(0)
            sdict[endkey] = valtup
            return (startkey,sdict)
        else:
            endkey = kls.pop(-1)
            kls.reverse()
            valkey = {endkey:valtup}
            for k in kls:
                sdict[k] = valkey
                valkey = dict(retdict)
            return (startkey,sdict)
    def updateGUI(self,args):
        for key in list(args.keys()):
            if key in self.inputdict:
                item = self.inputdict[key]
                argitem = args[key]
                self.keylist = ''
                self.updaterow(key,item,argitem)
    def hdftodict(self,group,retdict=dict()):
        for key,item in list(group.items()):
            if isinstance(item, h5py.Group):
                retdict[key] = dict()
                self.hdftodict(item, retdict[key])
            else:retdict[key] = item.value
            
        return retdict
    def updaterow(self,key,item,argitem):
        if isinstance(item,dict):
            parentkey = str(self.keylist)
            self.keylist+=key+';'
            #self.widgetdict[self.keylist] = (label,label,layout,False)
            for k in list(item.keys()):
                i = item[k]
                if k in argitem:
                    ai = argitem[k]
                    self.updaterow(k,i,ai)    
            self.keylist = str(parentkey)
            
        else:
            if isinstance(item,str):
                try:
                    text = self.widgetdict[self.keylist+key+';'][1]
                    text.setText(str(item))
                    text.textChanged = True
                    self.functiondict['Enter'](self.keylist+key+';',text)
                except Exception as e:
                    print('something wrong ',e)
            elif isinstance(item,float) or isinstance(item,int):
                text = self.widgetdict[self.keylist+key+';'][1]
                if key not in self.customwidgetdict:
                    text.setText(str(argitem)) 
                
                
                    #time.sleep(0.1)
                    text.textChanged = True
                    if 'Enter' in self.functiondict:self.functiondict['Enter'](self.keylist+key+';',text)
                else: text.updatetext(key,argitem)
            elif isinstance(item,list):
                text = self.widgetdict[self.keylist+key+';'][1]
                text.clear()
                #print(key)
                #print(argitem[0])
                text.insertItems(0,np.array(argitem[0],dtype=str))
            else:
                
                try:text = self.widgetdict[self.keylist+key+';'][1]
                except Exception as e:
                    print('something wrong here',e)
                #text.setText(str(item))
                #text.textChanged = True        
    def listofcheckedparameters(self): 
        ret=[]
        for key,item in self.valargs.items():
            #print(item)
            if item[1]==True:ret.append(key)
        return ret    
    @property
    def valargs(self):
        retdict = dict()
        #try:
        
        for key,tup in list(self.widgetdict.items()):
            label,widg,layout,check,minwidg,maxwidg = tup
            if isinstance(widg,QtWidgets.QComboBox):
                val = str(widg.currentText())
                retdict[key] = (val,check,(-1e10,1e10))
            elif isinstance(widg,QtWidgets.QLineEdit):
                val = str(widg.text())
                if isinstance(check,QtWidgets.QCheckBox):
                    chk = check.isChecked()
                else:
                    chk = check
                if val[0]=='-' or str(val[0]).isdigit() and minwidg:
                    
                    fval = float(val)
                    #print(key,minwidg,chk)
                    #mincheckey = key.split(';')
                    #maxcheckey = key.split(';')
                    #checkey.pop(-2)
                    if not isinstance(minwidg, bool):
                        #mincheckey[-2]=str(minwidg.text())
                        #maxcheckey[-2]=str(maxwidg.text())
                        #print(mincheckey)
                        #print(str(minwidg.text()),str(maxwidg.text()))
                        #mincheck = reduce(lambda x,y: x+';'+y,mincheckey)
                        #maxcheck = reduce(lambda x,y: x+';'+y,maxcheckey)
                        mincheck = self.checkforfloat(str(minwidg.text()))
                        maxcheck = self.checkforfloat(str(maxwidg.text()))
                        #print('min/max for ',key)
                        #print(mincheck,maxcheck)
                        if  mincheck and  maxcheck and chk:
                            minval = float(minwidg.text())
                            maxval = float(maxwidg.text())
                            #print('putting in retdict ',key,chk)
                            retdict[key] = (fval,chk,(minval,maxval))
                        elif not mincheck and  maxcheck and chk:
                            self.addminconstraint(retdict,key,str(minwidg.text()),float(maxwidg.text()))
                        elif  mincheck and not maxcheck and chk:
                            self.addmaxconstraint(retdict, key,float(minwidg.text()),str(maxwidg.text()))
                        elif not mincheck and not maxcheck and chk:
                            self.addminmaxconstraint(retdict,key,str(minwidg.text()),str(maxwidg.text()))
                        else:
                            minval = float(minwidg.text())
                            maxval = float(maxwidg.text())
                            retdict[key] = (fval,chk,(minval,maxval))
                    else:
                        #print(key)
                        retdict[key] = (fval,chk,(minwidg,minwidg))
                else:retdict[key] = (val,check,(-1e10,1e10))
            else:
                retdict[key] = (widg,check,(-1e10,1e10))
                #print fval,chk,(minval,maxval)
                
                #print 'didnt work', val,label.text()
                #retdict[key] = (val,check,(-1e10,1e10))
        #except Exception as e:
            #print('error in valargs')
            #print(e) 
            #print(widg,check,(-1e10,1e10),val)
            #retdict[key] = (val,check,(-1e10,1e10))

        
        return retdict
    def checkforfloat(self,keystr):
        check = True
        
        try:
            a=float(keystr)
            check=True
        except:check=False
       
        return check
                
                
    def addminconstraint(self,retdict,key,minstr,maxval):
        #the constrained parameter gets an expression 
        print('adding minimum')
        
        pval  = float(self.widgetdict[key][1].text())
        #cval = float(self.widgetdict[mincheck][1].text())
        #dval = pval-cval
        mincheck = minstr.replace(';','_')
        expsrs = 'Delta_'+key.replace(';','_')+'+'+mincheck
        retdict[key] = (pval,True,expsrs+' if '+expsrs+' < '+str(maxval)+' else ' +str(maxval)) 
        #we need to create a delta parameter
        retdict['Delta_'+key] = (0,True,(0,1e10))#this is approximate 
    def addmaxconstraint(self,retdict,key,minval,maxstr):
        print('adding maximum')
        #the constrained parameter gets an expression 
        pval  = float(self.widgetdict[key][1].text())
        #cval = float(self.widgetdict[mincheck][1].text())
        #dval = pval-cval
        maxcheck = maxstr.replace(';','_')
        expsrs = maxcheck+'-Delta_'+key.replace(';','_')
        retdict[key] = (pval,True,expsrs+' if '+expsrs+' > '+str(minval)+' else ' +str(minval)) 
        #we need to create a delta parameter
        retdict['Delta_'+key] = (0,True,(0,1e10))#this is approximate and assumes the initial guess is close 

    def addminmaxconstraint(self,retdict,key,minstr,maxstr):
        #the constrained parameter gets an expression 
        print('adding minimum and maximum')
        
        pval  = float(self.widgetdict[key][1].text())
        maxcheck = maxstr.replace(';','_')
        mincheck = minstr.replace(';','_')
        pvalexpr = maxcheck+'-Delta_'+key.replace(';','_')#+'+'+mincheck
        retdict[key] = (pval,True,pvalexpr + ' if '+pvalexpr +'>'+mincheck +' else ' +mincheck) 
        #we need to create a delta parameter
        
        retdict['Delta_'+key] = (0,True,(0,1e10))
class RandColorLayout(QtWidgets.QVBoxLayout):
    def __init__(self,color):
        super(RandColorLayout,self).__init__()
        self.color = [255-color[0],color[1],255-color[2]]
    def paintEvent(self,e):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(self.color))
        qp.drawRect(0, 0, self.size().width(), self.size().height())
        qp.end
