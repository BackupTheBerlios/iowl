
__version__ = "$Revision: 1.3 $"

"""
$Log: cAssociationRules.py,v $
Revision 1.3  2001/07/15 10:09:29  i10614
changed supportThreshold to 0.005 to improve rule computation time

Revision 1.2  2001/04/07 17:06:23  i10614
many, many bugfixes for working network communication

Revision 1.1.1.1  2001/03/24 19:22:52  i10614
Initial import to stio1 from my cvs-tree

Revision 1.9  2001/03/17 15:19:35  mbauer
removed lots of debug output

Revision 1.8  2001/02/22 12:18:26  a
minor changes

Revision 1.7  2001/02/21 18:27:32  a
basic asso rules works

Revision 1.6  2001/02/21 16:02:36  a
test rules generation

Revision 1.5  2001/02/21 14:33:08  a
major improvements

Revision 1.4  2001/02/20 20:42:30  a
added pAssocRulesInterface


"""

import cItemsets
import cItemset
import urlparse
import cSession
import pManager
import cRule


class cAssociationRules:

    """Class for computing association rules.
    
    Mostly algorithmic stuff here. For deeper understanding of whats going
    on see the paper:
    Agrawal, Srikant: Fast Algorithms for Mining Association Rules, 1994
    
    """

    def __init__(self):
        """Constructor."""


    def ComputeCandidateOneItemsets(self, lSessions):
        """Computes candidate one itemsets from session

        lSessions -- list of sessions
        return -- candidate one itemsets

        """
        oneitemsets = cItemsets.cItemsets(1)

        for session in lSessions:
            for click in session.GetClicks():
                iset = cItemset.cItemset()
                iset.SetUrls([click.GetUrl(),])
                oneitemsets.AddItemset(iset)

        return oneitemsets


    def CountOccurrence(self, lSessions, itemsets):
        """Count occurence of itemsets in session

        lSessions -- list of sessions
        itemsets -- itemsets to be counted

        """
        for session in lSessions:
            lUrls = session.GetUrls()
            itemsets.CountUrl(lUrls)


    def ComputeRules(self, lSessions, iOverallCount):
        """Compute association rules.

        lSessions -- list of sessions
        iOverallCount -- number of urls in clickstream

        """
        oneItemsets = self.ComputeCandidateOneItemsets(lSessions)
        #print '*************One Itemsets'
        #oneItemsets.Print()
        #print '*************'
        # store large itemsets here
        largeItemsets = []

        self.CountOccurrence(lSessions, oneItemsets)

        # prune itemsets
        # XXX is that a good value??
        # supportThreshold = 1.5 #.005*iOverallCount
        supportThreshold = .005*iOverallCount
        oneItemsets.Prune(supportThreshold)

        # Mike - removed debug output
        #
        # print 'Computed candidate one itemsets and pruned'
        # print '*************Did Count'
        # oneItemsets.Print()
        # print '****************'

        # i itemsets starting with 1-itemsets
        # but python starts counting indexes from 0
        largeItemsets.append(None)
        largeItemsets.append(oneItemsets)

        # loop for generating the large k itemsets
        k = 2

        while 1:
            candidate = self.GenerateCandidates(largeItemsets[k-1])

            if candidate == None:
                break

            self.CountOccurrence(lSessions, candidate)
            # prune itemsets
            candidate.Prune(supportThreshold)

            # Mike - removed debug output
            pManager.manager.DebugStr('pAssociationRules '+ __version__ +': Computed Candidate '+str(k)+'.')
            # candidate.Print()
            # print '**************'

            largeItemsets.append(candidate)

            k = k+1

        # 0th entry is Null, 1st is one itemsets
        # 2nd entry is start
        for large in largeItemsets[2:]:
            # Mike - removed debug output
            # large.Print()
            # print '***'
            # print large.GetSize()
            self.GenerateRules(large)

        # Mike - removed debug output
        # print k
        # print iOverallCount


    def GenerateCandidates(self, itemsets):
        """Generate candidate itemsets.

        This method generates new candidate i itemsets.
        apriori_gen() as seen in the Agrawal paper.

        itemsets -- large i-1 itemset
        return -- candidate i itemsets

        """
        k = itemsets.GetSize() + 1

        candidates = self.Join(itemsets)

        # XXX here the candidates should be pruned
        # however, this step is skipped due to time pressure
        # in implementing
        #for c in candidates:
        #    for s in c.GetSubsets(k-1):
        #        if s not in itemsets:
        #            del candidates[c]

        return candidates


    def GenerateRules(self, largeItemsets):
        """Generate rules.

        gen_rules not really as seen in the Agrawal paper, but similar.

        largeItemsets -- large itemsets

        """
        psi = pManager.manager.GetStatisticsInterface()

        for itemset in largeItemsets.GetList():
            lUrls = itemset.GetUrls()
            for url in lUrls:
                # create new rule
                rule = cRule.cRule()
                # url is consequent
                rule.SetConsequent(url)
                # all other urls in lUrls are antecedents
                lAnts = lUrls[:]
                index = lAnts.index(url)
                del lAnts[index]
                rule.SetAntecedents(lAnts)
                psi.AddRule(rule)



        #print 'Generate Rules'

        #urltuple = urlparse.urlparse('http://www.iowl.net/')
        #urltuple2 = urlparse.urlparse('http://slashdot.org')


        #rule.SetAntecedents([urltuple,])
        #rule.SetConfidence(10)
        #rule.SetSupport(10)


    def Join(self, itemsets):
        """Join itemsets.

        itemsets -- Lk-1 large k-1 itemsets
        return -- Ck candidate k itemsets

        """
        k = itemsets.GetSize() + 1
        candidates = cItemsets.cItemsets(k)

        lJoined = []

        for item_i in itemsets.GetList():
            for item_j in itemsets.GetList():
                list_i = item_i.GetUrls()
                list_j = item_j.GetUrls()
                # use dict to eliminate double occurences
                dict = {}
                for url in list_i:
                    dict[url] = 1
                for url in list_j:
                    dict[url] = 1

                if len(dict) == k:
                    if dict not in lJoined:
                        lJoined.append(dict)

        for dict in lJoined:
            i = cItemset.cItemset()
            for url in dict.keys():
                i.AddUrl(url)

            candidates.AddItemset(i)

        if len(candidates.lData) == 0:
            return None
        else:
            return candidates



