<?php
$fname = getloadfilename("текстовый файл (*.txt)");
$content = file($fname);
foreach($content as $row){
    $rc = addarticle($row,"мой текст","2010-12-23","зло, добро, борода");
    print "Добавили статью: $rc";
}
?>
