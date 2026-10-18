"""Wrapping tool controls, including when application text is enlarged."""
from PySide6.QtCore import QEvent,QRect,QSize,Qt
from PySide6.QtWidgets import QLayout,QSpacerItem,QSizePolicy,QWidget


class WrappingPanel(QWidget):
    """Reserve enough height for controls that wrap at narrow widths."""
    def _fit_height(self):
        if self.layout():
            height=max(0,self.layout().heightForWidth(self.width()))
            if height!=self.minimumHeight():self.setMinimumHeight(height)

    def resizeEvent(self,event):
        super().resizeEvent(event);self._fit_height()

    def event(self,event):
        handled=super().event(event)
        if event.type()==QEvent.Type.LayoutRequest:self._fit_height()
        return handled


class FlowLayout(QLayout):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.items=[]
        self.setContentsMargins(0,0,0,0)
        self.setSpacing(6)

    def addItem(self,item):self.items.append(item)
    def addWidget(self,widget,*args):super().addWidget(widget)
    def count(self):return len(self.items)
    def itemAt(self,index):return self.items[index] if 0<=index<len(self.items) else None
    def takeAt(self,index):return self.items.pop(index) if 0<=index<len(self.items) else None
    def addStretch(self,*args):pass
    def expandingDirections(self):return Qt.Orientation(0)
    def hasHeightForWidth(self):return True
    def heightForWidth(self,width):return self.arrange(QRect(0,0,width,0),False)
    def sizeHint(self):return self.minimumSize()
    def minimumSize(self):
        size=QSize()
        for item in self.items:
            if not item.isEmpty():size=size.expandedTo(item.minimumSize())
        return size

    def setGeometry(self,rect):
        super().setGeometry(rect)
        self.arrange(rect,True)

    def arrange(self,rect,apply):
        x,y,height=rect.x(),rect.y(),0
        for item in self.items:
            if item.isEmpty():continue
            size=item.sizeHint()
            width=min(size.width(),rect.width())
            if x>rect.x() and x+width>rect.right()+1:
                x=rect.x();y+=height+self.spacing();height=0
            if apply:item.setGeometry(QRect(x,y,width,size.height()))
            x+=width+self.spacing();height=max(height,size.height())
        return y+height-rect.y()
