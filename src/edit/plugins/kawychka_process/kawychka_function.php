<?php
function kavych ($s) {
  $s = preg_replace(
    array(
      "/(^|\s+|\(|\<|\{\[\|)\"/ms",
      "/\"(\s+|\.|\,|\!|\?|\)|\>|\}|\]|\||$)/ms",
    ),
    array(
      "\\1&laquo;",
      "&raquo;\\1",
    ),
    $s
  );
  return $s;
}
?>