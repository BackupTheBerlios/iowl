<?php
include '/home/groups/iowl/htdocs/header.html';
?>
<h1>Support</h1>
<h2>
  <a href="faq.php">FAQ</a>
  - <a href="usermanual.php">User Manual</a>
  - <a href="email.php">eMail</a>
</h2>
<h3>- <a href="howto.php">Howto</a><br>
    - Installation instructions</h3>
    <table width="100%" border="0">
    <tr>
      <td><a href="#windows">Windows</a></td>
    </tr>
    <tr>
      <td><a href="#linux">Linux</a></td>
    </tr>
   </table>
<h3>- <a href="browser.php">Browser Configuration</a></h3>

<p><a name="windows"></a></p>
<b>Windows 2000, 9x, ME, NT 4.0, XP</b>
<ol>
  <li>Double click on the downloaded file (iowl-[version].exe) to
      start the installation (You'll find the current version at <a href="http://www.iowl.net/download/">http://www.iowl.net/download/</a>)</li>
  <li>The installer program will start </li>
  <li>Select an installation folder where the software will be installed
      or leave the standard one -&gt; click &quot;Next&quot;</li>
  <li>Enter a folder where the iOwl.net shortcuts being stored or
      use the standard (iOwl.net) -&gt; click &quot;Next&quot;</li>
  <li>Choose beetwen the options given you -&gt; click &quot;Next&quot;</li>
  <li>Click &quot;Install&quot; to install iOwl.net</li>
  <li>Leave the &quot;Launch iOwl.net after Setup&quot; checkbox
      checked and finish the installation by pressing the "Finish" button</li>
</ol>

<p><a name="linux"></a></p>
<p><b>Linux</b></p>
<ol>
	<li>Download current cvs-snapshot <a href="http://www.iowl.net/files/daily/current-iowl.tar.gz">current-iowl.tar.gz</a> 
      and extract -&gt; <span class="kursiv">tar -xzvf current-iowl.tar.gz</span></li>
	<li>Change to iowl directory -&gt; <span class="kursiv">cd iowl</span></li>
	<li>Check if necessary software is installed -&gt; See <a href="http://www.iowl.net/wiki/index.php/Distributionen">tested distributions</a>. Cvs-snapshot contains an installation-guide for debian woody and suse7.3.</li> 
	<li>Start iOwl.net -&gt; <span class="kursiv">./iowl.sh start</span></li>
	<li>Test if iOwl.net runs -&gt; <span class="kursiv">telnet localhost 3228</span></li>
<p>&nbsp;</p>

<?php
include '/home/groups/iowl/htdocs/footer.html';
?>