#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  v2.0 Updated for KiCad 6.0

from __future__ import division
import pcbnew
from math import radians, sin, cos

import FootprintWizardBase

class SpiralAntFootprintWizard(FootprintWizardBase.FootprintWizard):

    def GetName(self):
        return "Spiral Antenna"

    def GetDescription(self):
        return "Spiral Antenna wizard"

    def GetValue(self):
        turns = self.parameters["spiral"]["turns"]
        tw = self.parameters["spiral"]["width"]
        td = self.parameters["spiral"]["distance"]
        return "SpiralAnt%d_%d_%d" % (turns,tw,td)

    def GenerateParameterList(self):
        self.AddParam( "spiral", "turns", self.uInteger, 10 )
        self.AddParam( "spiral", "width", self.uMM, 0.2 )
        self.AddParam( "spiral", "distance", self.uMM, 0.4 )
        self.AddParam( "spiral", "innerRadius", self.uMM, 2 )
        self.AddParam( "spiral", "segments", self.uInteger, 40 )
        self.AddParam( "spiral", "spin", self.uInteger, 1)
        # self.AddParam( "spiral", "startAngle", self.uInteger, 0)
        self.AddParam( "spiral", "mirror", self.uBool, 1)
        # self.AddParam( "Pads", "height", self.uMM, 1.6)

    def CheckParameters(self):
        #TODO implement custom parameter checking
        pass
    
    def makeVia(self, size, drill, pos, attrib=pcbnew.PAD_ATTRIB_PTH):
        via = pcbnew.PAD(self.module)
        via.SetSize(pcbnew.wxSize(size, size))
        via.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        via.SetAttribute(attrib)
        via.SetDrillSize(pcbnew.wxSize(drill, drill))
        if (attrib == pcbnew.PAD_ATTRIB_PTH):
            via.SetLayerSet(via.PTHMask())
        else:
            via.SetLayerSet(via.SMDMask())
        via.SetPos0(pos)
        via.SetPosition(pos)
        self.module.Add(via)
        return via


    def BuildThisFootprint(self):
        p = self.parameters
        turns = int(p["spiral"]["turns"])
        radius = p["spiral"]["innerRadius"]
        segs = p["spiral"]["segments"]
        tw = p["spiral"]["width"]
        td = p["spiral"]["distance"]
        spin = p["spiral"]["spin"]
        startangle = 0 #p["spiral"]["startAngle"]
        mirror = bool(p["spiral"]["mirror"])
        
        self.draw.SetLineThickness(tw)
        
        baseX = 0
        baseY = 0
        endX, endY = 0, 0
        radius = radius# - (td-tw)/2
        for j in range(turns):
            segangle = 360. / segs
            segradius = td / segs
            for i in range(int(segs)):
                self.draw.SetLayer(pcbnew.F_Cu)
                startX = baseX 
                startX = baseX + (radius + segradius * i + td * j) * sin(radians(segangle*spin*i + startangle))
                startY = baseY + (radius + segradius * i + td * j) * cos(radians(segangle*spin*i + startangle))
                endX = baseX + (radius + segradius * (i + 1.0) + td * j) * sin(radians(segangle*spin*(i + 1.0) + startangle))
                endY = baseY + (radius + segradius * (i + 1.0) + td * j) * cos(radians(segangle*spin*(i + 1.0) + startangle))
                if j == turns-1 and i == int(segs)-1: #last segment of spiral
                    endX -= td
                    # continue
                self.draw.Line( startX, startY, endX, endY)
                if mirror:
                    self.draw.SetLayer(pcbnew.B_Cu)
                    self.draw.SetLineThickness(tw)
                    self.draw.Line( -startX, startY, -endX, endY)
        if mirror:
            self.draw.SetLayer(pcbnew.F_Cu)
            viaSize = pcbnew.FromMM(0.6)
            drillSize = pcbnew.FromMM(0.3)

            pos = pcbnew.wxPoint(baseX, baseY-viaSize/2+radius)
            self.makeVia(viaSize, drillSize, pos)

            # TODO proper direction of via offset!
            self.draw.SetLayer(pcbnew.B_Cu)
            self.draw.Line(baseX, baseY+radius, baseX, baseY-viaSize/2+radius)
            self.draw.SetLayer(pcbnew.F_Cu)
            self.draw.Line(baseX, baseY+radius, baseX, baseY-viaSize/2+radius)
            # via.SetName("V")

            #outer via
            pos = pcbnew.wxPoint(-endX, endY+viaSize)
            padB = self.makeVia(viaSize, drillSize, pos)
            self.draw.SetLayer(pcbnew.B_Cu)
            self.draw.Line(-endX, endY, -endX, endY+viaSize)
            padB.SetName("2")


            pos = pcbnew.wxPoint(endX, endY+viaSize/2-tw/4)
            padFa = self.makeVia(drillSize, drillSize, pos, pcbnew.PAD_ATTRIB_SMD)
            padFa.SetShape(pcbnew.PAD_SHAPE_OVAL)
            padFa.SetSize(pcbnew.wxSize(tw, viaSize+tw/2))
            padFa.SetName("1")

            pos = pcbnew.wxPoint(endX, endY+viaSize)
            padF = self.makeVia(drillSize, drillSize, pos, pcbnew.PAD_ATTRIB_SMD)
            padF.SetName("1")
            # self.draw.SetLayer(pcbnew.F_Cu)
            # self.draw.Line(endX, endY, endX, endY+viaSize)


            # set courtyard line thickness to the one defined in KLC
            # self.draw.SetLineThickness(pcbnew.FromMM(0.05))
            # self.draw.Line( -max_x, min_y, max_x, min_y )
            # self.draw.Line( max_x, min_y, max_x, max_y )

SpiralAntFootprintWizard().register()
