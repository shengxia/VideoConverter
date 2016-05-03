<?php
$myfile = fopen("newfile.txt", "w") or die("Unable to open file!");
$txt = $_POST['md5'];
fwrite($myfile, $txt);
fclose($myfile);
?>
