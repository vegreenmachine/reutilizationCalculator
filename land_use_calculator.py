# -*- coding: utf-8 -*-
"""
/***************************************************************************
 reutilizationCaluculator
                                 A QGIS plugin
 This plugin is designed to propose options for reutilization for abandoned or misused land. 
                              -------------------
        begin                : 2017-12-01
        git sha              : $Format:%H$
        copyright            : (C) 2017 by GreenVenice
        email                : ve17.green@gmail.com
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

from qgis.core import QgsMapLayerRegistry, QgsField, QgsExpression
from qgis.gui import QgsMapLayerProxyModel
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from land_use_calculator_dialog import reutilizationCaluculatorDialog
import os.path
import time

class reutilizationCaluculator:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
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
            'reutilizationCaluculator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Land Re-Utilization Calculator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'reutilizationCaluculator')
        self.toolbar.setObjectName(u'reutilizationCaluculator')

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
        return QCoreApplication.translate('reutilizationCaluculator', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = reutilizationCaluculatorDialog()

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

        icon_path = ':/plugins/reutilizationCaluculator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Land Re-utilization Calculator'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Land Re-Utilization Calculator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
	# Calculate and return score of land
    def calculateScores(self):
	#the following values for attributes of land were calculated using matlab
	#the methodology behind the value is based on feedback from urban planners, 
	#ecology professors, and other professions
        upkeep = 3
        litter = 4
        bio = 4
        rich = 3
        hyg = 1
        invase = 1
      
        upkeep *= self.dlg.comboBox_2.currentIndex()
        litter *= self.dlg.comboBox_3.currentIndex()
        bio *= self.dlg.comboBox_4.currentIndex()
        rich *= self.dlg.comboBox_5.currentIndex()
        hyg *= self.dlg.comboBox_7.currentIndex()
        invase *= self.dlg.comboBox_8.currentIndex()
        rawScore = upkeep + litter + bio + rich + hyg +invase
		#this is a formula that makes the score go from 0 to 100
        scaledScore = int(round((rawScore - 16)*2.08))	
        return scaledScore
	#function to return condition based on scaled score
    def calculateCondition(self):
	    if self.calculateScores() >= 81:
		    condition = "Excellent"
	    elif self.calculateScores() >=52:
			condition = "Good"
	    elif self.calculateScores() >=23:
		    condition = "Fair"
	    else:
		    condition = "Poor"
	    return condition
	#the following function goes through rubrics and flowcharts designed
	#to calculate the reutilization options of specific lands. These
	#tools were designed by students of the Worcester Polytechnic Institute
	#as part of research conducted on the Green Spaces on Giudecca in Italy
    def calculateClassification(self):
		if self.dlg.comboBox.currentIndex() == 1:
			public = True
			privateAccess = False
		elif self.dlg.comboBox.currentIndex() == 2:
			privateAccess = True
			public = False
		else:
			privateAccess = False
			public = False
		if privateAccess and self.calculateScores() < 23:
			classification = "Urban Wild"
		elif public and self.calculateScores <23:
			classification = "Urban Wild"
		elif public and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) <= 400:
			classification = "Park"
		elif public and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 400 and self.dlg.comboBox_10.currentIndex() == 2 :
			classification  = "Park"
		elif public and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 400 and self.dlg.comboBox_10.currentIndex() == 1 :
			classification = "Urban Farm"
		elif privateAccess and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) < 1000 and self.dlg.comboBox_10.currentIndex() == 1 :
			classification = "Private Garden"
		elif privateAccess and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) < 1000 and self.dlg.comboBox_10.currentIndex() == 2 :
			classification = "Park"
		elif privateAccess and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and self.dlg.comboBox_2.currentIndex() < 2 :
			classification = "Urban Wild"
		elif privateAccess and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and self.dlg.comboBox_2.currentIndex() > 1 and self.dlg.comboBox_11.currentIndex() == 2 :
			classification = "Urban Wild"
		elif privateAccess and self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and self.dlg.comboBox_2.currentIndex() > 1 and self.dlg.comboBox_11.currentIndex() == 1 :
			classification = "Park"
		else:
			classification = "Something Went Horribly Wrong"
		return classification
		#within each ones of the major classifications: Urban Wilds, Urban Farmland, 
		#Private Garden, and Park, there are further reutilizations. This function
		#calculates and returns them
    def calculateReutilization(self):
		if self.calculateClassification() == "Park":
			if self.dlg.comboBox_12.currentIndex() == 1:
				reutilization = "Animal Sanctuary"
			elif self.dlg.comboBox_12.currentIndex() == 2 and int(self.dlg.textEdit.toPlainText()) <= 300 :
				reutilization = "Green Square"
			elif self.dlg.comboBox_12.currentIndex() == 2 and int(self.dlg.textEdit.toPlainText()) > 300 and self.calculateScores() >= 81:
				reutilization = "Social Gatherings"
			elif self.dlg.comboBox_12.currentIndex() == 2 and int(self.dlg.textEdit.toPlainText()) > 300 and self.calculateScores() < 81 and self.dlg.comboBox_6.currentIndex() == 1:
				reutilization = "Recreational Area"
			elif self.dlg.comboBox_12.currentIndex() == 2 and int(self.dlg.textEdit.toPlainText()) > 300 and self.calculateScores() < 81 and self.dlg.comboBox_6.currentIndex() == 2:
				reutilization = "Green Square"
			else:
				reutilization = "Something Went Wrong"
		elif self.calculateClassification() == "Urban Wild":
			if self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and self.dlg.comboBox_12.currentIndex() == 1:
				reutilization = "Transform to Park"
			elif self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and self.dlg.comboBox_12.currentIndex() == 2 and self.dlg.comboBox_5.currentIndex() > 2 and self.dlg.comboBox_10.currentIndex() == 1:
				reutilization = "Transform to Farmland"
			elif self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and self.dlg.comboBox_12.currentIndex() == 2 and self.dlg.comboBox_5.currentIndex() > 2 and self.dlg.comboBox_10.currentIndex() == 2:
				reutilization = "Transform to Park"
			elif self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and privateAccess and self.dlg.comboBox_16.currentIndex() == 1:
				reutilization =  "Transform to Private Garden"
			elif self.calculateScores() >= 23 and int(self.dlg.textEdit.toPlainText()) > 1000 and privateAccess and self.dlg.comboBox_16.currentIndex() == 2:
				reutilization =  "Green Square"
			elif self.calculateScores() < 23 and int(self.dlg.textEdit.toPlainText()) < 1000:
				reutilization =  "Small Scale Development"
			else:
				reutilization = "Something Went Wrong"
		elif self.calculateClassification() == "Urban Farm":
			if self.dlg.comboBox_13.currentIndex() == 1:
				reutilization = "Farm to Table"
			elif self.dlg.comboBox_13.currentIndex() == 2 and self.dlg.comboBox_14.currentIndex() == 1:
				reutilization = "Farmer's Market"
			elif self.dlg.comboBox_13.currentIndex() == 2 and self.dlg.comboBox_14.currentIndex() == 2:
				reutilization = "Community Farm"
			else:
				reutilization = "Something Went Wrong"
		elif self.calculateClassification() == "Private Garden":
			reutilization = "Reutilization N/A"
		else:
			reutilization = "Something Went Wrong"
		return reutilization
		#this function adds the data layers to a comboBox at the top of the UI
    def populateLayerList(self):
		layers = self.iface.legendInterface().layers()
		layer_list = []
		for layer in layers:
			layer_list.append(layer.name())
		self.dlg.comboBox_15.addItems(layer_list)
		#this function checks if the attributes exist in the attribute table
    def attributesNotAdded(self):
		combo_layer = self.dlg.comboBox_15.currentText()
		selected_layer = QgsMapLayerRegistry.instance().mapLayersByName(combo_layer)[0]
		condition = "Condition"
		reutil = "Re-Utilization"
		index_cond = selected_layer.fieldNameIndex(condition)
		index_reutil = selected_layer.fieldNameIndex(reutil)
		
		if index_cond == -1:
			return True
		else:
			return False
	#this function resets the UI to the original state
    def resetDialog(self):
		self.dlg.comboBox.setCurrentIndex(0)
		self.dlg.comboBox_2.setCurrentIndex(0)
		self.dlg.comboBox_3.setCurrentIndex(0)
		self.dlg.comboBox_4.setCurrentIndex(0)
		self.dlg.comboBox_5.setCurrentIndex(0)
		self.dlg.comboBox_6.setCurrentIndex(0)
		self.dlg.comboBox_7.setCurrentIndex(0)
		self.dlg.comboBox_8.setCurrentIndex(0)
		self.dlg.comboBox_9.setCurrentIndex(0)
		self.dlg.comboBox_10.setCurrentIndex(0)
		self.dlg.comboBox_11.setCurrentIndex(0)
		self.dlg.comboBox_12.setCurrentIndex(0)
		self.dlg.comboBox_13.setCurrentIndex(0)
		self.dlg.comboBox_14.setCurrentIndex(0)
		self.dlg.comboBox_15.setCurrentIndex(0)
		self.dlg.comboBox_16.setCurrentIndex(0)
		self.dlg.textEdit.setText("")
		self.dlg.textEdit_2.setText("")
		self.dlg.textEdit_3.setText("")
		self.dlg.textEdit_4.setText("")
		self.dlg.textEdit_5.setText("")
	    
		#Add attributes to the attribute table if they are not there already
		#Go through all the polygons selected and fill in data for those polygons
    def addAttributesToLayer(self):
		combo_layer = self.dlg.comboBox_15.currentText()
		selected_layer = QgsMapLayerRegistry.instance().mapLayersByName(combo_layer)[0]
		selected_layer.startEditing()
		
		if self.attributesNotAdded():
			selected_layer.dataProvider().addAttributes( [ QgsField("Condition", QVariant.String) ] )
			selected_layer.dataProvider().addAttributes( [QgsField("Re-Util", QVariant.String) ] )
			selected_layer.dataProvider().addAttributes( [QgsField("Score", QVariant.Int) ] )
			selected_layer.dataProvider().addAttributes( [QgsField("Comments", QVariant.String) ] )
			selected_layer.updateFields()
			
		selected_polygons = selected_layer.selectedFeatures()
		for feature in selected_polygons:
			selected_layer.changeAttributeValue(feature.id(), selected_layer.fieldNameIndex('Condition'), self.dlg.textEdit_3.toPlainText())
			selected_layer.changeAttributeValue(feature.id(), selected_layer.fieldNameIndex('Re-Util'), self.dlg.textEdit_4.toPlainText())
			selected_layer.changeAttributeValue(feature.id(), selected_layer.fieldNameIndex('Score'), str(self.dlg.textEdit_5.toPlainText()))
			selected_layer.changeAttributeValue(feature.id(), selected_layer.fieldNameIndex('Comments'), self.dlg.textEdit_2.toPlainText())
		selected_layer.commitChanges()
    def run(self):
        """Run method that performs all the real work"""
        self.populateLayerList();
        self.dlg.show()
        # # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            #fill in the textboxes with proper data
            self.dlg.textEdit_3.setText(self.calculateCondition())
            self.dlg.textEdit_4.setText(self.calculateClassification() + "-->" + self.calculateReutilization())
            self.dlg.textEdit_5.setText(str(self.calculateScores()))
            self.addAttributesToLayer()
            self.dlg.show()
            resultAgain = self.dlg.exec_()
            if resultAgain: #if the ok button is pressed again, then reset the dialog and close it
                self.resetDialog()
                self.dlg.close()
            
