 
__version__ = "$Revision: 1.1 $"

"""
$Log: cAnswer.py,v $
Revision 1.1  2001/03/24 19:22:51  i10614
Initial revision

Revision 1.5  2001/02/22 15:13:51  a
owls gives recommendation to itself

Revision 1.4  2001/02/22 12:17:07  a
basic network functionality

Revision 1.3  2001/02/19 19:20:04  a
added *Handler classes

Revision 1.2  2001/02/19 18:32:50  a
initial version

Revision 1.1  2001/02/19 18:20:28  a
initial version


"""

import urlparse
import cDOM
import cRule


class cAnswer:

    """Answer class.

    Internal representation of an answer of a request. Convert DOM to
    internal representation, convert internal representation into DOM.
    Rules are stored in a list of cRule.

    """

    def __init__(self):
        """Constructor."""
        self.lRules = []


    def SetRules(self, lRules):
        """Set a list of rules.

        lRules -- list of rules

        """
        self.lRules = lRules


    def GetRules(self):
        """Return list of rules.

        return -- lRules

        """
        return self.lRules


    def GetElement(self):
        """Return elements for storing in a DOM."""
        foo = cDOM.cDOM()

        lEls = []
        for rule in self.lRules:
            el = rule.GetElement()
            lEls.append(el)

        contEl = foo.CreateElementContainer('rules', {}, lEls)

        return contEl


    def SetElement(self, contEl):
        """Read elements into internal representation.

        contEl -- elements
        
        """
        foo = cDOM.cDOM()
        
        dAttrs, lEls = foo.GetElementContainerContent(contEl, 'rules', None)

        for el in lEls:
            rule = cRule.cRule()
            rule.SetElement(el)
            self.lRules.append(rule)
