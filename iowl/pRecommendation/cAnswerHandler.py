
__version__ = "$Revision: 1.1 $"

"""
$Log: cAnswerHandler.py,v $
Revision 1.1  2001/03/24 19:22:51  i10614
Initial revision

Revision 1.1  2001/02/19 19:20:04  a
added *Handler classes


"""

import cRequest
import cAnswer


class pAnswerHandler:

    """Handles answers.
    
    This class is responsible for handling answers.
    
    """"
    
    def __init__(self):
        """Constructor."""
        self.Answers = []


    def SetAnswer(self, lEls):
        """Parse answer into internal representation.

        lEls -- list of answer elements

        """
        answer = cAnswer.cAnswer()
        answer.SetElements(lEls)
        self.Answers.append(answer)


    def ComputeRecommendation(self):
        """Compute recommendations from past answers."""
        # here we go
        print ''
