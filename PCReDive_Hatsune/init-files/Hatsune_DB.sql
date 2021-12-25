/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 傾印 princess_connect_hatsune 的資料庫結構
CREATE DATABASE IF NOT EXISTS `princess_connect_hatsune` /*!40100 DEFAULT CHARACTER SET utf8mb4 */;
USE `princess_connect_hatsune`;

-- 傾印  資料表 princess_connect_hatsune.group 結構
CREATE TABLE IF NOT EXISTS `group` (
  `server_id` bigint(20) DEFAULT NULL,
  `sign_channel_id` bigint(20) DEFAULT NULL,
  `action_channel_id` bigint(20) DEFAULT NULL,
  `action_message_id` bigint(20) DEFAULT NULL,
  `reserved_message_id` bigint(20) DEFAULT NULL,
  `report_message_id` bigint(20) DEFAULT NULL,
  `now_week` tinyint(4) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect_hatsune.knifes 結構
CREATE TABLE IF NOT EXISTS `knifes` (
  `serial_number` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) NOT NULL,
  `member_id` bigint(20) NOT NULL,
  `sockpuppet` int(11) unsigned NOT NULL DEFAULT 0,
  `type` int(11) NOT NULL,
  `week` tinyint(4) unsigned NOT NULL DEFAULT 0,
  `boss` tinyint(4) unsigned NOT NULL DEFAULT 0,
  `reserved_time` tinyint(4) NOT NULL DEFAULT 0,
  `damage` int(11) NOT NULL DEFAULT 0,
  `comment` varchar(150) NOT NULL DEFAULT '',
  `update_time` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`serial_number`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=129 DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

-- 傾印  資料表 princess_connect_hatsune.members 結構
CREATE TABLE IF NOT EXISTS `members` (
  `serial_number` int(11) NOT NULL AUTO_INCREMENT,
  `server_id` bigint(20) DEFAULT NULL,
  `member_id` bigint(20) DEFAULT NULL,
  `sl_time` datetime DEFAULT current_timestamp(),
  `sockpuppet` int(10) unsigned NOT NULL DEFAULT 0,
  `now_using` tinyint(3) unsigned NOT NULL DEFAULT 1,
  PRIMARY KEY (`serial_number`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4;

-- 取消選取資料匯出。

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
