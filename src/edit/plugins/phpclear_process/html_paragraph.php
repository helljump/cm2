<?php

/**
 * ��������� ����� �� ���������, ��������� ��� ����� html ���� (<p></p>, <br />).
 * ���, ������� �������, ��������� ����� �� text/plain � text/html.
 * "������� ������" (������ � ������ ������) ��������������, ����������� ������� ����������.
 * ����� ������������ ��� ��������� ����:
 *   * ����� ��� �������� html ��� ����������
 *   * ����� �� �������� ��������� �����
 *
 * @param    string   $s           �����
 * @param    bool     $is_single   ��������� ������ ����������� ��������� ����������?
 * @return   string
 * @see      nl2br()
 *
 * @author   Nasibullin Rinat <n a s i b u l l i n  at starlink ru>
 * @charset  ANSI
 * @version  1.0.17
 */
function html_paragraph($s, $is_single = false)
{
    #���������� ��������� ��� ��������� �����
    #��������� ������������ ������� � ����� HTML � ������������ ��� UTF-8 ���������!
    static $re_attrs_fast_safe =  '(?> (?>[\x20\r\n\t]+|\xc2\xa0)+  #���������� ������� (�.�. �����������)
                                       (?>
                                         #���������� ��������
                                                                        [^>"\']+
                                         | (?<=[\=\x20\r\n\t]|\xc2\xa0) "[^"]*"
                                         | (?<=[\=\x20\r\n\t]|\xc2\xa0) \'[^\']*\'
                                         #�������� ��������
                                         |                              [^>]+
                                       )*
                                   )?';

    #���������� ������� �������� �� ���������
    $is_para = preg_match('/<(?i:p|br|t[dh]|li|h[1-6]|div|form|title)' . $re_attrs_fast_safe . '>/sx', $s);
    if (! $is_para)
    {
        #���. ��������� ��� �������� ������ text/plain �� ���������
        #"������� ������" (������ � ������ ������) ��������������!
        $p = preg_split('/[\x20\t]*(\r\n|[\r\n])(?>[\x20\t]|\\1)+/', trim($s), -1, PREG_SPLIT_NO_EMPTY);
        $p = preg_replace('/[\r\n]+/', "<br />\r\n", $p);
        if (count($p) > intval(! (bool)$is_single)) $s = '<p>' . implode("</p>\r\n\r\n<p>", $p) . '</p>';
        else $s = implode('', $p);
        $s = preg_replace('/\x20\x20+/s', ' ', $s);  #�������� ������ �������
    }
    return $s;
}

?>
