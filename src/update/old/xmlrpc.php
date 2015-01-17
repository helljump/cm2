<?php
define("XMLRPC_USERAGENT", "blap");

include("kd_xmlrpc.php"); 

$xmlrpc_methods = array();
$xmlrpc_methods['yasynpro.getNews'] = yasynpro_getNews;
$xmlrpc_methods['treeedit.getUpdate'] = treeedit_getUpdate;
$xmlrpc_methods['method_not_found'] = XMLRPC_method_not_found;

$xmlrpc_request = XMLRPC_parse($GLOBALS['HTTP_RAW_POST_DATA']);
$methodName = XMLRPC_getMethodName($xmlrpc_request);
$params = XMLRPC_getParams($xmlrpc_request);

if(!isset($xmlrpc_methods[$methodName])){
    $xmlrpc_methods['method_not_found']($methodName);
}else{
    $xmlrpc_methods[$methodName]($params[0]);
}

function XMLRPC_method_not_found(){
    //createDB();
    XMLRPC_error("1", "error: method not found"); 
}

function insertClient( $key, $hwinfo ){
    $ip = $_SERVER['REMOTE_ADDR'];
    //$db = sqlite_open("yasynpro.sqlite");
    //sqlite_query($db, "INSERT INTO clients (key, ip, hwinfo, cdate) VALUES ($key,'$ip','$hwinfo',datetime('now'))");
    //sqlite_close($db);    

    $fout = fopen("yasynpro.log","at");
    fwrite($fout,"[".date("Y/m/d H:i:s")."] key:".$key." ip:".$ip." hwinfo:".$hwinfo."\n");
    fclose($fout);

}

function yasynpro_getNews( $params ) {
    
    $key=$params['key'];
    $hwinfo=$params['hwinfo'];
    $fsize=$params['filesize'];
        
    insertClient( $key, $hwinfo);
    
    $newfsize = filesize("yasynpro/news.pak");
    
    if ($fsize!=$newfsize){
        $update_info['present'] = True;
        $update_info['url'] = "http://blap.ru/update/yasynpro/news.pak";
        $update_info['size'] = $newfsize;
    } else {
        $update_info['present'] = False;
    }
    
    XMLRPC_response(XMLRPC_prepare($update_info), XMLRPC_USERAGENT);
} 

function treeedit_getUpdate( $params ) {
    
    $key=$params['username'];
    $date=$params['date'];
    $version=$params['version'];
        
    $fname = get_latest("treeedit", $version);
    if ($fname!=False){
        $update_info['url'] = "http://blap.ru/update/treeedit/$fname";
        $update_info['size'] = filesize("treeedit/$fname");
    } else {
        $update_info['url'] = False;
    }
    
    XMLRPC_response(XMLRPC_prepare($update_info), XMLRPC_USERAGENT);
} 

class VersionFile{
    function VersionFile($ver, $fname){
        $this->ver = $ver;
        $this->fname = $fname;
    }
    function cmp($a, $b) 
    {
        $al = strtolower($a->ver);
        $bl = strtolower($b->ver);
        if ($al == $bl) return 0;
        return ($al > $bl) ? +1 : -1;
    }
}

function get_latest($cat, $ver){
    $versions = array();
    if ($handle = opendir($cat)) {
        while (false !== ($file = readdir($handle))) { 
            if ($file != "." && $file != "..") { 
                if (preg_match("/library-([\w\.]+)\.dat/", $file, $matches))
                    $versions[] = new VersionFile($matches[1], $file);
            } 
        }
        closedir($handle); 
    }
    usort($versions, array("VersionFile", "cmp"));
    $last_elem = array_pop($versions);
    if ($ver!=$last_elem->ver)
        return $last_elem->fname;
    else
        return False;
        
}

?>
