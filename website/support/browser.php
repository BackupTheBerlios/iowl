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
    - <a href="installation.php">Installation instructions </a><br>
    - Browser Configuration</h3>
<table border="0">
  <tr><td><a href="#net4">Netscape Navigator 4.x</a></td></tr>
  <tr><td><a href="#net6">Netscape Navigator 6.x</a></td></tr>
  <tr><td><a href="#ie4">Internet Explorer 4.x</a></td></tr>
  <tr><td><a href="#ie5">Internet Explorer 5.x</a></td></tr>
  <tr><td><a href="#lynx">Lynx</a></td></tr>
</table>

<p><a name="net4"></a></p>
<p><b>For Netscape Navigator 4.x</b>
<ol>
  <li>Go to the menu <b>Edit</b> &gt; <b>Preferences</b> &gt; <b>Advanced</b>
      &gt; <b>Proxies</b>. </li>
  <li>Choose <b>manual proxy</b> configuration.</li>
  <li>Click on the <b>&quot;View&quot;</b> button .</li>
  <li>For the <b>HTTP proxy address</b> insert &quot;<b>localhost</b>&quot;
      and &quot;<b>3228</b>&quot; for the <b>port</b>. Leave the other lines empty.</li>
  <li>Click <b>OK</b> button.</li>
  <li>Click <b>OK</b> button.</li>
</ol>

<p><a name="net6"></a></p>
<p><b>For Netscape Navigator 6.x</b></p>
<ol>
  <li>Go to the menu <b>Edit</b> &gt; <b>Preferences</b> &gt; <b>Advanced</b>
      &gt; <b>Proxies</b>. </li>
  <li>Choose <b>manual proxy</b> configuration.</li>
  <li>For the <b>&quot;HTTP Proxy:&quot;</b> insert &quot;<b>localhost</b>&quot; and<br>
      for the <b>&quot;Port:&quot; </b>&quot;<b>3228</b>&quot;. Leave the other lines empty.</li>
  <li>Click <b>OK</b> button.</li>
</ol>

<p><a name="ie4"></a></p>
<p><b>For Internet Explorer 4.x</b>
<ol>
  <li>Go to the menu <b>View</b> &gt; <b>Internet Options</b> &gt;
      <b>Connection</b>.
  <li>Select check box "<b>Access Internet using a proxy server</b>".
  <li>For "<b>Address</b>" enter "<b>localhost</b>".
  <li>For "<b>Port</b>" enter "<b>3228</b>".
  <li>Click <b>OK</b> button.</li>
</ol>

<p><a name="ie5"></a></p>
<p><b>For Internet Explorer 5.x</b></p>
<ol>
  <li>Go to the menu <b>Tools</b> &gt; <b>Internet Options</b> &gt; <b>Connection</b>.
  <li>Select check box "<b>Access Internet using a proxy server</b>".
  <li>Select either <b>dial-up connection or LAN</b><br>
      (depending on how you connect to the Internet) and click &quot;<b>Settings</b>&quot;
  <li>Check the <b>Use Proxy Server</b> box.
  <li>For "<b>Address</b>" enter "<b>localhost</b>".
  <li>For "<b>Port</b>" enter "<b>3228</b>".
  <li>Press <b>OK</b> button.</li>
</ol>

<p><a name="lynx"></a></p>
<p><b>For Lynx (running on Linux)</b></p>
<ol>
  <li>You have to specify an environment variable before starting
      lynx with:<font face="Courier New, Courier, mono"><br>
      &quot;<font face="Courier New, Courier, mono">setenv
      http_proxy http://localhost:3228/&quot;
</ol>
<?php
include '/home/groups/iowl/htdocs/footer.html';
?>