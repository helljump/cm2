-- MySQL dump 10.13  Distrib 5.1.41, for Win32 (ia32)
--
-- Host: localhost    Database: wordpress
-- ------------------------------------------------------
-- Server version	5.1.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `wp_comments`
--

DROP TABLE IF EXISTS `wp_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_comments` (
  `comment_ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `comment_post_ID` bigint(20) unsigned NOT NULL DEFAULT '0',
  `comment_author` tinytext NOT NULL,
  `comment_author_email` varchar(100) NOT NULL DEFAULT '',
  `comment_author_url` varchar(200) NOT NULL DEFAULT '',
  `comment_author_IP` varchar(100) NOT NULL DEFAULT '',
  `comment_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `comment_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `comment_content` text NOT NULL,
  `comment_karma` int(11) NOT NULL DEFAULT '0',
  `comment_approved` varchar(20) NOT NULL DEFAULT '1',
  `comment_agent` varchar(255) NOT NULL DEFAULT '',
  `comment_type` varchar(20) NOT NULL DEFAULT '',
  `comment_parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `user_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`comment_ID`),
  KEY `comment_approved` (`comment_approved`),
  KEY `comment_post_ID` (`comment_post_ID`),
  KEY `comment_approved_date_gmt` (`comment_approved`,`comment_date_gmt`),
  KEY `comment_date_gmt` (`comment_date_gmt`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_comments`
--

LOCK TABLES `wp_comments` WRITE;
/*!40000 ALTER TABLE `wp_comments` DISABLE KEYS */;
INSERT INTO `wp_comments` VALUES (1,1,'Мистер WordPress','','http://wordpress.org/','','2010-06-08 20:04:57','2010-06-08 16:04:57','Привет! Это комментарий. <br />Чтобы его удалить, авторизуйтесь и просмотрите комментарии. Там будут ссылки для удаления или изменения комментариев. <font color=\"red\">Для защиты от спама рекомендуется сразу после первичной настройки установить один или комбинацию плагинов.</font><br /> Например: Akismet, ReCapctha, Math Comment protection, MaxSite.org ant-spam image, Bad Behavior или другие. Все плагины легко найти через форумы и в поисковых системах. Или можно вот так <a href=\"http://wordpress.org/extend/plugins/search.php?q=spam\">поиск антиспам плагинов в официальном каталоге плагинов</a>',0,'1','','',0,0);
/*!40000 ALTER TABLE `wp_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_links`
--

DROP TABLE IF EXISTS `wp_links`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_links` (
  `link_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `link_url` varchar(255) NOT NULL DEFAULT '',
  `link_name` varchar(255) NOT NULL DEFAULT '',
  `link_image` varchar(255) NOT NULL DEFAULT '',
  `link_target` varchar(25) NOT NULL DEFAULT '',
  `link_description` varchar(255) NOT NULL DEFAULT '',
  `link_visible` varchar(20) NOT NULL DEFAULT 'Y',
  `link_owner` bigint(20) unsigned NOT NULL DEFAULT '1',
  `link_rating` int(11) NOT NULL DEFAULT '0',
  `link_updated` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `link_rel` varchar(255) NOT NULL DEFAULT '',
  `link_notes` mediumtext NOT NULL,
  `link_rss` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`link_id`),
  KEY `link_visible` (`link_visible`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_links`
--

LOCK TABLES `wp_links` WRITE;
/*!40000 ALTER TABLE `wp_links` DISABLE KEYS */;
INSERT INTO `wp_links` VALUES (1,'http://codex.wordpress.org/','Documentation','','','','Y',1,0,'0000-00-00 00:00:00','','',''),(2,'http://wordpress.org/development/','Development Blog','','','','Y',1,0,'0000-00-00 00:00:00','','','http://wordpress.org/development/feed/'),(3,'http://wordpress.org/extend/ideas/','Suggest Ideas','','','','Y',1,0,'0000-00-00 00:00:00','','',''),(4,'http://wordpress.org/support/','Support Forum','','','','Y',1,0,'0000-00-00 00:00:00','','',''),(5,'http://wordpress.org/extend/plugins/','Plugins','','','','Y',1,0,'0000-00-00 00:00:00','','',''),(6,'http://wordpress.org/extend/themes/','Themes','','','','Y',1,0,'0000-00-00 00:00:00','','',''),(7,'http://planet.wordpress.org/','WordPress Planet','','','','Y',1,0,'0000-00-00 00:00:00','','','');
/*!40000 ALTER TABLE `wp_links` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_options`
--

DROP TABLE IF EXISTS `wp_options`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_options` (
  `option_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `blog_id` int(11) NOT NULL DEFAULT '0',
  `option_name` varchar(64) NOT NULL DEFAULT '',
  `option_value` longtext NOT NULL,
  `autoload` varchar(20) NOT NULL DEFAULT 'yes',
  PRIMARY KEY (`option_id`,`blog_id`,`option_name`),
  KEY `option_name` (`option_name`)
) ENGINE=MyISAM AUTO_INCREMENT=153 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_options`
--

LOCK TABLES `wp_options` WRITE;
/*!40000 ALTER TABLE `wp_options` DISABLE KEYS */;
INSERT INTO `wp_options` VALUES (1,0,'_transient_random_seed','6bcd4b9e9f5c331ca1b98d64b50f444f','yes'),(2,0,'siteurl','http://wordpress.localhost','yes'),(3,0,'blogname','MyBlog','yes'),(4,0,'blogdescription','Описание вашего блога','yes'),(5,0,'users_can_register','0','yes'),(6,0,'admin_email','helljump@gmail.com','yes'),(7,0,'start_of_week','1','yes'),(8,0,'use_balanceTags','','yes'),(9,0,'use_smilies','1','yes'),(10,0,'require_name_email','1','yes'),(11,0,'comments_notify','1','yes'),(12,0,'posts_per_rss','10','yes'),(13,0,'rss_excerpt_length','50','yes'),(14,0,'rss_use_excerpt','0','yes'),(15,0,'mailserver_url','mail.example.com','yes'),(16,0,'mailserver_login','login@example.com','yes'),(17,0,'mailserver_pass','password','yes'),(18,0,'mailserver_port','110','yes'),(19,0,'default_category','1','yes'),(20,0,'default_comment_status','open','yes'),(21,0,'default_ping_status','open','yes'),(22,0,'default_pingback_flag','1','yes'),(23,0,'default_post_edit_rows','10','yes'),(24,0,'posts_per_page','10','yes'),(25,0,'date_format','j F Y','yes'),(26,0,'time_format','G:i','yes'),(27,0,'links_updated_date_format','j F Y G:i','yes'),(28,0,'links_recently_updated_prepend','<em>','yes'),(29,0,'links_recently_updated_append','</em>','yes'),(30,0,'links_recently_updated_time','120','yes'),(31,0,'comment_moderation','0','yes'),(32,0,'moderation_notify','1','yes'),(33,0,'permalink_structure','/%year%/%monthnum%/%postname%/','yes'),(34,0,'gzipcompression','0','yes'),(35,0,'hack_file','0','yes'),(36,0,'blog_charset','UTF-8','yes'),(37,0,'moderation_keys','','no'),(38,0,'active_plugins','a:3:{i:0;s:14:\"rus-to-lat.php\";i:1;s:16:\"russian-date.php\";i:2;s:25:\"total_disable_updates.php\";}','yes'),(39,0,'home','http://wordpress.localhost','yes'),(40,0,'category_base','','yes'),(41,0,'ping_sites','http://rpc.pingomatic.com/','yes'),(42,0,'advanced_edit','0','yes'),(43,0,'comment_max_links','2','yes'),(44,0,'gmt_offset','4','yes'),(45,0,'default_email_category','1','yes'),(46,0,'recently_edited','','no'),(47,0,'use_linksupdate','0','yes'),(48,0,'template','default','yes'),(49,0,'stylesheet','default','yes'),(50,0,'comment_whitelist','1','yes'),(51,0,'blacklist_keys','','no'),(52,0,'comment_registration','0','yes'),(53,0,'rss_language','en','yes'),(54,0,'html_type','text/html','yes'),(55,0,'use_trackback','0','yes'),(56,0,'default_role','subscriber','yes'),(57,0,'db_version','11548','yes'),(58,0,'uploads_use_yearmonth_folders','1','yes'),(59,0,'upload_path','C:\\xampplite\\htdocs\\wordpress/wp-content/uploads','yes'),(60,0,'secret','4Il4rvvZiAP9@j#FmteAnKpD#J*zhhJXKMiLpchv!OUBbVGZzTaT#C4mK4exVtB4','yes'),(61,0,'blog_public','1','yes'),(62,0,'default_link_category','2','yes'),(63,0,'show_on_front','posts','yes'),(64,0,'tag_base','','yes'),(65,0,'show_avatars','1','yes'),(66,0,'avatar_rating','G','yes'),(67,0,'upload_url_path','','yes'),(68,0,'thumbnail_size_w','150','yes'),(69,0,'thumbnail_size_h','150','yes'),(70,0,'thumbnail_crop','1','yes'),(71,0,'medium_size_w','300','yes'),(72,0,'medium_size_h','300','yes'),(73,0,'avatar_default','mystery','yes'),(74,0,'enable_app','','yes'),(75,0,'enable_xmlrpc','1','yes'),(76,0,'large_size_w','1024','yes'),(77,0,'large_size_h','1024','yes'),(78,0,'image_default_link_type','file','yes'),(79,0,'image_default_size','','yes'),(80,0,'image_default_align','','yes'),(81,0,'close_comments_for_old_posts','0','yes'),(82,0,'close_comments_days_old','14','yes'),(83,0,'thread_comments','0','yes'),(84,0,'thread_comments_depth','5','yes'),(85,0,'page_comments','1','yes'),(86,0,'comments_per_page','50','yes'),(87,0,'default_comments_page','newest','yes'),(88,0,'comment_order','asc','yes'),(89,0,'sticky_posts','a:0:{}','yes'),(90,0,'widget_categories','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(91,0,'widget_text','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(92,0,'widget_rss','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(93,0,'timezone_string','','yes'),(94,0,'wp_user_roles','a:5:{s:13:\"administrator\";a:2:{s:4:\"name\";s:13:\"Administrator\";s:12:\"capabilities\";a:54:{s:13:\"switch_themes\";b:1;s:11:\"edit_themes\";b:1;s:16:\"activate_plugins\";b:1;s:12:\"edit_plugins\";b:1;s:10:\"edit_users\";b:1;s:10:\"edit_files\";b:1;s:14:\"manage_options\";b:1;s:17:\"moderate_comments\";b:1;s:17:\"manage_categories\";b:1;s:12:\"manage_links\";b:1;s:12:\"upload_files\";b:1;s:6:\"import\";b:1;s:15:\"unfiltered_html\";b:1;s:10:\"edit_posts\";b:1;s:17:\"edit_others_posts\";b:1;s:20:\"edit_published_posts\";b:1;s:13:\"publish_posts\";b:1;s:10:\"edit_pages\";b:1;s:4:\"read\";b:1;s:8:\"level_10\";b:1;s:7:\"level_9\";b:1;s:7:\"level_8\";b:1;s:7:\"level_7\";b:1;s:7:\"level_6\";b:1;s:7:\"level_5\";b:1;s:7:\"level_4\";b:1;s:7:\"level_3\";b:1;s:7:\"level_2\";b:1;s:7:\"level_1\";b:1;s:7:\"level_0\";b:1;s:17:\"edit_others_pages\";b:1;s:20:\"edit_published_pages\";b:1;s:13:\"publish_pages\";b:1;s:12:\"delete_pages\";b:1;s:19:\"delete_others_pages\";b:1;s:22:\"delete_published_pages\";b:1;s:12:\"delete_posts\";b:1;s:19:\"delete_others_posts\";b:1;s:22:\"delete_published_posts\";b:1;s:20:\"delete_private_posts\";b:1;s:18:\"edit_private_posts\";b:1;s:18:\"read_private_posts\";b:1;s:20:\"delete_private_pages\";b:1;s:18:\"edit_private_pages\";b:1;s:18:\"read_private_pages\";b:1;s:12:\"delete_users\";b:1;s:12:\"create_users\";b:1;s:17:\"unfiltered_upload\";b:1;s:14:\"edit_dashboard\";b:1;s:14:\"update_plugins\";b:1;s:14:\"delete_plugins\";b:1;s:15:\"install_plugins\";b:1;s:13:\"update_themes\";b:1;s:14:\"install_themes\";b:1;}}s:6:\"editor\";a:2:{s:4:\"name\";s:6:\"Editor\";s:12:\"capabilities\";a:34:{s:17:\"moderate_comments\";b:1;s:17:\"manage_categories\";b:1;s:12:\"manage_links\";b:1;s:12:\"upload_files\";b:1;s:15:\"unfiltered_html\";b:1;s:10:\"edit_posts\";b:1;s:17:\"edit_others_posts\";b:1;s:20:\"edit_published_posts\";b:1;s:13:\"publish_posts\";b:1;s:10:\"edit_pages\";b:1;s:4:\"read\";b:1;s:7:\"level_7\";b:1;s:7:\"level_6\";b:1;s:7:\"level_5\";b:1;s:7:\"level_4\";b:1;s:7:\"level_3\";b:1;s:7:\"level_2\";b:1;s:7:\"level_1\";b:1;s:7:\"level_0\";b:1;s:17:\"edit_others_pages\";b:1;s:20:\"edit_published_pages\";b:1;s:13:\"publish_pages\";b:1;s:12:\"delete_pages\";b:1;s:19:\"delete_others_pages\";b:1;s:22:\"delete_published_pages\";b:1;s:12:\"delete_posts\";b:1;s:19:\"delete_others_posts\";b:1;s:22:\"delete_published_posts\";b:1;s:20:\"delete_private_posts\";b:1;s:18:\"edit_private_posts\";b:1;s:18:\"read_private_posts\";b:1;s:20:\"delete_private_pages\";b:1;s:18:\"edit_private_pages\";b:1;s:18:\"read_private_pages\";b:1;}}s:6:\"author\";a:2:{s:4:\"name\";s:6:\"Author\";s:12:\"capabilities\";a:10:{s:12:\"upload_files\";b:1;s:10:\"edit_posts\";b:1;s:20:\"edit_published_posts\";b:1;s:13:\"publish_posts\";b:1;s:4:\"read\";b:1;s:7:\"level_2\";b:1;s:7:\"level_1\";b:1;s:7:\"level_0\";b:1;s:12:\"delete_posts\";b:1;s:22:\"delete_published_posts\";b:1;}}s:11:\"contributor\";a:2:{s:4:\"name\";s:11:\"Contributor\";s:12:\"capabilities\";a:5:{s:10:\"edit_posts\";b:1;s:4:\"read\";b:1;s:7:\"level_1\";b:1;s:7:\"level_0\";b:1;s:12:\"delete_posts\";b:1;}}s:10:\"subscriber\";a:2:{s:4:\"name\";s:10:\"Subscriber\";s:12:\"capabilities\";a:2:{s:4:\"read\";b:1;s:7:\"level_0\";b:1;}}}','yes'),(144,0,'_transient_rewrite_rules','a:70:{s:12:\"robots\\.txt$\";s:18:\"index.php?robots=1\";s:14:\".*wp-atom.php$\";s:19:\"index.php?feed=atom\";s:13:\".*wp-rdf.php$\";s:18:\"index.php?feed=rdf\";s:13:\".*wp-rss.php$\";s:18:\"index.php?feed=rss\";s:14:\".*wp-rss2.php$\";s:19:\"index.php?feed=rss2\";s:14:\".*wp-feed.php$\";s:19:\"index.php?feed=feed\";s:22:\".*wp-commentsrss2.php$\";s:34:\"index.php?feed=rss2&withcomments=1\";s:32:\"feed/(feed|rdf|rss|rss2|atom)/?$\";s:27:\"index.php?&feed=$matches[1]\";s:27:\"(feed|rdf|rss|rss2|atom)/?$\";s:27:\"index.php?&feed=$matches[1]\";s:20:\"page/?([0-9]{1,})/?$\";s:28:\"index.php?&paged=$matches[1]\";s:41:\"comments/feed/(feed|rdf|rss|rss2|atom)/?$\";s:42:\"index.php?&feed=$matches[1]&withcomments=1\";s:36:\"comments/(feed|rdf|rss|rss2|atom)/?$\";s:42:\"index.php?&feed=$matches[1]&withcomments=1\";s:29:\"comments/page/?([0-9]{1,})/?$\";s:28:\"index.php?&paged=$matches[1]\";s:44:\"search/(.+)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:40:\"index.php?s=$matches[1]&feed=$matches[2]\";s:39:\"search/(.+)/(feed|rdf|rss|rss2|atom)/?$\";s:40:\"index.php?s=$matches[1]&feed=$matches[2]\";s:32:\"search/(.+)/page/?([0-9]{1,})/?$\";s:41:\"index.php?s=$matches[1]&paged=$matches[2]\";s:14:\"search/(.+)/?$\";s:23:\"index.php?s=$matches[1]\";s:47:\"category/(.+?)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:52:\"index.php?category_name=$matches[1]&feed=$matches[2]\";s:42:\"category/(.+?)/(feed|rdf|rss|rss2|atom)/?$\";s:52:\"index.php?category_name=$matches[1]&feed=$matches[2]\";s:35:\"category/(.+?)/page/?([0-9]{1,})/?$\";s:53:\"index.php?category_name=$matches[1]&paged=$matches[2]\";s:17:\"category/(.+?)/?$\";s:35:\"index.php?category_name=$matches[1]\";s:42:\"tag/(.+?)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:42:\"index.php?tag=$matches[1]&feed=$matches[2]\";s:37:\"tag/(.+?)/(feed|rdf|rss|rss2|atom)/?$\";s:42:\"index.php?tag=$matches[1]&feed=$matches[2]\";s:30:\"tag/(.+?)/page/?([0-9]{1,})/?$\";s:43:\"index.php?tag=$matches[1]&paged=$matches[2]\";s:12:\"tag/(.+?)/?$\";s:25:\"index.php?tag=$matches[1]\";s:47:\"author/([^/]+)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:50:\"index.php?author_name=$matches[1]&feed=$matches[2]\";s:42:\"author/([^/]+)/(feed|rdf|rss|rss2|atom)/?$\";s:50:\"index.php?author_name=$matches[1]&feed=$matches[2]\";s:35:\"author/([^/]+)/page/?([0-9]{1,})/?$\";s:51:\"index.php?author_name=$matches[1]&paged=$matches[2]\";s:17:\"author/([^/]+)/?$\";s:33:\"index.php?author_name=$matches[1]\";s:69:\"([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})/feed/(feed|rdf|rss|rss2|atom)/?$\";s:80:\"index.php?year=$matches[1]&monthnum=$matches[2]&day=$matches[3]&feed=$matches[4]\";s:64:\"([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})/(feed|rdf|rss|rss2|atom)/?$\";s:80:\"index.php?year=$matches[1]&monthnum=$matches[2]&day=$matches[3]&feed=$matches[4]\";s:57:\"([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})/page/?([0-9]{1,})/?$\";s:81:\"index.php?year=$matches[1]&monthnum=$matches[2]&day=$matches[3]&paged=$matches[4]\";s:39:\"([0-9]{4})/([0-9]{1,2})/([0-9]{1,2})/?$\";s:63:\"index.php?year=$matches[1]&monthnum=$matches[2]&day=$matches[3]\";s:56:\"([0-9]{4})/([0-9]{1,2})/feed/(feed|rdf|rss|rss2|atom)/?$\";s:64:\"index.php?year=$matches[1]&monthnum=$matches[2]&feed=$matches[3]\";s:51:\"([0-9]{4})/([0-9]{1,2})/(feed|rdf|rss|rss2|atom)/?$\";s:64:\"index.php?year=$matches[1]&monthnum=$matches[2]&feed=$matches[3]\";s:44:\"([0-9]{4})/([0-9]{1,2})/page/?([0-9]{1,})/?$\";s:65:\"index.php?year=$matches[1]&monthnum=$matches[2]&paged=$matches[3]\";s:26:\"([0-9]{4})/([0-9]{1,2})/?$\";s:47:\"index.php?year=$matches[1]&monthnum=$matches[2]\";s:43:\"([0-9]{4})/feed/(feed|rdf|rss|rss2|atom)/?$\";s:43:\"index.php?year=$matches[1]&feed=$matches[2]\";s:38:\"([0-9]{4})/(feed|rdf|rss|rss2|atom)/?$\";s:43:\"index.php?year=$matches[1]&feed=$matches[2]\";s:31:\"([0-9]{4})/page/?([0-9]{1,})/?$\";s:44:\"index.php?year=$matches[1]&paged=$matches[2]\";s:13:\"([0-9]{4})/?$\";s:26:\"index.php?year=$matches[1]\";s:47:\"[0-9]{4}/[0-9]{1,2}/[^/]+/attachment/([^/]+)/?$\";s:32:\"index.php?attachment=$matches[1]\";s:57:\"[0-9]{4}/[0-9]{1,2}/[^/]+/attachment/([^/]+)/trackback/?$\";s:37:\"index.php?attachment=$matches[1]&tb=1\";s:77:\"[0-9]{4}/[0-9]{1,2}/[^/]+/attachment/([^/]+)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:49:\"index.php?attachment=$matches[1]&feed=$matches[2]\";s:72:\"[0-9]{4}/[0-9]{1,2}/[^/]+/attachment/([^/]+)/(feed|rdf|rss|rss2|atom)/?$\";s:49:\"index.php?attachment=$matches[1]&feed=$matches[2]\";s:72:\"[0-9]{4}/[0-9]{1,2}/[^/]+/attachment/([^/]+)/comment-page-([0-9]{1,})/?$\";s:50:\"index.php?attachment=$matches[1]&cpage=$matches[2]\";s:44:\"([0-9]{4})/([0-9]{1,2})/([^/]+)/trackback/?$\";s:69:\"index.php?year=$matches[1]&monthnum=$matches[2]&name=$matches[3]&tb=1\";s:64:\"([0-9]{4})/([0-9]{1,2})/([^/]+)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:81:\"index.php?year=$matches[1]&monthnum=$matches[2]&name=$matches[3]&feed=$matches[4]\";s:59:\"([0-9]{4})/([0-9]{1,2})/([^/]+)/(feed|rdf|rss|rss2|atom)/?$\";s:81:\"index.php?year=$matches[1]&monthnum=$matches[2]&name=$matches[3]&feed=$matches[4]\";s:52:\"([0-9]{4})/([0-9]{1,2})/([^/]+)/page/?([0-9]{1,})/?$\";s:82:\"index.php?year=$matches[1]&monthnum=$matches[2]&name=$matches[3]&paged=$matches[4]\";s:59:\"([0-9]{4})/([0-9]{1,2})/([^/]+)/comment-page-([0-9]{1,})/?$\";s:82:\"index.php?year=$matches[1]&monthnum=$matches[2]&name=$matches[3]&cpage=$matches[4]\";s:44:\"([0-9]{4})/([0-9]{1,2})/([^/]+)(/[0-9]+)?/?$\";s:81:\"index.php?year=$matches[1]&monthnum=$matches[2]&name=$matches[3]&page=$matches[4]\";s:36:\"[0-9]{4}/[0-9]{1,2}/[^/]+/([^/]+)/?$\";s:32:\"index.php?attachment=$matches[1]\";s:46:\"[0-9]{4}/[0-9]{1,2}/[^/]+/([^/]+)/trackback/?$\";s:37:\"index.php?attachment=$matches[1]&tb=1\";s:66:\"[0-9]{4}/[0-9]{1,2}/[^/]+/([^/]+)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:49:\"index.php?attachment=$matches[1]&feed=$matches[2]\";s:61:\"[0-9]{4}/[0-9]{1,2}/[^/]+/([^/]+)/(feed|rdf|rss|rss2|atom)/?$\";s:49:\"index.php?attachment=$matches[1]&feed=$matches[2]\";s:61:\"[0-9]{4}/[0-9]{1,2}/[^/]+/([^/]+)/comment-page-([0-9]{1,})/?$\";s:50:\"index.php?attachment=$matches[1]&cpage=$matches[2]\";s:51:\"([0-9]{4})/([0-9]{1,2})/comment-page-([0-9]{1,})/?$\";s:65:\"index.php?year=$matches[1]&monthnum=$matches[2]&cpage=$matches[3]\";s:38:\"([0-9]{4})/comment-page-([0-9]{1,})/?$\";s:44:\"index.php?year=$matches[1]&cpage=$matches[2]\";s:25:\".+?/attachment/([^/]+)/?$\";s:32:\"index.php?attachment=$matches[1]\";s:35:\".+?/attachment/([^/]+)/trackback/?$\";s:37:\"index.php?attachment=$matches[1]&tb=1\";s:55:\".+?/attachment/([^/]+)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:49:\"index.php?attachment=$matches[1]&feed=$matches[2]\";s:50:\".+?/attachment/([^/]+)/(feed|rdf|rss|rss2|atom)/?$\";s:49:\"index.php?attachment=$matches[1]&feed=$matches[2]\";s:50:\".+?/attachment/([^/]+)/comment-page-([0-9]{1,})/?$\";s:50:\"index.php?attachment=$matches[1]&cpage=$matches[2]\";s:18:\"(.+?)/trackback/?$\";s:35:\"index.php?pagename=$matches[1]&tb=1\";s:38:\"(.+?)/feed/(feed|rdf|rss|rss2|atom)/?$\";s:47:\"index.php?pagename=$matches[1]&feed=$matches[2]\";s:33:\"(.+?)/(feed|rdf|rss|rss2|atom)/?$\";s:47:\"index.php?pagename=$matches[1]&feed=$matches[2]\";s:26:\"(.+?)/page/?([0-9]{1,})/?$\";s:48:\"index.php?pagename=$matches[1]&paged=$matches[2]\";s:33:\"(.+?)/comment-page-([0-9]{1,})/?$\";s:48:\"index.php?pagename=$matches[1]&cpage=$matches[2]\";s:18:\"(.+?)(/[0-9]+)?/?$\";s:47:\"index.php?pagename=$matches[1]&page=$matches[2]\";}','yes'),(96,0,'cron','a:2:{i:1277568309;a:3:{s:16:\"wp_version_check\";a:1:{s:32:\"40cd750bba9870f18aada2478b24840a\";a:3:{s:8:\"schedule\";s:10:\"twicedaily\";s:4:\"args\";a:0:{}s:8:\"interval\";i:43200;}}s:17:\"wp_update_plugins\";a:1:{s:32:\"40cd750bba9870f18aada2478b24840a\";a:3:{s:8:\"schedule\";s:10:\"twicedaily\";s:4:\"args\";a:0:{}s:8:\"interval\";i:43200;}}s:16:\"wp_update_themes\";a:1:{s:32:\"40cd750bba9870f18aada2478b24840a\";a:3:{s:8:\"schedule\";s:10:\"twicedaily\";s:4:\"args\";a:0:{}s:8:\"interval\";i:43200;}}}s:7:\"version\";i:2;}','yes'),(97,0,'_transient_doing_cron','1277539763','yes'),(98,0,'logged_in_salt','GT4UCyq0(A$BNX^3@y(dW8rteUCm^nZzIA0%P#AswwbC81q5pW*^9nAlQmmtY@Aj','yes'),(99,0,'_transient_update_core','O:8:\"stdClass\":3:{s:7:\"updates\";a:2:{i:0;O:8:\"stdClass\":5:{s:8:\"response\";s:7:\"upgrade\";s:3:\"url\";s:28:\"http://lecactus.ru/download/\";s:7:\"package\";s:53:\"http://lecactus.ru/download/wordpress-2.9.2-ru_RU.zip\";s:7:\"current\";s:5:\"2.9.2\";s:6:\"locale\";s:5:\"ru_RU\";}i:1;O:8:\"stdClass\":5:{s:8:\"response\";s:7:\"upgrade\";s:3:\"url\";s:30:\"http://wordpress.org/download/\";s:7:\"package\";s:40:\"http://wordpress.org/wordpress-2.9.2.zip\";s:7:\"current\";s:5:\"2.9.2\";s:6:\"locale\";s:5:\"en_US\";}}s:12:\"last_checked\";i:1276013113;s:15:\"version_checked\";s:5:\"2.8.6\";}','yes'),(100,0,'_transient_update_plugins','O:8:\"stdClass\":3:{s:12:\"last_checked\";i:1276013181;s:7:\"checked\";a:5:{s:19:\"akismet/akismet.php\";s:5:\"2.2.6\";s:9:\"hello.php\";s:5:\"1.5.1\";s:16:\"russian-date.php\";s:4:\"1.01\";s:14:\"rus-to-lat.php\";s:3:\"0.3\";s:25:\"total_disable_updates.php\";s:3:\"1.1\";}s:8:\"response\";a:1:{s:19:\"akismet/akismet.php\";O:8:\"stdClass\":5:{s:2:\"id\";s:2:\"15\";s:4:\"slug\";s:7:\"akismet\";s:11:\"new_version\";s:5:\"2.2.9\";s:3:\"url\";s:44:\"http://wordpress.org/extend/plugins/akismet/\";s:7:\"package\";s:55:\"http://downloads.wordpress.org/plugin/akismet.2.2.9.zip\";}}}','yes'),(101,0,'auth_salt','QdlbnL*A0LJi@sx8VzHn9usigjHZ1!z9(zzMBfcQ3pmxthwMF#DY$N&UGXF@xkY7','yes'),(102,0,'widget_pages','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(103,0,'widget_calendar','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(104,0,'widget_archives','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(105,0,'widget_links','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(106,0,'widget_meta','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(107,0,'widget_search','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(108,0,'widget_recent-posts','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(109,0,'widget_recent-comments','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(110,0,'widget_tag_cloud','a:2:{i:2;a:0:{}s:12:\"_multiwidget\";i:1;}','yes'),(112,0,'_transient_update_themes','O:8:\"stdClass\":1:{s:12:\"last_checked\";i:1276013115;}','yes'),(113,0,'dashboard_widget_options','a:3:{s:24:\"dashboard_incoming_links\";a:5:{s:4:\"home\";s:26:\"http://wordpress.localhost\";s:4:\"link\";s:108:\"http://blogsearch.google.com/blogsearch?hl=en&scoring=d&partner=wordpress&q=link:http://wordpress.localhost/\";s:3:\"url\";s:141:\"http://blogsearch.google.com/blogsearch_feeds?hl=en&scoring=d&ie=utf-8&num=20&output=rss&partner=wordpress&q=link:http://wordpress.localhost/\";s:5:\"items\";i:10;s:9:\"show_date\";b:0;}s:17:\"dashboard_primary\";a:7:{s:4:\"link\";s:33:\"http://wordpress.org/development/\";s:3:\"url\";s:38:\"http://wordpress.org/development/feed/\";s:5:\"title\";s:45:\"Блог разработчиков WordPress\";s:5:\"items\";i:2;s:12:\"show_summary\";i:1;s:11:\"show_author\";i:0;s:9:\"show_date\";i:1;}s:19:\"dashboard_secondary\";a:4:{s:4:\"link\";s:28:\"http://planet.wordpress.org/\";s:3:\"url\";s:33:\"http://planet.wordpress.org/feed/\";s:5:\"title\";s:37:\"Другие новости WordPress\";s:5:\"items\";i:5;}}','yes'),(114,0,'nonce_salt','uJcYsD#0vPCIVnjNaDE3&R68S0Tl20TZlgj(uQzM%Ey&BVRB4Z0!H6ErLms0!#*r','yes'),(115,0,'current_theme','WordPress Default','yes'),(118,0,'_transient_timeout_feed_mod_a1e726e3488ce7357765147057682201','1276056321','no'),(120,0,'can_compress_scripts','1','yes'),(123,0,'_transient_timeout_feed_mod_a5420c83891a9c88ad2a4f04584a5efc','1276056323','no'),(127,0,'_transient_timeout_feed_mod_57bc725ad6568758915363af670fd8bc','1276056325','no'),(131,0,'_transient_timeout_feed_mod_0ff4b43bd116a9d8720d689c80e7dfd4','1276056325','no'),(135,0,'_transient_timeout_feed_mod_1a5f760f2e2b48827d4974a60857e7c2','1276056326','no'),(147,0,'_transient_timeout_plugin_slugs','1277631445','no'),(148,0,'_transient_plugin_slugs','a:5:{i:0;s:19:\"akismet/akismet.php\";i:1;s:9:\"hello.php\";i:2;s:16:\"russian-date.php\";i:3;s:14:\"rus-to-lat.php\";i:4;s:25:\"total_disable_updates.php\";}','no'),(141,0,'_transient_timeout_feed_mod_867bd5c64f85878d03a060509cd2f92c','1276056339','no'),(145,0,'recently_activated','a:0:{}','yes'),(152,0,'category_children','a:0:{}','yes');
/*!40000 ALTER TABLE `wp_options` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_postmeta`
--

DROP TABLE IF EXISTS `wp_postmeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_postmeta` (
  `meta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext,
  PRIMARY KEY (`meta_id`),
  KEY `post_id` (`post_id`),
  KEY `meta_key` (`meta_key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_postmeta`
--

LOCK TABLES `wp_postmeta` WRITE;
/*!40000 ALTER TABLE `wp_postmeta` DISABLE KEYS */;
/*!40000 ALTER TABLE `wp_postmeta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_posts`
--

DROP TABLE IF EXISTS `wp_posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_posts` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `post_author` bigint(20) unsigned NOT NULL DEFAULT '0',
  `post_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_date_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_content` longtext NOT NULL,
  `post_title` text NOT NULL,
  `post_excerpt` text NOT NULL,
  `post_status` varchar(20) NOT NULL DEFAULT 'publish',
  `comment_status` varchar(20) NOT NULL DEFAULT 'open',
  `ping_status` varchar(20) NOT NULL DEFAULT 'open',
  `post_password` varchar(20) NOT NULL DEFAULT '',
  `post_name` varchar(200) NOT NULL DEFAULT '',
  `to_ping` text NOT NULL,
  `pinged` text NOT NULL,
  `post_modified` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_modified_gmt` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `post_content_filtered` text NOT NULL,
  `post_parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `guid` varchar(255) NOT NULL DEFAULT '',
  `menu_order` int(11) NOT NULL DEFAULT '0',
  `post_type` varchar(20) NOT NULL DEFAULT 'post',
  `post_mime_type` varchar(100) NOT NULL DEFAULT '',
  `comment_count` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`ID`),
  KEY `post_name` (`post_name`),
  KEY `type_status_date` (`post_type`,`post_status`,`post_date`,`ID`),
  KEY `post_parent` (`post_parent`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_posts`
--

LOCK TABLES `wp_posts` WRITE;
/*!40000 ALTER TABLE `wp_posts` DISABLE KEYS */;
INSERT INTO `wp_posts` VALUES (1,1,'2010-06-08 20:04:57','2010-06-08 16:04:57','Добро пожаловать в WordPress. Спасибо за выбор качественного перевода от lecactus.ru. Это ваша первая запись. Отредактируйте или удалите ее. Затем начинайте заниматься блогингом!<br /><br /><em>Для начала убедитесь, что вы скачали дистрибутив именно с сайта <a href=\"http://lecactus.ru\">lecactus.ru</a>, т.к. только там я могу гарантировать отсутствие вирусов, троянов и иных вмешательств в код.</em><br /><br /><strong>Внимание! Прежде чем приступить к работе, для того чтобы избежать проблем в будущем, выполните указанные ниже действия:</strong><ol><li> Создайте директорию wp-content/uploads, либо создайте папку для ваших загружаемых файлов в другом месте (например папку «images» в корневой директории блога) и пропишите этот путь/и полный путь url в «настройках блога»-«разное»  и установите на эту папку права доступа «777»</li><li>Запустите PhpMyAdmin (найдите его в панели управления хостингом) и проверьте что параметр «collation» (оно же «сопоставление») как в настройках всей базы, так и в каждой таблице выглядит как «utf8_general_ci» либо «utf8_unicode_ci». Если вы видите там что то вроде «cp1251_general_ci» либо «latin1_swedish» и т.п., то лучше всего очистите базу данных сразу и в свойствах базы данных выставите «сопоставление» принудительно в «utf8_general_ci». После этого инсталлируйте блог повторно и проверьте базу еще раз.</li><li>Проверьте что на всех папках (кроме «папки загрузок») стоят права 755, а на всех файлах 644. Если вам нужно разрешить запись в какие-либо файлы (например файл конфигурации или .htaccess, то установите на них права 666 (либо 664). Помните, что некоторые настройки блога (например установка шаблона ссылок требуют этого).</li><li> Для вашей безопасности, на файлы в корне блога (кроме sitemap.xml если вы используете генератор карты сайта) после всех настроек рекомендуется установить права 444 («только для чтения»). Если вам требуется внести изменения в них, то временно ставьте права указанные в п.3, а затем верните все как было.</li><li><a href=\"http://lecactus.ru/wordpress/moj-faq-po-wordpress/\">Прочитайте FAQ по WordPress для быстрого решения потенциальных \"проблем\"</a>, таких как например \"абракадабра(закорючки) в админке при сохранении записей\", не работающая локализация и т.д.</li><li>Для повышения быстродействия и снижения потребления ресурсов WordPress рекомендуется включить <a href=\"http://lecactus.ru/2008/11/15/3110/\" title=\"Прочитать как это работает\">лайт-перевод</a> и <a href=\"http://lecactus.ru/2008/11/27/3232/\" title=\"Прочитать как это работает\">отключить сервисы проверки обновлений</a>. Все это уже есть в дистрибутиве, только включите нужный плагин и отредактируйте файл конфигурации</li><li>Если вы еще не сделали этого, прочитайте наконец README и другие текстовые файлы в дистрибутиве. </li></ol>','Привет мир!','','publish','open','open','','privet-mir','','','2010-06-08 20:04:57','2010-06-08 16:04:57','',0,'http://wordpress.localhost/?p=1',0,'post','',1),(2,1,'2010-06-08 20:04:57','2010-06-08 16:04:57','Это пример страницы в WordPress. Вы можете написать здесь информацию о себе или о сайте, чтобы пользователи знали кто вы и откуда. Вы можете создать столько страниц и подстраниц, сколько необходимо и управлять их содержанием прямо в WordPress.','О сайте','','publish','open','open','','about','','','2010-06-08 20:04:57','2010-06-08 16:04:57','',0,'http://wordpress.localhost/?page_id=2',0,'page','',0);
/*!40000 ALTER TABLE `wp_posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_term_relationships`
--

DROP TABLE IF EXISTS `wp_term_relationships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_term_relationships` (
  `object_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `term_taxonomy_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `term_order` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`object_id`,`term_taxonomy_id`),
  KEY `term_taxonomy_id` (`term_taxonomy_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_term_relationships`
--

LOCK TABLES `wp_term_relationships` WRITE;
/*!40000 ALTER TABLE `wp_term_relationships` DISABLE KEYS */;
INSERT INTO `wp_term_relationships` VALUES (1,2,0),(2,2,0),(3,2,0),(4,2,0),(5,2,0),(6,2,0),(7,2,0),(1,1,0);
/*!40000 ALTER TABLE `wp_term_relationships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_term_taxonomy`
--

DROP TABLE IF EXISTS `wp_term_taxonomy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_term_taxonomy` (
  `term_taxonomy_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `term_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `taxonomy` varchar(32) NOT NULL DEFAULT '',
  `description` longtext NOT NULL,
  `parent` bigint(20) unsigned NOT NULL DEFAULT '0',
  `count` bigint(20) NOT NULL DEFAULT '0',
  PRIMARY KEY (`term_taxonomy_id`),
  UNIQUE KEY `term_id_taxonomy` (`term_id`,`taxonomy`),
  KEY `taxonomy` (`taxonomy`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_term_taxonomy`
--

LOCK TABLES `wp_term_taxonomy` WRITE;
/*!40000 ALTER TABLE `wp_term_taxonomy` DISABLE KEYS */;
INSERT INTO `wp_term_taxonomy` VALUES (1,1,'category','',0,1),(2,2,'link_category','',0,7);
/*!40000 ALTER TABLE `wp_term_taxonomy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_terms`
--

DROP TABLE IF EXISTS `wp_terms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_terms` (
  `term_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL DEFAULT '',
  `slug` varchar(200) NOT NULL DEFAULT '',
  `term_group` bigint(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`term_id`),
  UNIQUE KEY `slug` (`slug`),
  KEY `name` (`name`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_terms`
--

LOCK TABLES `wp_terms` WRITE;
/*!40000 ALTER TABLE `wp_terms` DISABLE KEYS */;
INSERT INTO `wp_terms` VALUES (1,'Новости','%d0%bd%d0%be%d0%b2%d0%be%d1%81%d1%82%d0%b8',0),(2,'Ссылки','%d1%81%d1%81%d1%8b%d0%bb%d0%ba%d0%b8',0);
/*!40000 ALTER TABLE `wp_terms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_usermeta`
--

DROP TABLE IF EXISTS `wp_usermeta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_usermeta` (
  `umeta_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL DEFAULT '0',
  `meta_key` varchar(255) DEFAULT NULL,
  `meta_value` longtext,
  PRIMARY KEY (`umeta_id`),
  KEY `user_id` (`user_id`),
  KEY `meta_key` (`meta_key`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_usermeta`
--

LOCK TABLES `wp_usermeta` WRITE;
/*!40000 ALTER TABLE `wp_usermeta` DISABLE KEYS */;
INSERT INTO `wp_usermeta` VALUES (1,1,'nickname','admin'),(2,1,'rich_editing','true'),(3,1,'comment_shortcuts','false'),(4,1,'admin_color','fresh'),(5,1,'wp_capabilities','a:1:{s:13:\"administrator\";b:1;}'),(7,1,'wp_user_level','10'),(8,1,'wp_usersettings','m7=o&m0=c&m1=c&m2=c&m3=c&m4=c&m5=o&m6=c&m8=o'),(9,1,'wp_usersettingstime','1276013177');
/*!40000 ALTER TABLE `wp_usermeta` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `wp_users`
--

DROP TABLE IF EXISTS `wp_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wp_users` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_login` varchar(60) NOT NULL DEFAULT '',
  `user_pass` varchar(64) NOT NULL DEFAULT '',
  `user_nicename` varchar(50) NOT NULL DEFAULT '',
  `user_email` varchar(100) NOT NULL DEFAULT '',
  `user_url` varchar(100) NOT NULL DEFAULT '',
  `user_registered` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `user_activation_key` varchar(60) NOT NULL DEFAULT '',
  `user_status` int(11) NOT NULL DEFAULT '0',
  `display_name` varchar(250) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  KEY `user_login_key` (`user_login`),
  KEY `user_nicename` (`user_nicename`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `wp_users`
--

LOCK TABLES `wp_users` WRITE;
/*!40000 ALTER TABLE `wp_users` DISABLE KEYS */;
INSERT INTO `wp_users` VALUES (1,'admin','$P$BVFNFv2zKHbPmkBA.3MfULuN6CeMMt0','admin','helljump@gmail.com','','2010-06-08 16:04:57','',0,'admin');
/*!40000 ALTER TABLE `wp_users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-06-26 14:16:34
