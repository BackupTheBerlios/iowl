__version__ = "$Revision: 1.5 $"

"""
$Log: cCommandValidator.py,v $
Revision 1.5  2002/02/13 10:47:34  Saruman
added statistics gui

Revision 1.4  2002/02/10 21:40:54  aharth
added showrules feature, cleaned up ui

Revision 1.3  2001/07/15 14:37:55  i10614
updated configuration GUI

Revision 1.2  2001/07/15 10:15:26  i10614
added commands "showconfig" and "showlog"

Revision 1.1.1.1  2001/03/24 19:22:54  i10614
Initial import to stio1 from my cvs-tree

Revision 1.5  2001/02/22 20:41:49  mbauer
revamped gui :-)

Revision 1.4  2001/02/21 14:51:07  mbauer
added more user-functions

Revision 1.2  2001/02/20 21:15:03  mbauer
initial release



"""

class cCommandValidator:
    """check if commands from proxy are valid"""

    def ValidateQuery(self, dQuery):
        """validate query

        dQuery  -- dictionary containing all parameters for query

        return  -- sCommand -> command to execute
                -- dParams  -> dictionary containing parameter for command

        """

        dParams = {}

        # first look for 'action'
        if 'action' not in dQuery.keys():
            # missing action!
            dParams['message'] = 'no action given!'
            return 'error', dParams

        # now check for correct combination of action and parameter
        if dQuery['action'][0] == 'showhelp':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command showhelp does not accept any parameter!'
                return 'error', dParams
            return 'showhelp', dParams

        if dQuery['action'][0] == 'showhistory':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command showhistory does not accept any parameter!'
                return 'error', dParams
            return 'showhistory', dParams

        if dQuery['action'][0] == 'activate':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command activate does not accept any parameter!'
                return 'error', dParams
            return 'activate', dParams

        if dQuery['action'][0] == 'deactivate':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command deactivate does not accept any parameter!'
                return 'error', dParams
            return 'deactivate', dParams

        if dQuery['action'][0] == 'showabout':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command showabout does not accept any parameter!'
                return 'error', dParams
            return 'showabout', dParams

        if dQuery['action'][0] == 'showconfig':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command showconfig does not accept any parameter!'
                return 'error', dParams
            return 'showconfig', dParams

        if dQuery['action'][0] == 'showrules':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command showrules does not accept any parameter!'
                return 'error', dParams
            return 'showrules', dParams

        if dQuery['action'][0] == 'showlog':
            if not ((len(dQuery.keys()) == 2) and ('inumlines' in dQuery.keys())):
                dParams['message'] = 'command showlog needs one parameter (inumlines)!'
                return 'error', dParams
            dParams['inumlines'] = dQuery['inumlines'][0]
            return 'showlog', dParams

        if dQuery['action'][0] == 'singlerecommendation':
            if not (len(dQuery.keys()) == 2) and ('sUrl' in dQuery.keys()):
                dParams['message'] = 'command singlerecommendation needs one parameter (url)!'
                return 'error', dParams
            # okay, seems to be a valid command
            dParams['sUrl'] = dQuery['sUrl'][0]
            return 'singlerecommendation', dParams

        if dQuery['action'][0] == 'sessionrecommendation':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command sessionrecommendation does not accept any parameter!'
                return 'error', dParams
            return 'sessionrecommendation', dParams

        if dQuery['action'][0] == 'longtermrecommendation':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command longtermrecommendation does not accept any parameter!'
                return 'error', dParams
            return 'longtermrecommendation', dParams

        if dQuery['action'][0] == 'getrecommendations':
            if not (len(dQuery.keys()) == 3) and ('id' in dQuery.keys()) and ('sUrl' in dQuery.keys()):
                dParams['message'] = 'command getrecommendations needs two parameter (id, url)!'
                return 'error', dParams
            # okay, seems to be a valid command
            dParams['id'] = dQuery['id'][0]
            dParams['sUrl'] = dQuery['sUrl'][0]
            return 'getrecommendations', dParams

        if dQuery['action'][0] == 'remove':
            if len(dQuery.keys()) != 2:
                dParams['message'] = 'command remove needs one parameter! (sUrl)'
                return 'error', dParams
            dParams['sUrl'] = dQuery['url']
            return 'remove', dParams

        if dQuery['action'][0] == 'updateconfig':
            if len(dQuery.keys()) != 4:
                dParams['message'] = 'command updateconfig needs 3 parameter! (section, option, value)'
                return 'error', dParams
            dParams['section'] = dQuery['section'][0]
            dParams['option'] = dQuery['option'][0]
            dParams['value'] = dQuery['value'][0]
            return 'updateconfig', dParams

        if dQuery['action'][0] == 'showstats':
            if len(dQuery.keys()) != 1:
                dParams['message'] = 'command showstats does not accept any parameter!'
                return 'error', dParams
            return 'showstats', dParams

        # default
        dParams['message']='unknown command "'+str(dQuery['action'])+'".'
        return 'error', dParams
