<?php
/**
 * Удаляет лишние таги, которые не могут быть вложены друг в друга и проверяет их парность.
 * Используется простой и быстрый алгоритм.
 *
 * Пример: "<noindex> ... <noindex> ... </noindex> ... </noindex>" => "<noindex> ...  ...  ... </noindex>"
 *
 * Яндекс и тег noindex.
 *   Робот Яндекса поддерживает тег noindex, который позволяет не индексировать заданные (служебные) участки текста.
 *   В начале служебного фрагмента поставьте — <noindex>, а в конце — </noindex>, и Яндекс не будет индексировать данный участок текста.
 *   Тег noindex чувствителен к вложенности!
 *   http://help.yandex.ru/webmaster/?id=995294
 *
 * @license  http://creativecommons.org/licenses/by-sa/3.0/
 * @author   Nasibullin Rinat, http://orangetie.ru/
 * @charset  ANSI
 * @version  2.1.0
 */
/*string*/ function html_tags_normalize(/*string*/ $s,                     #html код
                                        array      &$invalid_tags = null,  #возвращает массив некорректных парных тагов, если такие есть
                                        array      &$deleted_tags = null,  #возвращает массив удалённых тагов, где ключами явл. таги, а значениями кол-во > 0
                                        #эти парные таги не м.б. вложены друг в друга (XHTML):
                                        array $tags = array('html', 'head', 'body',
                                                            'title', 'h[1-6]',
                                                            'form', 'textarea', 'button', 'option', 'label', 'select',
                                                            'strong', 'em', 'big', 'small', 'sub', 'sup', 'tt',
                                                            '[abius]', 'bdo', 'caption', 'del', 'ins',
                                                            'script', 'noscript', 'style', 'map', 'applet', 'object',
                                                            'nobr', 'noindex', 'nofollow', 'notypo', 'comment',
                                                            )
                                       )
{
    static $_opened_tags  = array();
    static $_deleted_tags = array();

    if (is_array($s) && $invalid_tags === null)  #callback?
    {
        $tag = strtolower($s[2]);
        if (! array_key_exists($tag, $_opened_tags)) $_opened_tags[$tag] = 0;
        $o =& $_opened_tags[$tag];
        if ($s[1] !== '/')
        {
            #tag was opened
            $o++;
            if ($o > 1)
            {
                if (! array_key_exists($tag, $_deleted_tags)) $_deleted_tags[$tag] = 0;
                $_deleted_tags[$tag]++;
                return '';
            }
        }
        else
        {
            #tag was closed
            $o--;
            if ($o > 0)
            {
                if (! array_key_exists($tag, $_deleted_tags)) $_deleted_tags[$tag] = 0;
                $_deleted_tags[$tag]++;
                return '';
            }
        }
        return $s[0];
    }

    #в библиотеке PCRE для PHP \s - это любой пробельный символ, а именно класс символов [\x09\x0a\x0c\x0d\x20\xa0] или, по другому, [\t\n\f\r \xa0]
    #если \s используется с модификатором /u, то \s трактуется как [\x09\x0a\x0c\x0d\x20]
    #regular expression for tag attributes
    #correct processes dirty and broken HTML in a singlebyte or multibyte UTF-8 charset!
    $re_attrs_fast_safe = '(?![a-zA-Z\d])  #statement, which follows after a tag
                           #correct attributes
                           (?>
                               [^>"\']++
                             | (?<=[=\x00-\x20\x7f]|\xc2\xa0) "[^"]*+"
                             | (?<=[=\x00-\x20\x7f]|\xc2\xa0) \'[^\']*+\'
                           )*
                           #incorrect attributes
                           [^>]*+';

    $re_tags = implode('|', $tags);
    $s = preg_replace_callback('~<(/)?+                    #1
                                  ((?i:' . $re_tags . '))  #2
                                  (?(1)|' . $re_attrs_fast_safe . '(?<!/))
                                 >
                                ~sxSX', __FUNCTION__, $s);
    $invalid_tags = array();
    foreach ($_opened_tags as $tag => $count) if ($count !== 0) $invalid_tags[] = $tag;
    $deleted_tags = $_deleted_tags;

    #restore static values
    $_opened_tags  = array();
    $_deleted_tags = array();

    return $s;
}
?>
