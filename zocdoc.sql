-- MySQL dump 10.13  Distrib 5.6.27, for osx10.10 (x86_64)
--
-- Host: 127.0.0.1    Database: test
-- ------------------------------------------------------
-- Server version	5.6.27

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
-- Table structure for table `badges`
--

DROP TABLE IF EXISTS `badges`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `badges` (
  `badges_id` int(11) NOT NULL AUTO_INCREMENT,
  `badges_name` varchar(128) NOT NULL,
  PRIMARY KEY (`badges_id`)
) ENGINE=InnoDB AUTO_INCREMENT=298 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `badges_doc`
--

DROP TABLE IF EXISTS `badges_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `badges_doc` (
  `doc_id` int(11) DEFAULT NULL,
  `badges_id` int(11) DEFAULT NULL,
  KEY `doc_id` (`doc_id`),
  KEY `badges_id` (`badges_id`),
  CONSTRAINT `badges_doc_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`),
  CONSTRAINT `badges_doc_ibfk_2` FOREIGN KEY (`badges_id`) REFERENCES `badges` (`badges_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `certification`
--

DROP TABLE IF EXISTS `certification`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `certification` (
  `cer_id` int(11) NOT NULL AUTO_INCREMENT,
  `cer_name` varchar(1024) NOT NULL,
  PRIMARY KEY (`cer_id`)
) ENGINE=InnoDB AUTO_INCREMENT=303 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `certification_doc`
--

DROP TABLE IF EXISTS `certification_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `certification_doc` (
  `cer_id` int(11) DEFAULT NULL,
  `doc_id` int(11) DEFAULT NULL,
  KEY `doc_id` (`doc_id`),
  KEY `cer_id` (`cer_id`),
  CONSTRAINT `certification_doc_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`),
  CONSTRAINT `certification_doc_ibfk_2` FOREIGN KEY (`cer_id`) REFERENCES `certification` (`cer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `comment`
--

DROP TABLE IF EXISTS `comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `comment` (
  `comm_id` int(11) NOT NULL AUTO_INCREMENT,
  `doc_id` int(11) DEFAULT NULL,
  `comm_time` varchar(128) DEFAULT NULL,
  `comm_author` varchar(128) DEFAULT NULL,
  `overall_rating` varchar(20) DEFAULT NULL,
  `bedside_rating` varchar(20) DEFAULT NULL,
  `wait_time` varchar(20) DEFAULT NULL,
  `content` text,
  PRIMARY KEY (`comm_id`),
  KEY `doc_id` (`doc_id`),
  CONSTRAINT `comment_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`)
) ENGINE=InnoDB AUTO_INCREMENT=26026 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `doctor`
--

DROP TABLE IF EXISTS `doctor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `doctor` (
  `doc_id` int(11) NOT NULL,
  `doc_name` varchar(128) NOT NULL,
  `doc_gender` varchar(10) DEFAULT NULL,
  `doc_state` varchar(128) DEFAULT NULL,
  `doc_city` varchar(128) DEFAULT NULL,
  `doc_rating` varchar(128) DEFAULT NULL,
  `doc_address1` varchar(128) DEFAULT NULL,
  `doc_address2` varchar(128) DEFAULT NULL,
  `doc_practice_name` varchar(128) DEFAULT NULL,
  `doc_specialty_name` varchar(128) DEFAULT NULL,
  `doc_sub_specialty_name` varchar(128) DEFAULT NULL,
  `doc_title` varchar(128) DEFAULT NULL,
  `doc_professional_statement` text,
  PRIMARY KEY (`doc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `education`
--

DROP TABLE IF EXISTS `education`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `education` (
  `edu_id` int(11) NOT NULL AUTO_INCREMENT,
  `edu_name` varchar(1024) NOT NULL,
  PRIMARY KEY (`edu_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2079 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `education_doc`
--

DROP TABLE IF EXISTS `education_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `education_doc` (
  `edu_id` int(11) DEFAULT NULL,
  `doc_id` int(11) DEFAULT NULL,
  KEY `doc_id` (`doc_id`),
  KEY `edu_id` (`edu_id`),
  CONSTRAINT `education_doc_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`),
  CONSTRAINT `education_doc_ibfk_2` FOREIGN KEY (`edu_id`) REFERENCES `education` (`edu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance`
--

DROP TABLE IF EXISTS `insurance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance` (
  `insu_id` int(11) NOT NULL AUTO_INCREMENT,
  `insu_name` varchar(128) NOT NULL,
  PRIMARY KEY (`insu_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1851 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `insurance_doc`
--

DROP TABLE IF EXISTS `insurance_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `insurance_doc` (
  `doc_id` int(11) DEFAULT NULL,
  `insu_id` int(11) DEFAULT NULL,
  KEY `doc_id` (`doc_id`),
  KEY `insu_id` (`insu_id`),
  CONSTRAINT `insurance_doc_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`),
  CONSTRAINT `insurance_doc_ibfk_2` FOREIGN KEY (`insu_id`) REFERENCES `insurance` (`insu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `language`
--

DROP TABLE IF EXISTS `language`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `language` (
  `lang_id` int(11) NOT NULL AUTO_INCREMENT,
  `lang_name` varchar(128) NOT NULL,
  PRIMARY KEY (`lang_id`)
) ENGINE=InnoDB AUTO_INCREMENT=248 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `language_doc`
--

DROP TABLE IF EXISTS `language_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `language_doc` (
  `lang_id` int(11) DEFAULT NULL,
  `doc_id` int(11) DEFAULT NULL,
  KEY `doc_id` (`doc_id`),
  KEY `lang_id` (`lang_id`),
  CONSTRAINT `language_doc_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`),
  CONSTRAINT `language_doc_ibfk_2` FOREIGN KEY (`lang_id`) REFERENCES `language` (`lang_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `specialty`
--

DROP TABLE IF EXISTS `specialty`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `specialty` (
  `spec_id` int(11) NOT NULL AUTO_INCREMENT,
  `spec_name` varchar(128) NOT NULL,
  PRIMARY KEY (`spec_id`)
) ENGINE=InnoDB AUTO_INCREMENT=271 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `specialty_doc`
--

DROP TABLE IF EXISTS `specialty_doc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `specialty_doc` (
  `doc_id` int(11) DEFAULT NULL,
  `spec_id` int(11) DEFAULT NULL,
  KEY `doc_id` (`doc_id`),
  KEY `spec_id` (`spec_id`),
  CONSTRAINT `specialty_doc_ibfk_1` FOREIGN KEY (`doc_id`) REFERENCES `doctor` (`doc_id`),
  CONSTRAINT `specialty_doc_ibfk_2` FOREIGN KEY (`spec_id`) REFERENCES `specialty` (`spec_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `test`
--

DROP TABLE IF EXISTS `test`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test` (
  `id` int(11) DEFAULT NULL,
  `value` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-12-07 16:04:13
