<?php
include '/home/groups/iowl/htdocs/header.html';
?>
<h1>Support</h1>
<h2>
  <a href="faq.php">FAQ</a>
  - <a href="usermanual.php">User Manual</a>
  - <a href="email.php">eMail</a>
</h2>
<h3>- <a href="faq_gen.php">General</a><br>
    - <a href="faq_ins.php">Installation</a><br>
    - <a href="faq_con.php">Configuration</a><br>
    - <a href="faq_usa.php">Usage</a><br>
    - <a href="faq_rec.php">Recommendations</a><br>
    - <a href="faq_his.php">History</a><br>
    - <a href="faq_sec.php">Security</a></h3>
<table border="0">
  <tr><td><a href="#exchanged">What data is exchanged with other owls?</a></td></tr>
  <tr><td><a href="#grab">Can anyone grab my whole profile?</a></td></tr>
  <tr><td><a href="#trace">Can anyone trace my answer?</a></td></tr>
</table>
<h3>- <a href="faq_pla.php">Planned features</a></h3>

<p><a name="exchanged"></a></p>
<table width="95%" border="1">
<tr><td valign="top" width="8%">Q:</td>
    <td valign="top"><b>What data is exchanged with other owls?</b></td></tr>
<tr><td valign="top">A:</td>
    <td valign="top">Data exchanged with other owls is the request data (containing
                     of the URL's you would like to have a recommendation for).<br>
                     Furthermore the recommendations your owl gives other owls
                     will be transmitted. Elements which are removed from the
                     history wouldn't be suggested and/or transmitted.</td></tr>
</table>

<p><a name="grab"></a></p>
<table width="95%" border="1">
<tr><td valign="top" width="8%">Q:</td>
    <td valign="top"><b>Can anyone grab my whole profile?</b></td></tr>
<tr><td valign="top">A:</td>
    <td valign="top">Your owl transfer only few URL's (depends on the recommendation
                     type) but never your whole history.<br>
                     You are able to remove &quot;user sensitve&quot; information,
                     like your personal homepage, from the history everytime.</td></tr>
</table>

<p><a name="trace"></a></p>
<table width="95%" border="1">
<tr><td valign="top" width="8%">Q:</td>
    <td valign="top"><b>Can anyone trace my answer?</b></td></tr>
<tr><td valign="top">A:</td>
    <td valign="top">Since all communication is passed on from owl2owl you
                     can't tell which the originating owl is. The other way
                     round nobody can trace your request or recommendation.</td></tr>
</table>
<?php
include '/home/groups/iowl/htdocs/footer.html';
?>