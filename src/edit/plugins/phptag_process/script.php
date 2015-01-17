<?php
require_once 'html_tags_normalize.php';
print("Обрабатываем <b>$title</b>");
$text = html_tags_normalize ($text,$NoDeleteError,$DeleteError);
$NoDelet=count($NoDeleteError);
$Delet=count($DeleteError);
print( "Исправлено:$Delet, неисправлено:$NoDelet ошиб." );
if ($NoDelet != 0)
{
  for ($i=0; $i<$NoDelet; $i++)
  {
    $myNoDeleteError =$NoDeleteError[$i];
    print ("<b>Ошибка $1</b> - $myNoDeleteError");
    }
  }
?>
