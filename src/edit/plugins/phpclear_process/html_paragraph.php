<?php

/**
 * Разбивает текст на параграфы, используя для этого html таги (<p></p>, <br />).
 * Или, другими словами, переводит текст из text/plain в text/html.
 * "Красная строка" (отступ в начале абзаца) поддерживается, дублирующие пробелы вырезаются.
 * Текст возвращается без изменений если:
 *   * текст уже содержит html код параграфов
 *   * текст не содержит переносов строк
 *
 * @param    string   $s           текст
 * @param    bool     $is_single   обрамлять тагами единственно найденный парагаграф?
 * @return   string
 * @see      nl2br()
 *
 * @author   Nasibullin Rinat <n a s i b u l l i n  at starlink ru>
 * @charset  ANSI
 * @version  1.0.17
 */
function html_paragraph($s, $is_single = false)
{
    #регулярное выражение для атрибутов тагов
    #корректно обрабатывает грязный и битый HTML в однобайтовой или UTF-8 кодировке!
    static $re_attrs_fast_safe =  '(?> (?>[\x20\r\n\t]+|\xc2\xa0)+  #пробельные символы (д.б. обязательно)
                                       (?>
                                         #правильные атрибуты
                                                                        [^>"\']+
                                         | (?<=[\=\x20\r\n\t]|\xc2\xa0) "[^"]*"
                                         | (?<=[\=\x20\r\n\t]|\xc2\xa0) \'[^\']*\'
                                         #разбитые атрибуты
                                         |                              [^>]+
                                       )*
                                   )?';

    #определяем наличие разбивки на параграфы
    $is_para = preg_match('/<(?i:p|br|t[dh]|li|h[1-6]|div|form|title)' . $re_attrs_fast_safe . '>/sx', $s);
    if (! $is_para)
    {
        #рег. выражение для разбивки текста text/plain на параграфы
        #"красная строка" (отступ в начале абзаца) поддерживается!
        $p = preg_split('/[\x20\t]*(\r\n|[\r\n])(?>[\x20\t]|\\1)+/', trim($s), -1, PREG_SPLIT_NO_EMPTY);
        $p = preg_replace('/[\r\n]+/', "<br />\r\n", $p);
        if (count($p) > intval(! (bool)$is_single)) $s = '<p>' . implode("</p>\r\n\r\n<p>", $p) . '</p>';
        else $s = implode('', $p);
        $s = preg_replace('/\x20\x20+/s', ' ', $s);  #вырезаем лишние пробелы
    }
    return $s;
}

?>
