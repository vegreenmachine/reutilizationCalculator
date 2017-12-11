# -*- coding: utf-8 -*-
"""
/***************************************************************************
 reutilizationCaluculator
                                 A QGIS plugin
 This plugin is designed to propose options for reutilization for abandoned or misused land. 
                             -------------------
        begin                : 2017-12-01
        copyright            : (C) 2017 by GreenVenice
        email                : ve17.green@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load reutilizationCaluculator class from file reutilizationCaluculator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .land_use_calculator import reutilizationCaluculator
    return reutilizationCaluculator(iface)
