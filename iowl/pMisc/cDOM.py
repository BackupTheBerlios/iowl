
__version__ = "$Revision: 1.1 $"

"""
$Log: cDOM.py,v $
Revision 1.1  2001/03/24 19:23:01  i10614
Initial revision

Revision 1.7  2001/02/20 17:37:05  a
minor changes

Revision 1.6  2001/02/19 21:46:44  a
good night

Revision 1.5  2001/02/19 19:31:20  a
minor changes

Revision 1.4  2001/02/16 22:47:06  mbauer
added ParseString() to parse xml contained in string instead of file

Revision 1.3  2001/02/15 20:44:12  a
dunno what changed

Revision 1.2  2001/02/14 17:22:13  a
minor changes

Revision 1.1  2001/02/14 16:47:41  a
changed GetElementContent method

Revision 1.8  2001/02/13 15:45:47  a
included cFile into cItemsets and cAssoRules, added cStatistics

Revision 1.7  2001/02/12 23:11:45  a
changed to new naming scheme

Revision 1.6  2001/02/12 21:13:42  a
changed AssoRules

Revision 1.5  2001/02/12 17:49:14  a
mostly documentation changes

Revision 1.4  2001/02/11 17:40:25  a
multiple attributes support

Revision 1.3  2001/02/11 15:19:36  a
now supporting multiple urls

Revision 1.2  2001/02/11 13:19:16  a
handling one url per itemset possible

Revision 1.1  2001/02/11 10:48:41  a
added cItemset and cDOM

"""

import xml.dom.minidom



class cDOM:

    """Class for simplifing DOM use in other classes.
    
    This class contains the functions for creating elements to be
    stored in cFile. Other classes inherit this methods.

    Okay, short explanation what's going on here. The basic helper class is
    the element class. An element is a tag, which can contain either text
    or other elements. You can create an element with the CreateElement
    method e.g. el = CreateElement('tagname', {'attribute':'value}, 'text').
    The above code creates

    <tagname attribute="value">text</tagname>

    You can then create another tag that holds the tag e.g.
    els = []
    els.append(el)
    elCont = CreateElementContainer('container', None, els)

    This creates
    <container><tagname attribute="value">text</tagname></container>

    To add this to a DOM, call the method SetRootElement(elCont). Then
    you have a DOM and can print it in xml using the method ToXML().

    """
    def __init__(self):
        """Constructor."""
        self.Document = xml.dom.minidom.Document()


    def SetRootElement(self, rootel):
        """Set root element to document.

        rootel -- root element to be added

        """
        self.Document.appendChild(rootel)


    def GetRootElement(self):
        """Return root element.

        return -- root element

        """
        return self.Document.documentElement


    def ToXML(self):
        """Output xml."""
        return self.Document.toxml()


    def Parse(self, file):
        """Parse XML."""
        self.Document = xml.dom.minidom.parse(file)


    def ParseString(self, string):
        """Parse XML from string."""
        self.Document = xml.dom.minidom.parseString(string)


    def AddElement(self, el):
        """Add entry to document.

        el -- element to be added

        """
        self.Document.documentElement.appendChild(el)


    def DeleteElement(self, sName, sText):
        """Delete resource from document.

        sName -- tag name to be deleted
        sText -- text inside tag name

        XXX should also delete only name or combination with name, attr, text
        XXX doesn't work transparent and correctly
        
        """
        lEls = self.MatchingElements(sName, sText)
        for el in lEls:
            print self.GetText(el)
            self.Document.removeChild(el)


    def MatchingElements(self, sName, sText):
        """Return matching elements in the document.

        sName -- tag name of element
        sText -- text inside tag name

        return -- lEls, list of matching elements

        """
        lEls = []
        # XXX see if this works (was: foo = self.Document...(name):)
        for el in self.Document.getElementsByTagName(sName):
            if (self.GetText(el) == sText):
                lEls.append(el)

        return lEls


    def GetElements(self):
        """Return list of elements despite root element in the document."""
        return self.Document.documentElement.childNodes


    def GetText(self, el):
        """Return text of given elements.

        el -- element

        return -- sText

        """
        sText = ''
        for node in el.childNodes:
            if node.nodeType == xml.dom.minidom.Node.TEXT_NODE:
                sText = sText + node.data

        return sText


    def GetName(self, el):
        """Return name of given elements.

        el -- element

        return -- sName
        
        """
        if el.nodeType == xml.dom.minidom.Node.ELEMENT_NODE:
            return el.nodeName
        else:
            return None


    def GetAttrs(self, el, lAttrs):
        """Return attributes of given element.

        el -- element
        lAttrs -- list of possible attributes

        return -- dAttrs

        """
        if (lAttrs != None):
            dAttrs = {}
            for attr in lAttrs:
                dAttrs[attr] = el.getAttribute(attr)
            return dAttrs
        else:
            return None


    def CreateElement(self, sName, dAttrs, sText):
        """Create element.

        sName -- tag name
        dAttrs -- attributes
        sText -- string inside tag

        return -- created element

        """
        newel = xml.dom.minidom.Document.createElement(sName)
        for key in dAttrs.keys():
            newel.setAttribute(key, dAttrs[key])

        textel = xml.dom.minidom.Document.createTextNode(sText)
        newel.appendChild(textel)

        return newel


    def CreateElementContainer(self, sName, dAttrs, lEls):
        """Create container for elements.

        sName -- tag name
        dAttrs -- attributes
        lEls -- elements inside tag

        return -- created element

        """
        newel = xml.dom.minidom.Document.createElement(sName)
        for key in dAttrs.keys():
            newel.setAttribute(key, dAttrs[key])

        # append els to el
        for el in lEls:
            newel.appendChild(el)

        return newel


    def GetElementsContent(self, lEls, sName, lAttr):
        """Get content of given elements.

        lEls -- elements
        sName -- value of tag to return
        lAttr -- value of attr to return

        return -- dAttr, attr:value pairs for lAttr list
        return -- lContents, contents of childtags with name

        """
        lContents = []
        lAttrs = []
        
        # now here are the elements with given name
        for el in lEls:
            sTagName, dAttr, sContent = self.GetElementContent(el, lAttr)
            if (sTagName == sName):
                lContents.append(sContent)
                lAttrs.append(dAttr)

        return lAttrs, lContents


    def GetElementContent(self, el, lAttr):
        """Get content of given element.

        el -- element
        lAttr -- value of attr to return

        return -- sName, name of tag
        return -- dAttr, attr:value pairs for lAttr list
        return -- lContents, contents of childtags with name

        """
        dAttr = {}
        sContent = ''
        
        # e.g. <tag at="37" foo="bar">text</tag>
        # returns tag, value: dict with at:37, foo:bar
        # and text
        sName = self.GetName(el)
        sContent = self.GetText(el)
        dAttr = self.GetAttrs(el, lAttr)

        return sName, dAttr, sContent


    def GetElementContainerContent(self, contel, sName, lAttr):
        """Return elements inside a given element container.

        contel -- container element
        sName -- tags inside this tag name are returned
        lAttr -- list of attr-values of to return
        
        return -- dAttr, attr:value pairs for lAttr list
        return -- lEls, elements inside container element

        e.g.
        <foo>
        <bar>
        </bar>
        <bar>
        </bar>
        </foo>
        then the bar elements are returned as list

        """
        lEls = []
        dAttr = {}

        # now here are the elements with given name
        if (self.GetName(contel) == sName):
            dAttr = self.GetAttrs(contel, lAttr)
            for el in contel.childNodes:
                lEls.append(el)

        return dAttr, lEls
