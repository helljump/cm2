<?php
$fname = getloadfilename("текстовый файл UTF кодировка(*.txt)");
$content = file($fname);

for($kolichestwo_statey=0; $kolichestwo_statey<100; $kolichestwo_statey++){
$mycontent=$content[0];
print ($mycontent);
preg_match_all('#\[(.*)\]#Ui',$mycontent,$matches);

    for($i=0; $i<sizeof($matches[1]); $i++){

        $ns=explode("|",$matches[1][$i]);
        $c2=sizeof($ns);
        $rand=rand(0,($c2-1));
        $mycontent=str_replace("[".$matches[1][$i]."]",$ns[$rand],$mycontent);

    }

    $rc = addarticle('Статья-'.$kolichestwo_statey,$mycontent,"2010-10-5","нет,да,прочие теги");
    print "Добавили статью: $rc";
}
?>
