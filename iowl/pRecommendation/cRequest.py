 
__version__ = "$Revision: 1.1 $"

"""
$Log: cRequest.py,v $
Revision 1.1  2001/03/24 19:22:51  i10614
Initial revision

Revision 1.3  2001/02/22 12:17:07  a
basic network functionality

Revision 1.2  2001/02/19 19:20:04  a
added *Handler classes

Revision 1.1  2001/02/19 18:32:50  a
initial version

Revision 1.1  2001/02/19 18:20:28  a
initial version


"""

import urlparse
import cDOM
import cRule
import cItemset


class cRequest(cItemset.cItemset):

    """Request class.

    Internal representation of a request. Convert DOM to
    internal representation, convert internal representation into DOM.
    XXX should A request consists of one or more candidate-one-itemset.

    Now a request consists of one ore more urls stored in an itemset class

    """

    def __init__(self):
        """Constructor."""
        # XXX should be itemsets, now only urls are stored
        # in one itemset
        cItemset.cItemset.__init__(self)


    def ReturnRootElement(self):
        """Returns root element for request.

        return -- root element for this request

        """
        return self.GetElement()


    #def GetItemsets(self):
    #    """Return a list of itemsets stored in this class."""
    #    return self.lItemsets


    #def GetElement(self):
    #    """Return elements for storing in a DOM."""
#
   ##     lEls = []
 #       for itemset in self.lItemsets:
  #          el = itemset.GetElements()
     #       lEls.append(el)
#
 #       return lEls
#
#
 #   def SetElements(self, lEls):
  #      """Read elements into internal representation.
#
 #       lEls -- elements
  #      
   ##     """
     #   for el in lEls:
      #      itemset = cItemset.cItemset()
       #     itemset.SetElements(el)
        #    self.lItemsets.append(itemset)
