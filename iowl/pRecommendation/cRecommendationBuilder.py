
__version__ = "$Revision: 1.1 $"

"""
$Log: cRecommendationBuilder.py,v $
Revision 1.1  2001/03/24 19:22:51  i10614
Initial revision

Revision 1.2  2001/02/21 18:30:05  a
basic functions work

Revision 1.1  2001/02/21 16:03:50  a
minor changes


"""

import cClick
import urlparse


class cRecommendationBuilder:

    """Recommendation builder class.
    
    In this class recommendations are built. Incoming is 

    """

    def BuildRecommendation(self, lRules):
        """Build recommendations from list of returned rules.

        Rank etc. in this method.

        """
        lClicks = []

        for rule in lRules:
            click = cClick.cClick()
            tUrl = rule.GetConsequent()
            # we don't want double hits
            hasit = 0
            for c in lClicks:
                if c.HasUrl(tUrl):
                    hasit = 1
            if hasit == 0:
                click.SetClick(tUrl, 'text/html', '200', '4625', \
                           urlparse.urlunparse(tUrl), '')
                lClicks.append(click)

        # recommendation, list of clicks
        return lClicks




