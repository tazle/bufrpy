.. _examples:

Examples
========

RDT Contour Extraction
----------------------


.. code:: python

 import bufrpy
 from bufrpy.template import safnwc
 import re
 import itertools
 import sys

 def to_rings(bufrmsg):
     """ Return a list of cloud contours as closed rings, in lat/lon ordinate order"""
     out = []
     subsets = bufrmsg.section4.subsets
     for subset in subsets:
         for cloudsystem in subset.values[19]: # cloud systems are at index 19
             contour = cloudsystem[0] # contour is at index 0 of cloud system
             point_vals = list(itertools.chain(contour, itertools.islice(contour,1))) # close contour
             points = []
             for (lat, lon) in point_vals:
                 points.append((lat.value, lon.value)) # extract values
             out.append(points)
     return out

 def to_wkt(rings):
     out = []
     for ring in rings:
         # Change ordinate order, convert to strings, join and stick in a POLYGON
         points = [" ".join(map(str, reversed(latlon))) for latlon in ring]
         edge = ",".join(points)
         out.append("POLYGON((" + edge + "))")
     return "\n".join(out)

 if __name__ == '__main__':

     template = safnwc.read_template(open(sys.argv[1], 'rb'))
     msg = bufrpy.bufrdec_file(open(sys.argv[2], 'rb'), template)

     rings = to_rings(msg)
     wkt = to_wkt(rings)

     print wkt