####################################################################
## TEST FUNCTIONS ##################################################

import pClickstreamInterface

def test():
    csi = pClickstreamInterface.pClickstreamInterface()
    csi.SetParam('clickstreampathname', '/tmp/data')

    csi.Start()

    a = cAssociationRules()

    lSessions = csi.GetSessions()

    a.ComputeRules(lSessions)


def testJoin():
    iss = cItemsets.cItemsets(3)

    a = cAssociationRules()
    
    u1 = urlparse.urlparse('http://eins')
    u2 = urlparse.urlparse('http://zwei')
    u3 = urlparse.urlparse('http://drei')
    u4 = urlparse.urlparse('http://vier')
    u5 = urlparse.urlparse('http://fuenf')

    i1 = cItemset.cItemset()
    i1.SetUrls([u1,u2,u3])
    i2 = cItemset.cItemset()
    i2.SetUrls([u1,u2,u4])
    i3 = cItemset.cItemset()
    i3.SetUrls([u1,u3,u4])
    i4 = cItemset.cItemset()
    i4.SetUrls([u1,u3,u5])
    i5 = cItemset.cItemset()
    i5.SetUrls([u2,u3,u4])

    iss.AddItemset(i1)
    iss.AddItemset(i2)
    iss.AddItemset(i3)
    iss.AddItemset(i4)
    iss.AddItemset(i5)

    a.Join(iss).Print()


import pManager

if __name__ == '__main__':
    pManager.manager = pManager.cManager('')
    test()
        
