<?php
require_once 'strip_tags_smart.php';
require_once 'html_paragraph.php';

print("Обрабатываем <b>$title</b>");
$text = html_paragraph(strip_tags_smart ($text));

?>
