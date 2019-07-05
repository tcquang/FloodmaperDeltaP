# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FloodMap
                                 A QGIS plugin
 Flood maps for DeltaP model
                              -------------------
        begin                : 2019-03-29
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Truong Chi Quang/CTU
        email                : tcquang@ctu.edu.vn
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.analysis
import qgis.core
from qgis.utils import iface
from qgis.PyQt.QtGui import QColor
import re

# Initialize Qt resources from file resources.py
import resources
import processing
# Import the code for the dialog
from flood_map_dialog import FloodMapDialog
import os.path
import csv
import time

from qgis.analysis import QgsRasterCalculator,QgsRasterCalculatorEntry

class FloodMap:
    """QGIS Plugin Implementation."""
    file_toado =""
    file_hh_max=""
    file_dem=""
    d=[]
    
    matrix_mucnuoc=[]
    thumucchuadulieu=""
    danhsach=[]
    file_stylemax="" # os.path.dirname(__file__) + "/mau_tomau.qml"
    file_stylegio=""
    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'FloodMap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Flood map')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'FloodMap')
        self.toolbar.setObjectName(u'FloodMap')
        # Create the dialog (after translation) and keep reference
        self.dlg = FloodMapDialog()
        self.dlg.txtFilemax.clear()
        self.dlg.pushButton.clicked.connect(self.open_hh_max)
        # Mở file Dem
        self.dlg.txtDem.clear()
        self.dlg.btnOpenDEM.clicked.connect(self.open_dem)
        # Mở file  Toa do mat cat
        self.dlg.txtToado.clear()
        self.dlg.btnMatcat.clicked.connect(self.open_toado)
        # Mở file muc nuoc theo gio
        self.dlg.txtFileGio.clear()
        self.dlg.btnNgapGio.clicked.connect(self.open_ngap_gio)
        # Mở file Vung ranh giơi
        self.dlg.txtRanhgioi.clear()
        self.dlg.btnRanhgioi.clicked.connect(self.open_ranhgioi)
        # nuts leenhj mowr file toaj do
        self.dlg.btnNapDl.clicked.connect(self.chon_dulieu_mucnuoc)
        # Noi suy muc nuoc max
        self.dlg.btnBandoMax.clicked.connect(self.load_bd_diem_mucnuocmax)
        # Chọn thư mục
        self.dlg.btnThumuc.clicked.connect(self.chonthumuc)
        # Chon dong du lieu trich tao ban do
        self.dlg.cboNgaybatdau.currentIndexChanged.connect(self.chon_dot)
        # ban do muc nuoc theo gio
        self.dlg.btnNgapgio.clicked.connect(self.bando_mucnuoc_theogio)
        # mở bản đồ style mực nước max
        self.dlg.btnStyle_max.clicked.connect(self.open_stylemax)
        # open_style_gio
        self.dlg.btnStyle_gio.clicked.connect(self.open_stylegio)        
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('FloodMap', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """



        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        global file_stylemax
        global file_stylegio
        icon_path = ':/plugins/FloodMap/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Flood Map'),
            callback=self.run,
            parent=self.iface.mainWindow())
        file_stylemax = os.path.dirname(__file__) + "/style_ngapmax.qml"
        self.dlg.txtStylemax.setText(file_stylemax)
        
        file_stylegio = os.path.dirname(__file__) + "/mau_tomau.qml"
        self.dlg.txtStylegio.setText(file_stylegio)
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Flood map'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def open_hh_max(self):
        global file_hh_max
        file_hh_max = QFileDialog.getOpenFileName(self.dlg,u"Mở file mực nước Max","",'*.HSUM')
       # filename = QFileDialog.getSaveFileName(self.dlg, "Select output file ","", '*.txt')
        self.dlg.txtFilemax.setText(file_hh_max)

    def open_dem(self):
        global file_dem
        file_dem = QFileDialog.getOpenFileName(self.dlg,u"Mở file DEM","",'*.tif')
        self.dlg.txtDem.setText(file_dem)

    def open_toado(self):
        global file_toado
        file_toado = QFileDialog.getOpenFileName(self.dlg,u"Mở file tọa độ mặt cắt","",'*.shp')
        self.dlg.txtToado.setText(file_toado)
    def open_ngap_gio(self):
        global file_ngap_gio
        file_ngap_gio = QFileDialog.getOpenFileName(self.dlg,u"Mở file mực nước giờ","",'*.HHH')
        self.dlg.txtFileGio.setText(file_ngap_gio)
        self.load_cboNgaygio()
    def open_stylemax(self):
        global file_stylemax
        file_toado = QFileDialog.getOpenFileName(self.dlg,u"Mở file style mực nước max","",'*.qml')
        self.dlg.txtStylemax.clear()
        self.dlg.txtStylemax.setText(file_stylemax)
    def open_stylegio(self):
        global file_stylegio
        file_toado = QFileDialog.getOpenFileName(self.dlg,u"Mở file style mực nước theo giờ","",'*.qml')
        self.dlg.txtStylegio.clear()
        self.dlg.txtStylegio.setText(file_stylegio)
        
    def open_ranhgioi(self):
        file_ranhgioi = QFileDialog.getOpenFileName(self.dlg,u"Mở file ranh giới","",'*.shp')
        self.dlg.txtRanhgioi.setText(file_ranhgioi)
    def chonthumuc(self):
        global thumucchuadulieu
        thumucchuadulieu = QFileDialog.getExistingDirectory(self.dlg,u"Chọn thư mục đẻ lưu kết quả", "D:\dulieu_plugin\ketquanoisuy")
        self.dlg.txtThumuc.setText(thumucchuadulieu)
    def doc_dulieuhhmax(self):
        QMessageBox.information(self.iface.mainWindow(),"Thong Bao", u"Mở dữ liệu mực nước max" )
        # Kết nối dữ liệu mực nước max vào file tọa độ
        res = processing.runalg("qgis:joinattributestable","d:/dulieu_plugin/diem_mucnuoc_camau.shp","d:/dulieu_plugin/toado1.csv","Nhanh","stt","d:/dulieu_plugin/join_mucnuoc_max.shp")
        layer = QgsVectorLayer(res['OUTPUT_LAYER'], "toado_mucnuocmax", "ogr")
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        layer = qgis.utils.iface.activeLayer() 
        # nap combobox
        lyr = iface.activeLayer()
        idx = lyr.dataProvider().fieldNameIndex( 'NAME_1' ) 
        uv = lyr.dataProvider().uniqueValues( idx )
        cb = QComboBox()
        cboNgaybatdau.addItems( uv )  
    def load_bd_diem_mucnuocmax(self):
        global thumucchuadulieu
        global file_hh_max
        global file_toado
        global file_dem
        
        s = QSettings()
        oldValidation = s.value( "/Projections/defaultBehaviour")
        s.setValue( "/Projections/defaultBehaviour", "useGlobal" )
        InFlnm='Diem_mucnuocMax'
        #InDrPth='D:/dulieu_plugin/'
        InFlPth="file:///"+file_hh_max
        #---  6 Set import Sting here note only need to set x and y other come for free
        uri = InFlPth+"?crs=epsg:32648&delimiter=%s&xField=%s&yField=%s" % ("\t","XX","YY")
        #--- 7 Load point layer
        bh = QgsVectorLayer(uri, InFlnm, "delimitedtext")
        bh.isValid()
        file_diemmax = thumucchuadulieu + "/diem_mucnuocmax.shp"
        crs=QgsCoordinateReferenceSystem("epsg:32648")
        error = QgsVectorFileWriter.writeAsVectorFormat(bh, file_diemmax, "UTF-8", crs , "ESRI Shapefile")
        layer = QgsVectorLayer(file_diemmax, "Diem_mucnuocMax", "ogr")
        QgsMapLayerRegistry.instance().addMapLayers([layer])
        
        #QMessageBox.information(self.iface.mainWindow(),"Thong Bao", u"File tọa độ mực nước max: "  + file_toado)
        #layer = QgsVectorLayer(file_toado, "Diem_mucnuoc", "ogr")
        #QgsMapLayerRegistry.instance().addMapLayers([layer])
       # layer = qgis.utils.iface.activeLayer() 
        
        # noi suy muc nuoc
        layer_data = qgis.analysis.QgsInterpolator.LayerData()
        layer_data.vectorLayer = layer
        layer_data.zCoordInterpolation=False
       
        layer_data.interpolationAttribute =2
        layer_data.mInputType = 1
        idw_interpolator = qgis.analysis.QgsIDWInterpolator([layer_data])
        
        export_path = thumucchuadulieu + "/noisuy_max.asc"
        
        rect = layer.extent()
        res = 100
        ncol = int( ( rect.xMaximum() - rect.xMinimum() ) / res )
        nrows = int( (rect.yMaximum() - rect.yMinimum() ) / res)
        output =  qgis.analysis.QgsGridFileWriter(idw_interpolator,export_path,rect,ncol,nrows,res,res)
        output.writeFile(True)
        
        # load ban do noi suy
        layer_noisuy  = QgsRasterLayer(export_path, "bd_noisuy")
        #QgsMapLayerRegistry.instance().addMapLayers([layer_noisuy])
        #layer_noisuy = qgis.utils.iface.activeLayer() 
        # mo ban do DEM 
        layer_DEM  = QgsRasterLayer(file_dem, 'bd_DEM')
        #QgsMapLayerRegistry.instance().addMapLayers([layer_DEM])
        # layer_DEM = qgis.utils.iface.activeLayer() 
        # tinh DEM - ngap 2 lop raster
        try:
            entries = []
            # Define band1
            boh1 = QgsRasterCalculatorEntry()
            boh1.ref = 'boh@1'
            boh1.raster = layer_DEM
            boh1.bandNumber = 1
            entries.append( boh1 ) 
            # dinh nghia lop 2
            boh2 = QgsRasterCalculatorEntry()
            boh2.ref = 'boh1@1'
            boh2.raster = layer_noisuy
            boh2.bandNumber = 1
            entries.append( boh2 )    
            outputRas = thumucchuadulieu + "/bd_mucnuocmax.tif"
            QMessageBox.information(self.iface.mainWindow(),"Thong Bao", u"File kq tính toán: "  + outputRas)
          
            # Process calculation with input extent and resolution
            calc =QgsRasterCalculator('boh@1 - boh1@1',outputRas,'GTiff', layer_DEM.extent(), layer_DEM.width(), layer_DEM.height(), entries )
            calc.processCalculation()   
             # mo ban do tính toán 
            layer_ngap  = QgsRasterLayer(outputRas, 'bd_mucnuocmax')
            QgsMapLayerRegistry.instance().addMapLayers([layer_ngap])
            #self.tomau
           # style_layer =  os.path.dirname(__file__) + "/mau_tomau.qml"
            processing.runalg("qgis:setstyleforrasterlayer", outputRas,file_stylemax)
        except:
            self.userWarning("Error in Create map", "Can not create Create map, Exit")
    # Nội suy ban do muc nuoc max 
    def bando_mucnuoc_theogio(self):
        global file_toado
        global file_dem
        global thumucchuadulieu
        global danhsach
        #diem_mucnuoc_h
        layer=None
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            if lyr.name() == "diem_mucnuoc_h":
                layer = lyr
                break
        giatridau=self.dlg.cboNgaybatdau.currentIndex()-1
        sodot= int(self.dlg.txtSodot.text())
        buocnhay = int(self.dlg.boxBuocnhay.text())
        v_h = giatridau
        # noi suy muc nuoc
        while v_h < (giatridau+sodot * buocnhay):
            layer_data = qgis.analysis.QgsInterpolator.LayerData()
            layer_data.vectorLayer = layer
            layer_data.zCoordInterpolation=False
            cot_h="cot_h" + str(v_h)
            field_cot_h = layer.fieldNameIndex(cot_h)
            layer_data.interpolationAttribute = field_cot_h #7
            layer_data.mInputType = 1
            idw_interpolator = qgis.analysis.QgsIDWInterpolator([layer_data])
            export_path = thumucchuadulieu + "/ngap_" + str(danhsach[v_h+1]) +".asc"
            rect = layer.extent()
            res = 100
            ncol = int( ( rect.xMaximum() - rect.xMinimum() ) / res )
            nrows = int( (rect.yMaximum() - rect.yMinimum() ) / res)
            output =  qgis.analysis.QgsGridFileWriter(idw_interpolator,export_path,rect,ncol,nrows,res,res)
            output.writeFile(True)
            # load ban do noi suy
            layer_noisuy  = QgsRasterLayer(export_path, "ngap_" + str(danhsach[v_h+1]))
            # mo ban do DEM 
            layer_DEM  = QgsRasterLayer(file_dem, 'bd_DEM')
            #QgsMapLayerRegistry.instance().addMapLayers([layer_DEM])
            # tinh DEM - ngap 2 lop raster
            #try:
            entries = []
             # Define band1
            boh1 = QgsRasterCalculatorEntry()
            boh1.ref = 'boh@1'
            boh1.raster = layer_DEM
            boh1.bandNumber = 1
            entries.append( boh1 ) 
            # dinh nghia lop 2
            boh2 = QgsRasterCalculatorEntry()
            boh2.ref = 'boh1@1'
            boh2.raster = layer_noisuy
            boh2.bandNumber = 1
            entries.append( boh2 )    
            outputRas = thumucchuadulieu + "/ngap_" + str(danhsach[v_h+1]) +".tif"
            
            # Process calculation with input extent and resolution
            calc =QgsRasterCalculator('boh@1 - boh1@1',outputRas,'GTiff', layer_DEM.extent(), layer_DEM.width(), layer_DEM.height(), entries )
            calc.processCalculation()   
             # to mau
            #style_layer  # =  os.path.dirname(__file__) + "/mau_tomau.qml"
            processing.runalg("qgis:setstyleforrasterlayer", outputRas,file_stylegio)
            v_h = v_h+buocnhay   
        # mo ban do tính toán 
        #layer_ngap  = QgsRasterLayer(outputRas, "ngap_" + str(danhsach[v_h]))
        #QgsMapLayerRegistry.instance().addMapLayers([layer_ngap])
        #tenbando = "ngap_" + str(danhsach[v_h])
        #except:
        #    self.userWarning(u"Tạo bản đồ ngập", u"Lỗi tạo bản đồ ngập, Thoát.")
                
    #nap combo box ngay bat dau
    def load_cboNgaygio(self):
        global file_ngap_gio
        global d
        global danhsach
        with open(file_ngap_gio) as f:
            reader = csv.reader(f, delimiter=";")
            d = list(reader)
        danhsach=[]
        st = ''
        self.dlg.cboNgaybatdau.clear 
        #print d[0][1:5]
        #print d[1]
        #print "kich thuoc ma tran d:" + str(range(len(d)))
        #print "kich thuoc dong dau:" + str(range(len(d[0])))
        #print "kich thuoc dong dau -1:" + str(range(len(d[0])-1))
        for row in d: 
            st = row[1].strip() + "_" + row[2].strip() + "-" + row[3].strip() +  "-" + row[4].strip()
            danhsach = danhsach + [st]
        #print danhsach
        
        #danhsach=d[0][1:5]
        #layer = QgsVectorLayer(file_toado, "Diem_mucnuoc", "ogr")
        #QgsMapLayerRegistry.instance().addMapLayers([layer])
        #layer = qgis.utils.iface.activeLayer() 
        #idx = layer.dataProvider().fieldNameIndex('Mcat') 
        #uv = layer.dataProvider().uniqueValues( idx )
        self.dlg.cboNgaybatdau.addItems(danhsach)  
        
    def chon_dot(self):
        global d
        print  self.dlg.cboNgaybatdau.currentText()
        print self.dlg.cboNgaybatdau.currentIndex()
        
        # thu doc du liwu cua dong duoc chon 
        #print d[self.dlg.cboNgaybatdau.currentIndex()]
    #def taodanhsachdotchon(self):
        
    def chon_dulieu_mucnuoc(self):
        global d
        global file_toado 
        global thumucchuadulieu
        cot = len(d[0])-1
        if  (self.dlg.cboNgaybatdau.currentIndex() == 0) :
            QMessageBox.information(self.iface.mainWindow(),u"Thông báo", u"Bạn vui lòng chọn đợt dữ liệu bắt đầu")
        else:
        #   self.taodanhsachdotchon()
            dong1 = d[0][5:cot]
            for k in range(len(dong1)):
                dong1[k] = int(dong1[k])
            # save cac diem co trong danh muc chon ra file
            #file_toado = 'D:/dulieu_plugin/diem_mucnuoc.shp'
            layer = QgsVectorLayer(file_toado, "Diem_mucnuoc", "ogr")
            QgsMapLayerRegistry.instance().addMapLayers([layer])
            
            query = '\"Mcat\" in ('
            for k in range(len(dong1)-1):
                query = query + str(dong1[k]) +","
            query = query + str(dong1[len(dong1)-1]) + ')'  
            selection = layer.getFeatures(QgsFeatureRequest().setFilterExpression(query))
            layer.setSelectedFeatures([k.id() for k in selection])
            # Save du lieu tim duoc vao file ; True : chi save cac diem duco chon
            crs=QgsCoordinateReferenceSystem("epsg:32648")
            file_diem_selected = thumucchuadulieu + "/diem_mucnuoc_h.shp"
            error = QgsVectorFileWriter.writeAsVectorFormat(layer, file_diem_selected, "UTF-8", crs , "ESRI Shapefile", True )
            layerSelected = QgsVectorLayer(file_diem_selected, "diem_mucnuoc_h", "ogr")
            QgsMapLayerRegistry.instance().addMapLayers([layerSelected])
            # Them cot diem muc nuoc gio vao file diem muc nuoc gio
            giatridau=self.dlg.cboNgaybatdau.currentIndex()-1
            sodot= int(self.dlg.txtSodot.text())
            buocnhay = int(self.dlg.boxBuocnhay.text())
            v_h = giatridau
            while v_h < (giatridau+sodot * buocnhay):
                #print v_h
                #print matrixmoi
                cot_h="cot_h" + str(v_h)
                vpr = layerSelected.dataProvider()
                vpr.addAttributes([QgsField(cot_h, QVariant.Double)])
                layerSelected.updateFields()
                dong2 = d[v_h+1][5:cot]
                for k in range(len(dong2)):
                    dong2[k] = float(dong2[k])
                #_______________________________________________________________________________
                matrixmoi = [dong1,dong2]
                features=layerSelected.getFeatures()
                layer_provider=layerSelected.dataProvider()
                for f in features:
                    id=f.id()
                    fieldMatcat = layerSelected.fieldNameIndex("Mcat")
                    field_cot_h = layerSelected.fieldNameIndex(cot_h)
                    matcat=f.attributes()[fieldMatcat]
                    h_value = self.tim_h_matcat(matrixmoi,matcat)
                    attr_value={field_cot_h:h_value}
                    layer_provider.changeAttributeValues({id:attr_value})
                v_h = v_h+buocnhay
                layerSelected.commitChanges()
            QMessageBox.information(self.iface.mainWindow(),u"Thông báo", u"Đã xây dựng file dữ liệu điểm ngập theo thời gian xong"+"\n"+ u"Hãy chạy chức năng tạo bản đồ ngập theo giờ.")
            self.dlg.btnNgapgio.setEnabled(True) 
             # chay noi suy muc nuoc gio, luu thanh file
         
    def tim_h_matcat(self,matrixmoi_h, v_matcat): 
        h_mucnuoc = 0.0
        for j in range(len(matrixmoi_h[0])):   # so cot cua ma tran
            if matrixmoi_h[0][j] == v_matcat:
                h_mucnuoc = matrixmoi_h[1][j]
        return h_mucnuoc
    def mofilecsv(self):
        print u"Mở file CSV mực nước"
    
    def tomau(self, bandongap):
        #chua chay duoc
        #layer =  QgsMapLayerRegistry.instance().mapLayersByName('bd_ngap')[0]
        renderer = bandongap.renderer()
        provider = bandongap.dataProvider()
        band = renderer.usesBands()
        min = provider.bandStatistics(band[0], QgsRasterBandStats.All).minimumValue
        max = provider.bandStatistics(band[0], QgsRasterBandStats.All).maximumValue
        print "min: {:.1f}, max: {:.1f}".format(min, max)
        myStyle = QgsStyleV2().defaultStyle()
        ramp_names = myStyle.colorRampNames()
        dict = {}
        for i, name in enumerate(ramp_names):
            dict[ramp_names[i]] = i 
        print 'Blues ramp is number:', dict['Blues']
        ramp = myStyle.colorRamp('Blues')  #RdYlGn ramp
        print ramp_names[dict['Blues']]
        rp = ramp.properties()
        print rp
        #To set an interpolated color RdYlGn ramp shader with five classes
        number_classes = 10
        interval = (max - min)/(number_classes -1 )
        print "class interval: ", interval
        #classes
        sum = min
        classes = []
        for i in range(number_classes):
            tmp = round(sum, 1)
            print 'class {:d}: {:f}'.format(i+1, tmp)
            classes.append(tmp)
            sum += interval
        print "classes: ", classes
        c1 = [ int(element) for element in rp['color1'].split(',') ]
        stops = [ element for element in re.split('[,;:]', rp['stops']) ]
        c2 = [ int(element) for element in rp['color2'].split(',') ]
        color_list = [ QgsColorRampShader.ColorRampItem(classes[0], QColor(c1[0],c1[1],c1[2], c1[3])),
                       QgsColorRampShader.ColorRampItem(classes[1], QColor(int(stops[1]),int(stops[2]),int(stops[3]),int(stops[4]))),
                       QgsColorRampShader.ColorRampItem(classes[2], QColor(int(stops[6]),int(stops[7]),int(stops[8]),int(stops[9]))),
                       QgsColorRampShader.ColorRampItem(classes[3], QColor(int(stops[11]),int(stops[12]),int(stops[13]),int(stops[14]))),
                       QgsColorRampShader.ColorRampItem(classes[4], QColor(c2[0],c2[1],c2[2], c2[3])) ]
        myRasterShader = QgsRasterShader()
        myColorRamp = QgsColorRampShader()
        myColorRamp.setColorRampItemList(color_list)
        myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
        myRasterShader.setRasterShaderFunction(myColorRamp)
        myPseudoRenderer = QgsSingleBandPseudoColorRenderer(bandongap.dataProvider(), 1,  myRasterShader)
        bandongap.setRenderer(myPseudoRenderer)
        bandongap.triggerRepaint()    
        
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
