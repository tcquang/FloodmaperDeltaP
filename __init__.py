# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FloodMap
                                 A QGIS plugin
 Flood maps for DeltaP model
                             -------------------
        begin                : 2019-03-29
        copyright            : (C) 2019 by Truong Chi Quang/CTU
        email                : tcquang@ctu.edu.vn
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
    """Load FloodMap class from file FloodMap.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from flood_map import FloodMap
    return FloodMap(iface)
