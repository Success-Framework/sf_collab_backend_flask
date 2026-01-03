-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: mysql-367e2d56-mohamed311-06d1.f.aivencloud.com    Database: defaultdb
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

-- Ensure user exists with correct host
CREATE USER IF NOT EXISTS 'sfcollab'@'%' IDENTIFIED BY 'sfcollab_pass';

-- Always reset privileges
GRANT ALL PRIVILEGES ON sfcollab_db.* TO 'sfcollab'@'%';

FLUSH PRIVILEGES;

--
-- GTID state at the beginning of the backup 
--
CREATE TABLE `activities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(255) NOT NULL,
  `details` text,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` text,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `action` (`action`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `activities_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
--
-- Table structure for table `achievements`
--
DROP TABLE IF EXISTS `waitlist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `waitlist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_activity_at` datetime DEFAULT NULL,
  `referral_points` int DEFAULT 0,
  `contribution_points` int DEFAULT 0,
  `activity_points` int DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `ix_email` (`email`),
  KEY `ix_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40101 SET character_set_client = @saved_cs_client */;
--
-- Dumping data for table `waitlist`
--


LOCK TABLES `waitlist` WRITE;


/*!40000 ALTER TABLE `waitlist` DISABLE KEYS */;
/*!40000 ALTER TABLE `waitlist` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `content` text NOT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `achievements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `achievements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text,
  `icon` varchar(100) DEFAULT NULL,
  `category` enum('task','social','learning','milestone') DEFAULT NULL,
  `points` int DEFAULT NULL,
  `requirement_type` varchar(50) DEFAULT NULL,
  `requirement_value` int DEFAULT NULL,
  `badge_color` varchar(20) DEFAULT NULL,
  `rarity` enum('common','rare','epic','legendary') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=235 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `achievements`
--

LOCK TABLES `achievements` WRITE;
/*!40000 ALTER TABLE `achievements` DISABLE KEYS */;
INSERT INTO `achievements` VALUES (100,'First Idea','Create your first business idea','­ƒÆí','milestone',100,'ideas_created',1,NULL,'common',NULL),(101,'Idea Machine','Create 10 business ideas','­ƒÜÇ','milestone',500,'ideas_created',10,NULL,'rare',NULL),(102,'Idea Factory','Create 50 business ideas','­ƒÅ¡','milestone',1000,'ideas_created',50,NULL,'epic',NULL),(103,'Idea Visionary','Create 100 business ideas','­ƒö¡','milestone',2500,'ideas_created',100,NULL,'legendary',NULL),(104,'First Task','Complete your first task','Ôÿæ´©Å','milestone',50,'tasks_completed',1,NULL,'common',NULL),(105,'Task Master','Complete 50 tasks','Ô£à','milestone',300,'tasks_completed',50,NULL,'rare',NULL),(106,'Productivity Guru','Complete 200 tasks','ÔÜí','milestone',800,'tasks_completed',200,NULL,'epic',NULL),(107,'Task Titan','Complete 500 tasks','­ƒÅå','milestone',2000,'tasks_completed',500,NULL,'legendary',NULL),(108,'7-Day Streak','Maintain a 7-day activity streak','­ƒöÑ','milestone',150,'streak_days',7,NULL,'common',NULL),(109,'Month of Momentum','Maintain a 30-day activity streak','­ƒôà','milestone',500,'streak_days',30,NULL,'rare',NULL),(110,'Dedicated Developer','Maintain a 90-day activity streak','­ƒÆ¬','milestone',1500,'streak_days',90,NULL,'epic',NULL),(111,'Unstoppable Force','Maintain a 365-day activity streak','­ƒîƒ','milestone',5000,'streak_days',365,NULL,'legendary',NULL),(112,'First Comment','Make your first comment','­ƒÆ¼','social',50,'comments_made',1,NULL,'common',NULL),(113,'Comment Contributor','Make 25 comments on ideas','­ƒÆ¼','social',200,'comments_made',25,NULL,'common',NULL),(114,'Active Commenter','Make 100 comments','­ƒùú´©Å','social',500,'comments_made',100,NULL,'rare',NULL),(115,'Discussion Leader','Make 500 comments','­ƒææ','social',1200,'comments_made',500,NULL,'epic',NULL),(116,'First Like','Receive your first like','­ƒæì','social',25,'likes_received',1,NULL,'common',NULL),(117,'Popular Idea','Get 100 likes on your ideas','ÔØñ´©Å','social',400,'likes_received',100,NULL,'epic',NULL),(118,'Community Favorite','Get 500 likes on your ideas','Ô¡É','social',1000,'likes_received',500,NULL,'epic',NULL),(119,'Internet Sensation','Get 1000 likes on your ideas','­ƒîÉ','social',2500,'likes_received',1000,NULL,'legendary',NULL),(120,'First Follower','Gain your first follower','­ƒæÑ','social',100,'followers_gained',1,NULL,'common',NULL),(121,'Growing Audience','Gain 10 followers','­ƒôê','social',300,'followers_gained',10,NULL,'common',NULL),(122,'Influencer','Gain 50 followers','­ƒôó','social',800,'followers_gained',50,NULL,'rare',NULL),(123,'Thought Leader','Gain 200 followers','­ƒÄ»','social',2000,'followers_gained',200,NULL,'epic',NULL),(124,'Early Bird','Complete a task before its due date','­ƒÉª','task',75,'tasks_completed_early',1,NULL,'common',NULL),(125,'Time Manager','Complete 25 tasks early','ÔÅ░','task',400,'tasks_completed_early',25,NULL,'rare',NULL),(126,'Last Minute Hero','Complete a task on the due date','­ƒª©','task',50,'tasks_completed_on_time',1,NULL,'common',NULL),(127,'Perfect Timing','Complete 50 tasks on their due date','­ƒÄ»','task',600,'tasks_completed_on_time',50,NULL,'rare',NULL),(128,'Task Explorer','Create tasks in 5 different categories','­ƒº¡','task',200,'task_categories_used',5,NULL,'common',NULL),(129,'Organized Mind','Create tasks in 10 different categories','­ƒùé´©Å','task',500,'task_categories_used',10,NULL,'rare',NULL),(130,'Detailed Thinker','Create an idea with 500+ characters','­ƒôØ','',150,'detailed_ideas',1,NULL,'common',NULL),(131,'Thorough Planner','Create 10 detailed ideas','­ƒôï','',600,'detailed_ideas',10,NULL,'rare',NULL),(132,'Idea Architect','Create an idea with attached documents','­ƒÅù´©Å','',200,'ideas_with_attachments',1,NULL,'common',NULL),(133,'Resourceful Creator','Create 20 ideas with attachments','­ƒôÄ','',800,'ideas_with_attachments',20,NULL,'rare',NULL),(134,'Team Player','Collaborate on 5 different ideas','­ƒñØ','',300,'ideas_collaborated',5,NULL,'common',NULL),(135,'Idea Partner','Collaborate on 20 different ideas','­ƒæÑ','',800,'ideas_collaborated',20,NULL,'rare',NULL),(136,'Master Collaborator','Collaborate on 50 different ideas','­ƒîƒ','',2000,'ideas_collaborated',50,NULL,'epic',NULL),(137,'Helpful Mentor','Get 10 helpful votes on your comments','­ƒÆí','',400,'helpful_votes_received',10,NULL,'rare',NULL),(138,'Weekend Warrior','Complete tasks on 5 different weekends','­ƒÄ¬','',300,'weekend_activities',5,NULL,'rare',NULL),(139,'Night Owl','Create ideas between 10 PM and 2 AM','­ƒªë','',250,'late_night_activities',5,NULL,'rare',NULL),(140,'Early Riser','Create ideas between 5 AM and 8 AM','­ƒîà','',250,'early_morning_activities',5,NULL,'rare',NULL),(141,'Platform Explorer','Use all major platform features','­ƒº®','',400,'features_used',10,NULL,'rare',NULL),(142,'Power User','Use platform for 30 consecutive days','ÔÜí','',600,'consecutive_days_used',30,NULL,'epic',NULL),(143,'Platform Veteran','Use platform for 180 days total','­ƒøí´©Å','',1500,'total_days_used',180,NULL,'epic',NULL),(144,'Creative Spark','Create ideas in 3 different categories','­ƒÄ¿','',200,'idea_categories_used',3,NULL,'common',NULL),(145,'Diverse Thinker','Create ideas in 10 different categories','­ƒîê','',700,'idea_categories_used',10,NULL,'rare',NULL),(146,'Innovation Master','Create ideas in 20 different categories','­ƒÆÄ','',1500,'idea_categories_used',20,NULL,'epic',NULL),(147,'First Share','Share your first idea externally','­ƒôñ','social',100,'ideas_shared',1,NULL,'common',NULL),(148,'Social Butterfly','Share 25 ideas externally','­ƒªï','social',500,'ideas_shared',25,NULL,'rare',NULL),(149,'Bookworm','Read 50 idea descriptions completely','­ƒôÜ','',300,'ideas_read_completely',50,NULL,'common',NULL),(150,'Knowledge Seeker','Read 200 idea descriptions completely','­ƒöì','',800,'ideas_read_completely',200,NULL,'rare',NULL),(151,'Feedback Provider','Give feedback on 10 different ideas','­ƒôØ','',400,'feedbacks_given',10,NULL,'common',NULL),(152,'Constructive Critic','Give feedback on 50 different ideas','­ƒÅù´©Å','',1000,'feedbacks_given',50,NULL,'rare',NULL),(153,'Idea Refiner','Update and improve 10 existing ideas','Ô£¿','',500,'ideas_improved',10,NULL,'rare',NULL),(154,'Perfectionist','Update and improve 50 existing ideas','­ƒÄ¡','',1200,'ideas_improved',50,NULL,'epic',NULL),(155,'Mobile User','Use the platform on mobile device','­ƒô▒','',100,'mobile_sessions',1,NULL,'common',NULL),(156,'On-the-Go','Use platform on mobile 50 times','­ƒÜÂ','',400,'mobile_sessions',50,NULL,'rare',NULL),(157,'Desktop Commander','Use platform on desktop 100 times','­ƒÆ╗','',500,'desktop_sessions',100,NULL,'rare',NULL),(158,'Multi-Platform','Use platform on 3 different devices','­ƒöä','',300,'devices_used',3,NULL,'common',NULL),(159,'Seasoned Veteran','Use platform for 1 year','­ƒÄé','milestone',1000,'account_age_days',365,NULL,'epic',NULL),(160,'Long-term Visionary','Use platform for 2 years','Ôîø','milestone',2500,'account_age_days',730,NULL,'legendary',NULL),(161,'Idea Collector','Save 20 ideas to your favorites','Ô¡É','',300,'ideas_saved',20,NULL,'common',NULL),(162,'Curator','Save 100 ideas to your favorites','­ƒÅø´©Å','',800,'ideas_saved',100,NULL,'rare',NULL),(163,'Archivist','Save 500 ideas to your favorites','­ƒôÜ','',2000,'ideas_saved',500,NULL,'epic',NULL),(164,'Tag Master','Use 50 different tags on ideas','­ƒÅÀ´©Å','',400,'unique_tags_used',50,NULL,'rare',NULL),(165,'Organized Mind','Create 10 custom categories','­ƒùâ´©Å','',500,'custom_categories_created',10,NULL,'rare',NULL),(166,'Template Creator','Create 5 idea templates','­ƒôä','',600,'templates_created',5,NULL,'epic',NULL),(167,'Quick Draw','Complete a task within 1 hour of creating it','ÔÜí','task',150,'quick_tasks_completed',1,NULL,'common',NULL),(168,'Speed Demon','Complete 20 tasks within 1 hour','­ƒÄ»','task',600,'quick_tasks_completed',20,NULL,'rare',NULL),(169,'Weekly Regular','Use platform 4 weeks in a row','­ƒôå','',300,'consecutive_weeks',4,NULL,'common',NULL),(170,'Monthly Champion','Use platform 6 months in a row','­ƒÅà','',1000,'consecutive_months',6,NULL,'epic',NULL),(171,'Welcome Committee','Welcome 10 new users','­ƒæï','',400,'new_users_welcomed',10,NULL,'rare',NULL),(172,'Community Builder','Welcome 50 new users','­ƒÅÿ´©Å','',1200,'new_users_welcomed',50,NULL,'epic',NULL),(173,'Quick Learner','Complete the platform tutorial','­ƒÄô','learning',200,'tutorial_completed',1,NULL,'common',NULL),(174,'Feature Expert','Use all advanced features','­ƒºá','learning',800,'advanced_features_used',10,NULL,'epic',NULL),(175,'New Year Innovator','Create an idea on January 1st','­ƒÄå','',250,'new_years_idea',1,NULL,'rare',NULL),(176,'Summer Thinker','Create ideas during summer months','ÔÿÇ´©Å','',300,'summer_ideas',5,NULL,'common',NULL),(177,'Challenge Accepted','Participate in your first challenge','­ƒÄ¬','',200,'challenges_participated',1,NULL,'common',NULL),(178,'Challenge Champion','Win 5 challenges','­ƒÅå','',1500,'challenges_won',5,NULL,'epic',NULL),(179,'Level Up','Reach level 10','Ô¼å´©Å','',500,'user_level',10,NULL,'common',NULL),(180,'Master Level','Reach level 50','­ƒÄ»','',2000,'user_level',50,NULL,'epic',NULL),(181,'Achievement Hunter','Earn 50 different achievements','­ƒÅ╣','',1000,'achievements_earned',50,NULL,'rare',NULL),(182,'Completionist','Earn 100 different achievements','­ƒÆ»','',3000,'achievements_earned',100,NULL,'legendary',NULL),(183,'First Project','Create your first project','­ƒôü','milestone',150,'projects_created',1,NULL,'common',NULL),(184,'Project Manager','Create 10 projects','­ƒæ¿ÔÇì­ƒÆ╝','milestone',600,'projects_created',10,NULL,'rare',NULL),(185,'Portfolio Builder','Create 25 projects','­ƒÆ╝','milestone',1200,'projects_created',25,NULL,'epic',NULL),(186,'Enterprise Architect','Create 50 projects','­ƒÅó','milestone',2500,'projects_created',50,NULL,'legendary',NULL),(187,'Task Streak','Complete tasks for 7 days straight','­ƒôè','task',400,'task_streak_days',7,NULL,'rare',NULL),(188,'Task Marathon','Complete tasks for 30 days straight','­ƒÅâ','task',1000,'task_streak_days',30,NULL,'epic',NULL),(189,'Priority Handler','Complete 20 high priority tasks','­ƒö┤','task',500,'high_priority_tasks',20,NULL,'rare',NULL),(190,'Urgent Expert','Complete 50 urgent tasks','­ƒÜ¿','task',1200,'urgent_tasks',50,NULL,'epic',NULL),(191,'Like Giver','Like 50 different ideas','­ƒæì','social',300,'likes_given',50,NULL,'common',NULL),(192,'Supportive Member','Like 200 different ideas','­ƒÆØ','social',800,'likes_given',200,NULL,'rare',NULL),(193,'Community Pillar','Like 500 different ideas','­ƒÅø´©Å','social',1500,'likes_given',500,NULL,'epic',NULL),(194,'Following Active','Follow 20 other users','­ƒæÇ','social',300,'users_followed',20,NULL,'common',NULL),(195,'Network Builder','Follow 50 other users','­ƒò©´©Å','social',700,'users_followed',50,NULL,'rare',NULL),(196,'Well Structured','Create idea with multiple sections','­ƒôæ','',200,'structured_ideas',1,NULL,'common',NULL),(197,'Detailed Planner','Create 15 well-structured ideas','­ƒôï','',600,'structured_ideas',15,NULL,'rare',NULL),(198,'Research Expert','Add research to 10 ideas','­ƒö¼','',800,'researched_ideas',10,NULL,'epic',NULL),(199,'Market Analyst','Conduct market research for 5 ideas','­ƒôè','',1000,'market_researched_ideas',5,NULL,'epic',NULL),(200,'Team Builder','Invite 5 users to collaborate','­ƒæÑ','',400,'collaborators_invited',5,NULL,'common',NULL),(201,'Collaboration Champion','Invite 20 users to collaborate','­ƒñØ','',1000,'collaborators_invited',20,NULL,'rare',NULL),(202,'Feedback Receiver','Receive feedback on 10 ideas','­ƒôÑ','',300,'feedbacks_received',10,NULL,'common',NULL),(203,'Open to Feedback','Receive feedback on 50 ideas','­ƒÄü','',800,'feedbacks_received',50,NULL,'rare',NULL),(204,'Settings Explorer','Customize your profile settings','ÔÜÖ´©Å','',100,'settings_customized',1,NULL,'common',NULL),(205,'Profile Perfect','Complete your profile 100%','­ƒæñ','',300,'profile_completed',1,NULL,'common',NULL),(206,'Notification Master','Configure all notification settings','­ƒöö','',200,'notifications_configured',1,NULL,'common',NULL),(207,'Theme Customizer','Change your theme','­ƒÄ¿','',150,'theme_changed',1,NULL,'common',NULL),(208,'Brainstormer','Create 5 ideas in one day','­ƒî¬´©Å','',400,'ideas_in_one_day',5,NULL,'rare',NULL),(209,'Idea Storm','Create 10 ideas in one day','Ôøê´©Å','',1000,'ideas_in_one_day',10,NULL,'epic',NULL),(210,'Creative Flow','Create ideas for 5 days straight','­ƒîè','',600,'creative_streak_days',5,NULL,'rare',NULL),(211,'Inspiration Wave','Create ideas for 14 days straight','­ƒîÇ','',1500,'creative_streak_days',14,NULL,'epic',NULL),(212,'Category Expert','Use 10 different categories','­ƒôé','',400,'categories_used',10,NULL,'common',NULL),(213,'Tag Innovator','Create 10 custom tags','­ƒÅÀ´©Å','',300,'custom_tags_created',10,NULL,'common',NULL),(214,'Folder Organizer','Organize ideas into folders','­ƒôü','',200,'folders_created',1,NULL,'common',NULL),(215,'System Architect','Create complex organization system','­ƒÅù´©Å','',800,'organization_systems',1,NULL,'epic',NULL),(216,'Daily Visitor','Visit platform for 10 consecutive days','­ƒôà','',300,'consecutive_visits',10,NULL,'common',NULL),(217,'Loyal User','Visit platform for 30 consecutive days','­ƒÆØ','',800,'consecutive_visits',30,NULL,'rare',NULL),(218,'Platform Advocate','Refer 5 friends to the platform','­ƒôó','',500,'friends_referred',5,NULL,'rare',NULL),(219,'Community Ambassador','Refer 20 friends to the platform','­ƒÄô','',1500,'friends_referred',20,NULL,'epic',NULL),(220,'Holiday Creator','Create idea on a holiday','­ƒÄä','',300,'holiday_ideas',1,NULL,'rare',NULL),(221,'Birthday Idea','Create idea on your birthday','­ƒÄé','',400,'birthday_ideas',1,NULL,'rare',NULL),(222,'Anniversary User','Use platform on account anniversary','­ƒÄë','',500,'anniversary_activities',1,NULL,'epic',NULL),(223,'Challenge Regular','Participate in 10 challenges','­ƒÄ¬','',600,'challenges_participated',10,NULL,'rare',NULL),(224,'Challenge Expert','Participate in 25 challenges','­ƒÅà','',1200,'challenges_participated',25,NULL,'epic',NULL),(225,'Top Performer','Finish in top 3 of a challenge','­ƒÑç','',800,'top_3_finishes',1,NULL,'epic',NULL),(226,'Challenge Dominator','Finish in top 3 of 10 challenges','­ƒææ','',2500,'top_3_finishes',10,NULL,'legendary',NULL),(227,'Rising Star','Reach level 5','Ô¡É','',200,'user_level',5,NULL,'common',NULL),(228,'Experienced User','Reach level 20','­ƒÄ»','',800,'user_level',20,NULL,'rare',NULL),(229,'Veteran User','Reach level 75','­ƒøí´©Å','',3000,'user_level',75,NULL,'legendary',NULL),(230,'Max Level','Reach maximum level','­ƒÅö´©Å','',5000,'user_level',100,NULL,'legendary',NULL),(231,'Trophy Collector','Earn 10 rare achievements','­ƒÅå','',800,'rare_achievements',10,NULL,'rare',NULL),(232,'Epic Collector','Earn 5 epic achievements','­ƒÆÄ','',1200,'epic_achievements',5,NULL,'epic',NULL),(233,'Legendary Collector','Earn 3 legendary achievements','­ƒîƒ','',2000,'legendary_achievements',3,NULL,'legendary',NULL),(234,'Achievement Master','Earn all common achievements','­ƒÄô','',1500,'common_achievements_all',1,NULL,'epic',NULL);
/*!40000 ALTER TABLE `achievements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('55cb5f25f54c'),('d659945d25c6');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `calendar_events`
--

DROP TABLE IF EXISTS `calendar_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `calendar_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `startup_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `start_date` datetime NOT NULL,
  `end_date` datetime DEFAULT NULL,
  `all_day` tinyint(1) DEFAULT NULL,
  `category` enum('meeting','deadline','reminder','event') DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `is_recurring` tinyint(1) DEFAULT NULL,
  `recurrence_rule` varchar(255) DEFAULT NULL,
  `reminder_minutes` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `calendar_events_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`),
  CONSTRAINT `calendar_events_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `calendar_events`
--

LOCK TABLES `calendar_events` WRITE;
/*!40000 ALTER TABLE `calendar_events` DISABLE KEYS */;
INSERT INTO `calendar_events` VALUES (1,104,24,'Weekly Team Sync','Weekly team meeting to discuss progress, blockers, and priorities for the upcoming week.','2025-11-10 10:00:00','2025-11-10 11:00:00',0,'meeting','#3B82F6','Zoom: https://zoom.us/j/123456789',1,'FREQ=WEEKLY;BYDAY=MO',15,'2025-11-01 17:20:56','2025-11-01 17:20:56'),(2,104,24,'Investor Pitch Practice','Practice session for upcoming investor pitch. Focus on demo flow and Q&A.','2025-11-17 14:00:00','2025-11-17 16:00:00',0,'meeting','#8B5CF6','Conference Room A',0,NULL,30,'2025-11-06 17:20:56','2025-11-06 17:20:56'),(3,104,24,'Beta Launch Deadline','Soft launch of beta version to first 100 users.','2025-11-24 00:00:00',NULL,1,'deadline','#EF4444',NULL,0,NULL,60,'2025-11-11 17:20:56','2025-11-26 17:20:56'),(4,104,24,'Tech Innovation Summit','Annual tech conference. Network with potential partners and investors.','2025-12-06 09:00:00','2025-12-06 18:00:00',0,'event','#10B981','Convention Center, Main Hall',0,NULL,60,'2025-11-16 17:20:56','2025-12-01 17:20:56'),(5,104,24,'Co-founder Sync','Weekly sync with co-founder to discuss strategy and operational items.','2025-11-17 16:00:00','2025-11-17 17:00:00',0,'meeting','#F59E0B','Co-working Space',1,'FREQ=WEEKLY;BYDAY=WE',10,'2025-11-03 17:20:56','2025-11-03 17:20:56'),(6,104,24,'Customer Feedback Session','User testing session with 5 beta customers to gather feedback on new features.','2025-12-03 13:00:00','2025-12-03 15:00:00',0,'meeting','#06B6D4','User Testing Lab',0,NULL,15,'2025-11-21 17:20:56','2025-11-29 17:20:56'),(7,104,24,'Q3 Roadmap Review','Quarterly product roadmap review with the product team.','2025-12-08 11:00:00','2025-12-08 13:00:00',0,'meeting','#8B5CF6','Product War Room',0,NULL,30,'2025-11-23 17:20:56','2025-12-01 17:20:56'),(8,104,24,'Startup Anniversary','Celebrating 1 year since founding! Team lunch and retrospective.','2025-12-11 00:00:00',NULL,1,'event','#EC4899','Office & Nearby Restaurant',0,NULL,1440,'2025-11-26 17:20:56','2025-12-01 17:20:56'),(9,104,24,'VC Firm Meeting','Meeting with potential investors from Sequoia Capital.','2025-12-04 15:00:00','2025-12-04 16:30:00',0,'meeting','#6366F1','VC Office - Downtown',0,NULL,60,'2025-11-24 17:20:56','2025-12-01 17:20:56'),(10,104,24,'Sprint Planning Session','Two-week sprint planning with engineering and product teams.','2025-12-02 09:30:00','2025-12-02 12:00:00',0,'meeting','#059669','Engineering Hub',1,'FREQ=WEEKLY;INTERVAL=2;BYDAY=FR',10,'2025-11-17 17:20:56','2025-11-28 17:20:56'),(11,104,24,'Team Building: Escape Room','Monthly team building activity to boost morale and collaboration.','2025-12-08 17:00:00','2025-12-08 20:00:00',0,'event','#F97316','Escape Room Downtown',1,'FREQ=MONTHLY;BYDAY=3FR',60,'2025-11-19 17:20:56','2025-12-01 17:20:56'),(12,104,24,'New Feature Launch','Launch of AI-powered recommendation engine feature.','2025-12-15 00:00:00',NULL,1,'reminder','#84CC16',NULL,0,NULL,1440,'2025-11-25 17:20:56','2025-12-01 17:20:56'),(13,104,24,'Legal Consultation: IP Protection','Meeting with legal team to discuss patent filing and IP strategy.','2025-12-05 10:00:00','2025-12-05 11:30:00',0,'meeting','#78716C','Law Firm Offices',0,NULL,30,'2025-11-22 17:20:56','2025-11-30 17:20:56'),(14,104,24,'Demo Day Dry Run','Full run-through of demo day presentation with mentors.','2025-12-07 14:00:00','2025-12-07 17:00:00',0,'meeting','#DC2626','Accelerator Space',0,NULL,15,'2025-11-27 17:20:56','2025-12-01 17:20:56'),(15,104,24,'Monthly Metrics Review','Review key performance indicators and metrics with leadership team.','2025-12-09 09:00:00','2025-12-09 10:30:00',0,'meeting','#0EA5E9','Board Room',1,'FREQ=MONTHLY;BYMONTHDAY=15',30,'2025-11-09 17:20:56','2025-11-24 17:20:56'),(16,104,NULL,'Dentist Appointment','Regular dental check-up and cleaning.','2025-12-03 16:00:00','2025-12-03 17:00:00',0,'reminder','#6B7280','Family Dental Clinic',0,NULL,60,'2025-11-26 17:20:57','2025-12-01 17:20:57'),(17,104,NULL,'Friend\'s Birthday Party','Celebrating Sarah\'s 30th birthday.','2025-12-04 19:00:00','2025-12-04 23:00:00',0,'event','#EC4899','The Rooftop Bar',0,NULL,120,'2025-11-28 17:20:57','2025-12-01 17:20:57'),(18,104,NULL,'Gym Session','Personal training session','2025-12-02 07:00:00','2025-12-02 08:00:00',0,'reminder','#10B981','Fitness Center',1,'FREQ=WEEKLY;BYDAY=MO,WE,FR',10,'2025-11-01 17:20:57','2025-11-01 17:20:57');
/*!40000 ALTER TABLE `calendar_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_conversations`
--

DROP TABLE IF EXISTS `chat_conversations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_conversations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `conversation_type` varchar(20) DEFAULT NULL,
  `created_by_id` int NOT NULL,
  `description` text,
  `avatar_url` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `settings` json DEFAULT NULL,
  `unread_count` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by_id` (`created_by_id`),
  CONSTRAINT `chat_conversations_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_conversations`
--

LOCK TABLES `chat_conversations` WRITE;
/*!40000 ALTER TABLE `chat_conversations` DISABLE KEYS */;
INSERT INTO `chat_conversations` VALUES (1,'Test Group Chat','group',11,'This is a test group',NULL,1,'{}',NULL,'2025-11-21 22:40:34','2025-11-26 05:46:14'),(2,NULL,'direct',11,NULL,NULL,1,'{}',NULL,'2025-11-22 01:40:06','2025-11-22 03:28:37'),(3,'sf collab group','group',11,'sf collab group group chat',NULL,1,'{}',NULL,'2025-11-22 03:44:55','2025-11-24 08:13:16'),(4,NULL,'direct',11,NULL,NULL,1,'{}',NULL,'2025-11-22 04:39:20','2025-11-26 19:35:12'),(100,'new','group',11,'new group chat',NULL,1,'{}',0,'2025-11-28 04:52:48','2025-11-28 04:52:48'),(101,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:16','2025-11-28 16:52:16'),(102,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:22','2025-11-28 16:52:22'),(103,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:27','2025-11-28 16:52:27'),(104,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:32','2025-11-28 16:53:33'),(105,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:38','2025-11-28 16:52:38'),(106,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:43','2025-11-28 16:52:43'),(107,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:48','2025-11-28 16:52:48'),(108,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:54','2025-11-28 16:52:54'),(109,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:52:59','2025-11-28 16:52:59'),(110,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:53:04','2025-11-28 16:53:04'),(111,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:53:10','2025-11-28 16:53:10'),(112,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:53:15','2025-11-28 16:53:15'),(113,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:53:20','2025-11-28 16:53:20'),(114,NULL,'direct',11,NULL,NULL,1,'{}',0,'2025-11-28 16:53:26','2025-11-28 16:53:26'),(115,NULL,'direct',104,NULL,NULL,1,'{}',0,'2025-12-05 01:17:41','2025-12-11 03:08:44'),(116,NULL,'direct',107,NULL,NULL,1,'{}',0,'2025-12-05 17:32:34','2025-12-05 17:32:34'),(117,'sf collab ui/ux','group',107,'sf collab ui/ux group chat',NULL,1,'{}',0,'2025-12-05 17:34:47','2025-12-05 17:35:13'),(118,NULL,'direct',104,NULL,NULL,1,'{}',0,'2025-12-07 02:35:45','2025-12-07 19:26:08'),(119,'','group',104,' group chat',NULL,1,'{}',0,'2025-12-07 03:12:30','2025-12-07 03:14:50'),(120,NULL,'direct',111,NULL,NULL,1,'{}',0,'2025-12-07 17:25:05','2025-12-07 17:25:05'),(121,NULL,'direct',111,NULL,NULL,1,'{}',0,'2025-12-07 17:25:08','2025-12-07 19:54:58'),(122,'test 2','group',104,'test 2 group chat',NULL,1,'{}',0,'2025-12-07 19:28:00','2025-12-11 18:48:08'),(123,NULL,'direct',108,NULL,NULL,1,'{}',0,'2025-12-08 18:14:27','2025-12-08 18:14:27'),(124,NULL,'direct',108,NULL,NULL,1,'{}',0,'2025-12-08 18:14:29','2025-12-08 18:14:29'),(125,NULL,'direct',118,NULL,NULL,1,'{}',0,'2025-12-11 22:34:38','2025-12-14 01:33:02'),(126,NULL,'direct',108,NULL,NULL,1,'{}',0,'2025-12-14 04:03:12','2025-12-14 04:03:12'),(127,NULL,'direct',108,NULL,NULL,1,'{}',0,'2025-12-14 04:03:14','2025-12-14 04:03:14'),(128,NULL,'direct',108,NULL,NULL,1,'{}',0,'2025-12-14 04:03:17','2025-12-14 04:03:17'),(129,NULL,'direct',108,NULL,NULL,1,'{}',0,'2025-12-14 04:03:18','2025-12-14 04:03:18'),(130,NULL,'direct',100,NULL,NULL,1,'{}',0,'2025-12-14 05:01:24','2025-12-14 05:01:52');
/*!40000 ALTER TABLE `chat_conversations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `chat_messages`
--

DROP TABLE IF EXISTS `chat_messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `chat_messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `conversation_id` int NOT NULL,
  `sender_id` int NOT NULL,
  `original_content` text NOT NULL,
  `sender_timezone` varchar(50) DEFAULT NULL,
  `message_type` varchar(20) DEFAULT NULL,
  `metadata_data` json DEFAULT NULL,
  `is_edited` tinyint(1) DEFAULT NULL,
  `edited_at` datetime DEFAULT NULL,
  `reply_to_id` int DEFAULT NULL,
  `file_url` varchar(500) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `file_type` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `conversation_id` (`conversation_id`),
  KEY `reply_to_id` (`reply_to_id`),
  KEY `sender_id` (`sender_id`),
  CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  CONSTRAINT `chat_messages_ibfk_2` FOREIGN KEY (`reply_to_id`) REFERENCES `chat_messages` (`id`),
  CONSTRAINT `chat_messages_ibfk_3` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=151 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `chat_messages`
--

LOCK TABLES `chat_messages` WRITE;
/*!40000 ALTER TABLE `chat_messages` DISABLE KEYS */;
INSERT INTO `chat_messages` VALUES (24,4,11,'hello emily','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 02:17:28','2025-11-24 02:17:28'),(25,4,11,'landing','America/Los_Angeles','file','{\"file_info\": {\"size\": 899917, \"type\": \"image/png\", \"uploaded_at\": \"2025-11-24T02:18:08.303870\", \"original_name\": \"Capture_decran_2025-10-06_230716.png\"}}',0,NULL,NULL,'/api/chat/uploads/20251124_021808_11_Capture_decran_2025-10-06_230716.png','Capture_decran_2025-10-06_230716.png',899917,'image/png','2025-11-24 02:18:08','2025-11-24 02:18:08'),(26,3,11,'hello guys','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 02:19:54','2025-11-24 02:19:54'),(27,3,11,'here\'s database schema','America/Los_Angeles','file','{\"file_info\": {\"size\": 77573, \"type\": \"application/pdf\", \"uploaded_at\": \"2025-11-24T02:20:24.338693\", \"original_name\": \"Database_Schema_Design.pdf\"}}',0,NULL,NULL,'/api/chat/uploads/20251124_022024_11_Database_Schema_Design.pdf','Database_Schema_Design.pdf',77573,'application/pdf','2025-11-24 02:20:24','2025-11-24 02:20:24'),(28,3,11,'last update','America/Los_Angeles','file','{\"file_info\": {\"size\": 16549, \"type\": \"application/vnd.openxmlformats-officedocument.wordprocessingml.document\", \"uploaded_at\": \"2025-11-24T02:21:02.026498\", \"original_name\": \"checkList.docx\"}}',0,NULL,NULL,'/api/chat/uploads/20251124_022102_11_checkList.docx','checkList.docx',16549,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','2025-11-24 02:21:02','2025-11-24 02:21:02'),(31,1,11,'nice to meet you','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 06:36:09','2025-11-24 06:36:09'),(32,1,12,'hello ','America/Toronto','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 06:44:29','2025-11-24 06:44:29'),(33,4,11,'that\'s good bro','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 08:11:54','2025-11-24 08:11:54'),(34,1,13,'hello guys','Europe/Madrid','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 08:13:02','2025-11-24 08:13:02'),(35,3,13,'good job','Europe/Madrid','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 08:13:16','2025-11-24 08:13:16'),(36,4,14,'Sent a file','Europe/London','file','{\"file_info\": {\"size\": 16549, \"type\": \"application/vnd.openxmlformats-officedocument.wordprocessingml.document\", \"uploaded_at\": \"2025-11-24T08:48:53.441124\", \"original_name\": \"checkList.docx\"}}',0,NULL,NULL,'/api/chat/uploads/20251124_084853_14_checkList.docx','checkList.docx',16549,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','2025-11-24 08:48:53','2025-11-24 08:48:53'),(37,4,14,'updated content','Europe/London','file','{\"file_info\": {\"size\": 6024385, \"type\": \"application/pdf\", \"uploaded_at\": \"2025-11-24T08:49:29.209309\", \"original_name\": \"1000055985.pdf\"}}',1,'2025-11-24 08:50:48',NULL,'/api/chat/uploads/20251124_084929_14_1000055985.pdf','1000055985.pdf',6024385,'application/pdf','2025-11-24 08:49:29','2025-11-24 08:50:48'),(38,1,11,'hello','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-24 22:43:13','2025-11-24 22:43:13'),(39,1,11,'hello guys no time no seen ','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-26 05:46:14','2025-11-26 05:46:14'),(100,104,11,'meeting at 19','America/Los_Angeles','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-28 16:53:33','2025-11-28 16:53:33'),(101,115,104,'hello  from gmail','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-05 01:18:27','2025-12-05 01:18:27'),(102,115,107,'hello bro','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-05 02:23:44','2025-12-05 02:23:44'),(103,115,104,'what\'s up  with the project, is everything alrigh so what\'s going ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-05 03:11:46','2025-12-05 03:11:46'),(104,115,107,'dont forget to add this','UTC','file','{\"file_info\": {\"size\": 3894784, \"type\": \"image/gif\", \"uploaded_at\": \"2025-12-05T03:21:53.819051\", \"original_name\": \"demo.gif\"}}',0,NULL,NULL,'/api/chat/uploads/20251205_032153_107_demo.gif','demo.gif',3894784,'image/gif','2025-12-05 03:21:55','2025-12-05 03:21:55'),(105,117,107,'hello','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-05 17:35:14','2025-12-05 17:35:14'),(106,118,108,'yo','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 02:36:15','2025-12-07 02:36:15'),(107,118,104,'hello brother','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 02:36:41','2025-12-07 02:36:41'),(108,118,104,'wasup hhhhh','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 02:37:35','2025-12-07 02:37:35'),(109,119,104,'hello ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 03:13:20','2025-12-07 03:13:20'),(110,119,104,'Sent a file','UTC','file','{\"file_info\": {\"size\": 1422749, \"type\": \"image/png\", \"uploaded_at\": \"2025-12-07T03:14:50.350128\", \"original_name\": \"image-o53JuZpiN3JOy3N3lXQMLmskV0OslK.png\"}}',0,NULL,NULL,'/api/chat/uploads/20251207_031450_104_image-o53JuZpiN3JOy3N3lXQMLmskV0OslK.png','image-o53JuZpiN3JOy3N3lXQMLmskV0OslK.png',1422749,'image/png','2025-12-07 03:14:52','2025-12-07 03:14:52'),(111,121,111,'Hello','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 17:26:05','2025-12-07 17:26:05'),(112,118,104,'hello is it working?','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 19:26:08','2025-12-07 19:26:08'),(113,122,104,'hello brother\'s','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 19:28:39','2025-12-07 19:28:39'),(114,122,111,'hello','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 19:54:35','2025-12-07 19:54:35'),(115,121,111,'hey bro','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 19:54:58','2025-12-07 19:54:58'),(116,122,104,'need\'s improvements hhh','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 19:56:38','2025-12-07 19:56:38'),(117,122,111,'yeah lol','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 19:57:12','2025-12-07 19:57:12'),(118,122,104,'[21:10] \nwhat time do you see ?','UTC','text','{\"sent_at_utc\": \"2025-12-07T20:10:36.749877\", \"sender_timezone\": \"UTC\", \"has_time_placeholders\": true}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-07 20:10:38','2025-12-07 20:10:38'),(119,115,107,'hello ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-10 23:50:29','2025-12-10 23:50:29'),(120,115,104,'hello body ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-10 23:55:34','2025-12-10 23:55:34'),(121,115,107,'life is fucked up man','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 00:01:29','2025-12-11 00:01:29'),(122,115,107,'yes ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 00:05:18','2025-12-11 00:05:18'),(123,115,104,'so what are we going to do','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 00:17:57','2025-12-11 00:17:57'),(124,115,107,'probably nothing','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 00:19:15','2025-12-11 00:19:15'),(125,115,104,'fuck you we most never give up','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 00:22:37','2025-12-11 00:22:37'),(126,115,107,'hjhsxjhjnj','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 00:28:12','2025-12-11 00:28:12'),(127,115,104,'what the fuck ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 01:19:23','2025-12-11 01:19:23'),(128,115,107,'sorry brother we need to get rich or just died','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 03:01:22','2025-12-11 03:01:22'),(129,115,104,'yes','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 03:06:59','2025-12-11 03:06:59'),(130,115,107,'zedzedzed','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 03:08:44','2025-12-11 03:08:44'),(131,122,104,'aiuzduiuhd','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 18:48:09','2025-12-11 18:48:09'),(132,125,118,'hello bro','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 22:35:13','2025-12-11 22:35:13'),(133,125,104,'hello university','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-11 23:58:32','2025-12-11 23:58:32'),(134,125,118,'hello  ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:04:07','2025-12-12 00:04:07'),(135,125,118,'you won the lottery','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:06:19','2025-12-12 00:06:19'),(136,125,104,'whaaaaaaaaaaaat??','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:08:50','2025-12-12 00:08:50'),(137,125,118,'yes','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:10:01','2025-12-12 00:10:01'),(138,125,104,'no thanks','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:13:45','2025-12-12 00:13:45'),(139,125,104,'[01:30]  now','UTC','text','{\"sent_at_utc\": \"2025-12-12T00:14:15.271685\", \"sender_timezone\": \"UTC\", \"has_time_placeholders\": true}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:14:16','2025-12-12 00:14:16'),(140,125,118,'what\'s that time for?','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:52:50','2025-12-12 00:52:50'),(141,125,104,'here in Morocco','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:53:42','2025-12-12 00:53:42'),(142,125,118,'okay what\'s good now','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:55:54','2025-12-12 00:55:54'),(143,125,118,'yes','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 00:58:04','2025-12-12 00:58:04'),(144,125,118,'zedzedzedzed','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 01:01:23','2025-12-12 01:01:23'),(145,125,104,'same shit','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 01:02:20','2025-12-12 01:02:20'),(146,125,118,'why','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 01:04:20','2025-12-12 01:04:20'),(147,125,118,'fgffgf','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-12 06:35:42','2025-12-12 06:35:42'),(148,125,104,'hello [01:40] ','UTC','text','{\"sent_at_utc\": \"2025-12-13T02:17:44.012873\", \"sender_timezone\": \"UTC\", \"has_time_placeholders\": true}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-13 02:17:45','2025-12-13 02:17:45'),(149,125,118,'hi','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-14 01:33:03','2025-12-14 01:33:03'),(150,130,100,'hello ','UTC','text','{}',0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-14 05:01:52','2025-12-14 05:01:52');
/*!40000 ALTER TABLE `chat_messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conversation_participants`
--

DROP TABLE IF EXISTS `conversation_participants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conversation_participants` (
  `conversation_id` int NOT NULL,
  `user_id` int NOT NULL,
  `joined_at` datetime DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`conversation_id`,`user_id`),
  KEY `conversation_id` (`conversation_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `conversation_participants_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  CONSTRAINT `conversation_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversation_participants`
--

LOCK TABLES `conversation_participants` WRITE;
/*!40000 ALTER TABLE `conversation_participants` DISABLE KEYS */;
INSERT INTO `conversation_participants` VALUES (1,11,'2025-11-21 22:40:34','admin'),(1,12,'2025-11-21 22:40:34','member'),(1,13,'2025-11-21 22:40:34','member'),(2,11,'2025-11-22 01:40:06','admin'),(2,12,'2025-11-22 01:40:06','member'),(2,13,'2025-11-22 01:40:06','member'),(3,11,'2025-11-22 03:44:56','admin'),(3,13,'2025-11-22 03:44:56','member'),(3,14,'2025-11-22 03:44:56','member'),(3,15,'2025-11-22 03:44:56','member'),(4,11,'2025-11-22 04:39:20','admin'),(4,14,'2025-11-22 04:39:20','member'),(100,11,'2025-11-28 04:52:48','admin'),(100,12,'2025-11-28 04:52:49','member'),(100,13,'2025-11-28 04:52:50','member'),(101,11,'2025-11-28 16:52:17','admin'),(101,14,'2025-11-28 16:52:18','member'),(102,11,'2025-11-28 16:52:22','admin'),(102,14,'2025-11-28 16:52:23','member'),(103,11,'2025-11-28 16:52:28','admin'),(103,14,'2025-11-28 16:52:29','member'),(104,11,'2025-11-28 16:52:33','admin'),(104,14,'2025-11-28 16:52:34','member'),(105,11,'2025-11-28 16:52:38','admin'),(105,14,'2025-11-28 16:52:39','member'),(106,11,'2025-11-28 16:52:44','admin'),(106,14,'2025-11-28 16:52:45','member'),(107,11,'2025-11-28 16:52:49','admin'),(107,14,'2025-11-28 16:52:50','member'),(108,11,'2025-11-28 16:52:54','admin'),(108,14,'2025-11-28 16:52:55','member'),(109,11,'2025-11-28 16:53:00','admin'),(109,14,'2025-11-28 16:53:01','member'),(110,11,'2025-11-28 16:53:05','admin'),(110,14,'2025-11-28 16:53:06','member'),(111,11,'2025-11-28 16:53:10','admin'),(111,14,'2025-11-28 16:53:11','member'),(112,11,'2025-11-28 16:53:16','admin'),(112,14,'2025-11-28 16:53:17','member'),(113,11,'2025-11-28 16:53:21','admin'),(113,14,'2025-11-28 16:53:22','member'),(114,11,'2025-11-28 16:53:26','admin'),(114,14,'2025-11-28 16:53:27','member'),(115,104,'2025-12-05 01:17:42','admin'),(115,107,'2025-12-05 01:17:43','member'),(116,104,'2025-12-05 17:32:35','member'),(116,107,'2025-12-05 17:32:35','admin'),(117,105,'2025-12-05 17:34:48','member'),(117,106,'2025-12-05 17:34:49','member'),(117,107,'2025-12-05 17:34:48','admin'),(118,104,'2025-12-07 02:35:46','admin'),(118,108,'2025-12-07 02:35:47','member'),(119,104,'2025-12-07 03:12:31','admin'),(119,105,'2025-12-07 03:12:32','member'),(119,106,'2025-12-07 03:12:33','member'),(119,108,'2025-12-07 03:12:34','member'),(120,100,'2025-12-07 17:25:07','member'),(120,111,'2025-12-07 17:25:05','admin'),(121,100,'2025-12-07 17:25:10','member'),(121,111,'2025-12-07 17:25:09','admin'),(122,104,'2025-12-07 19:28:01','admin'),(122,108,'2025-12-07 19:28:02','member'),(122,111,'2025-12-07 19:28:03','member'),(123,11,'2025-12-08 18:14:28','member'),(123,108,'2025-12-08 18:14:27','admin'),(124,11,'2025-12-08 18:14:31','member'),(124,108,'2025-12-08 18:14:30','admin'),(125,104,'2025-12-11 22:34:39','member'),(125,118,'2025-12-11 22:34:38','admin'),(126,108,'2025-12-14 04:03:13','admin'),(126,109,'2025-12-14 04:03:14','member'),(127,108,'2025-12-14 04:03:14','admin'),(127,109,'2025-12-14 04:03:15','member'),(128,108,'2025-12-14 04:03:18','admin'),(128,109,'2025-12-14 04:03:19','member'),(129,108,'2025-12-14 04:03:18','admin'),(129,109,'2025-12-14 04:03:19','member'),(130,100,'2025-12-14 05:01:25','admin'),(130,104,'2025-12-14 05:01:26','member');
/*!40000 ALTER TABLE `conversation_participants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conversation_user_reads`
--

DROP TABLE IF EXISTS `conversation_user_reads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conversation_user_reads` (
  `conversation_id` int NOT NULL,
  `user_id` int NOT NULL,
  `last_read_at` datetime DEFAULT NULL,
  `unread_count` int DEFAULT NULL,
  PRIMARY KEY (`conversation_id`,`user_id`),
  KEY `conversation_id` (`conversation_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `conversation_user_reads_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  CONSTRAINT `conversation_user_reads_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversation_user_reads`
--

LOCK TABLES `conversation_user_reads` WRITE;
/*!40000 ALTER TABLE `conversation_user_reads` DISABLE KEYS */;
INSERT INTO `conversation_user_reads` VALUES (1,11,'2025-11-26 19:33:11',0),(1,12,'2025-11-24 06:43:26',3),(1,13,'2025-11-24 08:12:47',2),(2,11,'2025-11-24 08:13:24',0),(2,13,'2025-11-24 08:12:21',0),(3,11,'2025-11-24 22:38:46',0),(3,13,'2025-11-24 08:13:04',0),(3,14,'2025-11-24 10:24:44',0),(3,15,'2025-11-24 08:13:16',1),(4,11,'2025-11-28 02:41:59',0),(4,14,'2025-11-24 10:26:08',1),(104,14,'2025-11-28 16:53:33',1),(115,104,'2025-12-11 03:15:25',0),(115,107,'2025-12-11 03:07:57',0),(116,104,'2025-12-07 02:37:16',0),(116,107,'2025-12-11 02:14:10',0),(117,105,'2025-12-05 17:35:14',1),(117,106,'2025-12-05 17:35:14',1),(117,107,'2025-12-11 02:18:30',0),(118,104,'2025-12-13 06:04:17',0),(118,108,'2025-12-07 03:19:46',1),(119,104,'2025-12-12 01:17:35',0),(119,105,'2025-12-07 03:13:19',2),(119,106,'2025-12-07 03:13:20',2),(119,108,'2025-12-07 03:19:40',0),(121,100,'2025-12-07 17:26:05',2),(121,111,'2025-12-07 19:54:42',0),(122,104,'2025-12-12 00:11:13',0),(122,108,'2025-12-08 18:16:53',1),(122,111,'2025-12-07 19:56:43',2),(125,104,'2025-12-14 20:25:49',0),(125,118,'2025-12-14 20:25:57',0),(127,108,'2025-12-14 04:03:29',0),(130,104,'2025-12-14 20:45:23',0);
/*!40000 ALTER TABLE `conversation_user_reads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `goal_milestones`
--

DROP TABLE IF EXISTS `goal_milestones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `goal_milestones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `goal_id` int NOT NULL,
  `user_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `order` int DEFAULT NULL,
  `is_completed` tinyint(1) DEFAULT NULL,
  `completed_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `goal_id` (`goal_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `goal_milestones_ibfk_1` FOREIGN KEY (`goal_id`) REFERENCES `project_goals` (`id`),
  CONSTRAINT `goal_milestones_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `goal_milestones`
--

LOCK TABLES `goal_milestones` WRITE;
/*!40000 ALTER TABLE `goal_milestones` DISABLE KEYS */;
/*!40000 ALTER TABLE `goal_milestones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `growth_metrics`
--

DROP TABLE IF EXISTS `growth_metrics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `growth_metrics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startup_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `metric_type` enum('user_growth','revenue','market_share','overall') NOT NULL,
  `current_value` float DEFAULT NULL,
  `previous_value` float DEFAULT NULL,
  `growth_percentage` float DEFAULT NULL,
  `user_growth_percentage` float DEFAULT NULL,
  `revenue_amount` float DEFAULT NULL,
  `market_share_percentage` float DEFAULT NULL,
  `period_start` datetime NOT NULL,
  `period_end` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `growth_metrics_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`),
  CONSTRAINT `growth_metrics_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `growth_metrics`
--

LOCK TABLES `growth_metrics` WRITE;
/*!40000 ALTER TABLE `growth_metrics` DISABLE KEYS */;
/*!40000 ALTER TABLE `growth_metrics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `idea_bookmarks`
--

DROP TABLE IF EXISTS `idea_bookmarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `idea_bookmarks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `idea_id` int NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content_preview` text,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idea_id` (`idea_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `idea_bookmarks_ibfk_1` FOREIGN KEY (`idea_id`) REFERENCES `ideas` (`id`) ON DELETE CASCADE,
  CONSTRAINT `idea_bookmarks_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idea_bookmarks`
--

LOCK TABLES `idea_bookmarks` WRITE;
/*!40000 ALTER TABLE `idea_bookmarks` DISABLE KEYS */;
/*!40000 ALTER TABLE `idea_bookmarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `idea_comments`
--

DROP TABLE IF EXISTS `idea_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `idea_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idea_id` int NOT NULL,
  `content` text NOT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `idea_id` (`idea_id`),
  CONSTRAINT `idea_comments_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `idea_comments_ibfk_2` FOREIGN KEY (`idea_id`) REFERENCES `ideas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `idea_comments`
--

LOCK TABLES `idea_comments` WRITE;
/*!40000 ALTER TABLE `idea_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `idea_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ideas`
--

DROP TABLE IF EXISTS `ideas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ideas` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `project_details` text NOT NULL,
  `industry` varchar(100) NOT NULL,
  `stage` varchar(100) NOT NULL,
  `tags` json DEFAULT NULL,
  `privacy` enum('public','private') DEFAULT NULL,
  `creator_id` int NOT NULL,
  `creator_first_name` varchar(100) DEFAULT NULL,
  `creator_last_name` varchar(100) DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT NULL,
  `likes` int DEFAULT NULL,
  `views` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `ideas_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ideas`
--

LOCK TABLES `ideas` WRITE;
/*!40000 ALTER TABLE `ideas` DISABLE KEYS */;
INSERT INTO `ideas` VALUES (16,'AI-Powered Learning Platform for Kids','An adaptive learning platform that uses AI to personalize educational content for children based on their learning style and pace.','The platform will use machine learning algorithms to analyze student performance and adapt content difficulty. Will include gamification elements and progress tracking for parents.','Education Technology','Concept','[\"AI\", \"Education\", \"Machine Learning\", \"EdTech\", \"Children\"]','public',104,'','','active',178,779,'2025-11-01 17:07:35','2025-12-11 20:34:25'),(17,'Sustainable Vertical Farming System','A modular vertical farming system for urban environments that uses 90% less water than traditional farming.','System includes automated nutrient delivery, LED lighting optimized for plant growth, and IoT sensors for monitoring plant health. Targeting restaurants and urban communities.','Agriculture','Prototype','[\"Sustainability\", \"Agriculture\", \"Urban Farming\", \"IoT\", \"Green Tech\"]','public',104,'','','active',150,806,'2025-11-06 17:07:35','2025-12-07 06:34:36'),(18,'Blockchain-Based Digital Identity Solution','A decentralized digital identity system that gives users control over their personal data and verification credentials.','Using blockchain technology to create tamper-proof digital identities. Solution includes mobile app for identity management and API for third-party verification.','FinTech','Research','[\"Blockchain\", \"Security\", \"Digital Identity\", \"Privacy\", \"FinTech\"]','private',104,'','','active',55,349,'2025-11-11 17:07:35','2025-11-30 17:07:35'),(19,'Mental Health Companion App','An AI-powered mental health app that provides daily check-ins, coping strategies, and connects users with resources.','Features include mood tracking, guided meditation, cognitive behavioral therapy exercises, and emergency resource directory. Will use natural language processing for conversational support.','Healthcare','Planning','[\"Mental Health\", \"AI\", \"Healthcare\", \"Wellness\", \"Mobile App\"]','public',104,'','','active',87,510,'2025-11-16 17:07:35','2025-11-28 17:07:35'),(20,'Smart Waste Management System','IoT-based waste management system that optimizes collection routes and schedules based on fill levels.','Smart bins with sensors transmit fill level data to central system. Algorithm optimizes collection routes to reduce fuel consumption and operational costs.','Clean Tech','Development','[\"IoT\", \"Sustainability\", \"Smart Cities\", \"Waste Management\", \"Clean Tech\"]','public',104,'','','active',152,654,'2025-11-21 17:07:35','2025-12-01 17:07:35'),(21,'AR Interior Design Platform','Augmented Reality app that lets users visualize furniture and decor in their space before purchasing.','Users upload room dimensions or use phone camera to create AR overlay of products. Integration with furniture retailers and interior design services.','Retail Technology','Concept','[\"AR\", \"Interior Design\", \"Retail\", \"Mobile App\", \"Visualization\"]','public',104,'','','active',101,944,'2025-11-23 17:07:35','2025-11-30 17:07:35'),(22,'Remote Team Collaboration Tool','Virtual workspace designed for distributed teams with integrated project management and communication features.','Includes virtual whiteboards, task management, video conferencing, and document collaboration. Focus on reducing meeting fatigue and improving asynchronous work.','SaaS','Beta','[\"Remote Work\", \"SaaS\", \"Collaboration\", \"Productivity\", \"B2B\"]','private',104,'','','active',144,147,'2025-11-26 17:07:35','2025-12-01 17:07:35'),(23,'Plant-Based Meat Alternatives Marketplace','Online platform connecting consumers with local producers of plant-based meat alternatives.','Subscription box service and a la carte ordering. Focus on locally-sourced, sustainable plant-based proteins with transparent sourcing information.','Food Tech','Planning','[\"Food Tech\", \"Sustainability\", \"Plant-Based\", \"E-commerce\", \"Health\"]','public',104,'','','active',18,401,'2025-11-28 17:07:35','2025-12-11 01:05:04'),(24,'Renewable Energy Microgrid Controller','Smart controller for managing microgrids with mixed renewable energy sources (solar, wind, battery storage).','Uses AI to predict energy production and consumption, optimizing energy distribution and storage. Targets rural communities and commercial campuses.','Energy','Research','[\"Renewable Energy\", \"AI\", \"Smart Grid\", \"Sustainability\", \"Clean Energy\"]','public',104,'','','active',47,370,'2025-11-29 17:07:35','2025-12-01 17:07:35'),(25,'Personal Finance AI Assistant','AI-powered financial advisor that helps users with budgeting, saving, and investment decisions.','Analyzes spending patterns, suggests budgets, identifies saving opportunities, and provides personalized investment recommendations based on risk profile.','FinTech','Concept','[\"FinTech\", \"AI\", \"Personal Finance\", \"Investing\", \"Budgeting\"]','public',104,'','','active',131,545,'2025-11-30 17:07:35','2025-12-01 17:07:35');
/*!40000 ALTER TABLE `ideas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `join_requests`
--

DROP TABLE IF EXISTS `join_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `join_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startup_id` int NOT NULL,
  `startup_name` varchar(255) DEFAULT NULL,
  `user_id` int NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `message` text,
  `role` varchar(100) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `join_requests_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `join_requests_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `join_requests`
--

LOCK TABLES `join_requests` WRITE;
/*!40000 ALTER TABLE `join_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `join_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `knowledge`
--

DROP TABLE IF EXISTS `knowledge`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `title_description` text NOT NULL,
  `content_preview` text NOT NULL,
  `category` varchar(100) NOT NULL,
  `file_url` varchar(500) DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT NULL,
  `views` int DEFAULT NULL,
  `downloads` int DEFAULT NULL,
  `likes` int DEFAULT NULL,
  `image_buffer` blob,
  `image_content_type` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  CONSTRAINT `knowledge_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `knowledge`
--

LOCK TABLES `knowledge` WRITE;
/*!40000 ALTER TABLE `knowledge` DISABLE KEYS */;
/*!40000 ALTER TABLE `knowledge` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `knowledge_bookmarks`
--

DROP TABLE IF EXISTS `knowledge_bookmarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_bookmarks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `knowledge_id` int NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content_preview` text,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `knowledge_id` (`knowledge_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `knowledge_bookmarks_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE,
  CONSTRAINT `knowledge_bookmarks_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `knowledge_bookmarks`
--

LOCK TABLES `knowledge_bookmarks` WRITE;
/*!40000 ALTER TABLE `knowledge_bookmarks` DISABLE KEYS */;
/*!40000 ALTER TABLE `knowledge_bookmarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `knowledge_comments`
--

DROP TABLE IF EXISTS `knowledge_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resource_id` int NOT NULL,
  `content` text NOT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `knowledge_comments_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `knowledge_comments_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `knowledge_comments`
--

LOCK TABLES `knowledge_comments` WRITE;
/*!40000 ALTER TABLE `knowledge_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `knowledge_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `notification_type` varchar(50) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `message` text,
  `data` json DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `read_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,104,'system','Welcome to the Platform','Thank you for joining our platform! We are excited to have you here.','{\"page\": \"dashboard\", \"action\": \"welcome\"}',0,NULL,'2025-11-29 03:44:24','2025-11-29 03:44:24'),(2,104,'system','Profile Update Required','Please complete your profile information to get the most out of our platform.','{\"page\": \"profile\", \"action\": \"update_profile\"}',1,'2025-11-29 04:44:24','2025-11-29 02:44:24','2025-11-29 04:44:24'),(3,104,'suggestion','New Suggestion Available','You have a new suggestion waiting for your review.','{\"type\": \"feature\", \"status\": \"pending\", \"suggestion_id\": 456}',1,'2025-11-29 05:47:13','2025-11-29 05:14:24','2025-11-29 05:47:13'),(4,104,'suggestion','Suggestion Approved','Your suggestion \"Dark Mode Feature\" has been approved by the admin.','{\"title\": \"Dark Mode Feature\", \"status\": \"approved\", \"suggestion_id\": 123}',1,'2025-11-29 05:29:24','2025-11-29 04:59:24','2025-11-29 05:29:24'),(5,104,'system','Weekly Summary','Here is your weekly activity summary. You have been very active this week!','{\"period\": \"week\", \"activities\": 15, \"achievements\": 3}',1,'2025-11-29 05:47:10','2025-11-29 05:34:24','2025-11-29 05:47:10'),(6,104,'system','System Maintenance','Scheduled maintenance will occur this weekend. The system may be unavailable for 2 hours.','{\"duration\": \"2 hours\", \"maintenance_date\": \"2024-01-15\"}',1,'2025-11-28 03:44:24','2025-11-27 23:44:24','2025-11-28 03:44:24'),(7,104,'suggestion','Suggestion Feedback','Your suggestion needs some modifications before it can be approved.','{\"status\": \"rejected\", \"feedback\": \"Please provide more details about implementation\", \"suggestion_id\": 789}',1,'2025-11-29 00:44:24','2025-11-28 21:44:24','2025-11-29 00:44:24'),(8,104,'urgent','Security Alert','Unusual login activity detected on your account. Please review your account security.','{\"ip_address\": \"192.168.1.100\", \"alert_level\": \"high\", \"action_required\": true}',1,'2025-11-29 05:46:57','2025-11-29 05:39:24','2025-11-29 05:46:57');
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_comments`
--

DROP TABLE IF EXISTS `post_comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL,
  `content` text NOT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `post_id` (`post_id`),
  CONSTRAINT `post_comments_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `post_comments_ibfk_2` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_comments`
--

LOCK TABLES `post_comments` WRITE;
/*!40000 ALTER TABLE `post_comments` DISABLE KEYS */;
/*!40000 ALTER TABLE `post_comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_likes`
--

DROP TABLE IF EXISTS `post_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL,
  `user_id` int NOT NULL,
  `liked_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `post_likes_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `post_likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_likes`
--

LOCK TABLES `post_likes` WRITE;
/*!40000 ALTER TABLE `post_likes` DISABLE KEYS */;
/*!40000 ALTER TABLE `post_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `post_media`
--

DROP TABLE IF EXISTS `post_media`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `post_media` (
  `id` int NOT NULL AUTO_INCREMENT,
  `post_id` int NOT NULL,
  `data` blob,
  `content_type` varchar(100) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `caption` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `post_id` (`post_id`),
  CONSTRAINT `post_media_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `post_media`
--

LOCK TABLES `post_media` WRITE;
/*!40000 ALTER TABLE `post_media` DISABLE KEYS */;
/*!40000 ALTER TABLE `post_media` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `posts`
--

DROP TABLE IF EXISTS `posts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `posts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `content` text NOT NULL,
  `type` enum('professional','social','image','video') DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `likes` int DEFAULT NULL,
  `comments_count` int DEFAULT NULL,
  `shares` int DEFAULT NULL,
  `saves` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `posts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `posts`
--

LOCK TABLES `posts` WRITE;
/*!40000 ALTER TABLE `posts` DISABLE KEYS */;
/*!40000 ALTER TABLE `posts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project_goals`
--

DROP TABLE IF EXISTS `project_goals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_goals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startup_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `progress_percentage` float DEFAULT NULL,
  `milestones_completed` int DEFAULT NULL,
  `milestones_total` int DEFAULT NULL,
  `is_on_track` tinyint(1) DEFAULT NULL,
  `next_milestone` varchar(255) DEFAULT NULL,
  `target_date` datetime DEFAULT NULL,
  `completed_date` datetime DEFAULT NULL,
  `status` enum('active','completed','on_hold','cancelled') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `project_goals_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`),
  CONSTRAINT `project_goals_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `project_goals`
--

LOCK TABLES `project_goals` WRITE;
/*!40000 ALTER TABLE `project_goals` DISABLE KEYS */;
/*!40000 ALTER TABLE `project_goals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `refresh_tokens`
--

DROP TABLE IF EXISTS `refresh_tokens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `refresh_tokens` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `token` varchar(500) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `refresh_tokens_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `refresh_tokens`
--

LOCK TABLES `refresh_tokens` WRITE;
/*!40000 ALTER TABLE `refresh_tokens` DISABLE KEYS */;
INSERT INTO `refresh_tokens` VALUES (1,0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDI5NTM3OSwianRpIjoiMTA5MGZmMTItNWUwOC00NTM2LTlmN2UtNWU3N2ZmMjU0Y2U1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIwIiwibmJmIjoxNzY0Mjk1Mzc5LCJjc3JmIjoiZWFhZjg3ZjMtZmIzMC00ZWEzLWFiMjYtMDNmYTljMDExZDk0IiwiZXhwIjoxNzY2ODg3Mzc5fQ.cxyGKlrka7LsGsIzLhhVhyn4zbBflqiA_6ZYgGq2CPY','2025-11-28 02:02:59','2025-11-28 02:02:59'),(2,21,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDI5NTQ4MiwianRpIjoiZWI2NjM4NWUtNzZhZS00ODE1LWFkYzMtNDFlOWZmMTI0N2I5IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIyMSIsIm5iZiI6MTc2NDI5NTQ4MiwiY3NyZiI6IjhhZjA4NWNjLWEyNGYtNDRlZC1iYzhhLTc2NTA0OTVkMzMwZSIsImV4cCI6MTc2Njg4NzQ4Mn0.1SyaQyWulSG2Z-xC_rv1o9pdTDsxQPoiFb1vepeTXPE','2025-11-28 02:04:42','2025-11-28 02:04:42'),(4,101,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDMwMDMzMywianRpIjoiY2YwZTQ5ODktNDA4NS00NDI0LWE1Y2QtM2ViMjBjYWQxOWUzIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDEiLCJuYmYiOjE3NjQzMDAzMzMsImNzcmYiOiI1OTg1ODFiZi1lYzhmLTQ5NDUtYjUyNy1hY2M5NDg3MTY2ZjgiLCJleHAiOjE3NjY4OTIzMzN9.lryZtBB7yOdgCSD9ocgWbRT69KOC-8hC_46sGyXsYsw','2025-11-28 03:25:33','2025-11-28 03:25:33'),(11,102,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM1MzIxMiwianRpIjoiOTAxODk4OGQtNDk1My00ZTQ1LWFiYjQtNGZhNTk3MGYxMTYzIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDIiLCJuYmYiOjE3NjQzNTMyMTIsImNzcmYiOiI5YjY2Zjk4ZC1jNDJhLTQyNjUtOGUxNi01YWU2OWQzZTY4OWQiLCJleHAiOjE3NjY5NDUyMTJ9.9tjcx6EMy2f13q0hmnr5MQugQfWEkl9WsOBiG81N6Kk','2025-11-28 18:06:52','2025-11-28 18:06:52'),(13,103,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM1MzI2MywianRpIjoiNjI2NmM2OWQtODE3MC00MzNhLThkYmEtZjZmMjEyNzI2M2Q3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDMiLCJuYmYiOjE3NjQzNTMyNjMsImNzcmYiOiI5YjQyNjIwNS0zMDc2LTQxMDUtYWRmMC0xNDIyZTdlMzQ1ZTgiLCJleHAiOjE3NjY5NDUyNjN9.5AiYV_8YZ1ON8z-bFaVUN59HbcbsNl2P6U0YirmX4EM','2025-11-28 18:07:43','2025-11-28 18:07:43'),(20,105,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM2MDk1OCwianRpIjoiNWQ5YmYyZTMtNDZmNC00Y2RhLThhYTEtMDEyMDE1ZGEwMjEzIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDUiLCJuYmYiOjE3NjQzNjA5NTgsImNzcmYiOiJkM2NmMDQzZC03Mzg1LTQxODgtODVhMi02NDJiN2Q4YWZiOGMiLCJleHAiOjE3NjY5NTI5NTh9.8akyIhkXC7pqiem3LKIhfCD2SYZTea-AN5IrS7yJSwg','2025-11-28 20:15:58','2025-11-28 20:15:58'),(37,106,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDYxMTk4MSwianRpIjoiZGViYmUyNTMtNWFlNC00ODIxLWE2MjQtYmM0NzYwZTlhNDg4IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDYiLCJuYmYiOjE3NjQ2MTE5ODEsImNzcmYiOiJlMDYxZTE0OS1lZDhlLTRlYTctYThlNC0wYjBhNmYxOTFkM2QiLCJleHAiOjE3NjcyMDM5ODF9.RSf-JBZMfyPZNdlXvVu7IL9a6ESmXyfS4MVcSL8Aohk','2025-12-01 17:59:41','2025-12-01 17:59:41'),(66,109,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTA4MjkyOCwianRpIjoiODI5ZGI4ZGEtZDcyMS00ODA0LWExMTItMmUyYTNhZDhmMTI0IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDkiLCJuYmYiOjE3NjUwODI5MjgsImNzcmYiOiI5YWM3NjMxNy1jNjFlLTQ1MzMtYjhkMi04M2Y0MGM3ZWI1NTIiLCJleHAiOjE3Njc2NzQ5Mjh9.NmCk6zvQ1URlq5GPLmtqFCv4HFk2mjHxcC3I3mzrDRg','2025-12-07 04:48:49','2025-12-07 04:48:49'),(67,110,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTEyODA2OCwianRpIjoiMmFjZmI4NWYtMWU5NC00YTZjLWI1ZWQtOGRiOGFmODA3ZDc1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTAiLCJuYmYiOjE3NjUxMjgwNjgsImNzcmYiOiJiOWM4YTc0NC1hNDEyLTQ0ZTAtOGM2MS0zZjI2NzJlNzVlN2IiLCJleHAiOjE3Njc3MjAwNjh9.KgpyGqilB3fOcmq_D4knSwuT7OE3TDn5tDhiDJOCNMs','2025-12-07 17:21:09','2025-12-07 17:21:09'),(72,112,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTEzNTUwOSwianRpIjoiYTA4MDRlM2QtYzA2OC00MTBhLThjZjktOGUxNDc5MTFjYjBmIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTIiLCJuYmYiOjE3NjUxMzU1MDksImNzcmYiOiJiYjU1MTljYS02ZWRiLTQ1MTgtYTBkNi0wNWUwNjdkNjQ0ODEiLCJleHAiOjE3Njc3Mjc1MDl9.qu1Zzk64vS1RuyXXTtM5bERQYGWeYiiBYDJHxSKyYMg','2025-12-07 19:25:10','2025-12-07 19:25:10'),(73,111,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTEzNzIxNCwianRpIjoiMjdkMzZhOTktZGY0ZS00MmNkLThiODEtYTU1OWVkNDI4YzViIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTEiLCJuYmYiOjE3NjUxMzcyMTQsImNzcmYiOiI0ZTMzZTgzMy04Y2M1LTQ2OTktODFlMy1lZmMyMzY3YWE4YTciLCJleHAiOjE3Njc3MjkyMTR9.xz2nRM-m5qUF3sxy8V8ccoy2e9XtlK800_YmOjYzEW8','2025-12-07 19:53:35','2025-12-07 19:53:35'),(76,113,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTIxMDk4MywianRpIjoiZmI1NTQ5YTktODU1YS00MGVmLWE5Y2EtMDcxZDA5ZjcyOTYwIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTMiLCJuYmYiOjE3NjUyMTA5ODMsImNzcmYiOiI1YWY2ZTZhYy1kM2I0LTQ1NjYtYjAzYS01YzNiMGEyZmJlZTAiLCJleHAiOjE3Njc4MDI5ODN9.4stuC4wcLSv5EnbFqQHwthsjplDqLdV4pmz_wH8XSdc','2025-12-08 16:23:04','2025-12-08 16:23:04'),(82,114,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTI4MjUxMiwianRpIjoiN2NkMzFkZjAtNTE5Zi00M2ViLWJlOWYtMTVmMWJjYWRmOGM1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTQiLCJuYmYiOjE3NjUyODI1MTIsImNzcmYiOiI3ZjViNDA4ZC0yOGY2LTRhZjAtYjhjYy05MjI1ZTI4MmQyYjciLCJleHAiOjE3Njc4NzQ1MTJ9.sWjBGBkwlvYGwFGD5YxyNa-nBHG1iXCGn1rjCXlOjgM','2025-12-09 12:15:13','2025-12-09 12:15:13'),(83,115,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTI4Mjk4OSwianRpIjoiOGI2ODRmOWUtOGY0Ni00MDFhLWI5NDUtNGU3MDU1ZjRjZTk4IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTUiLCJuYmYiOjE3NjUyODI5ODksImNzcmYiOiI2NjM5NWVhYi0zZjg0LTQxODgtOTE1ZC00NmQ4ZGVjN2YwZDAiLCJleHAiOjE3Njc4NzQ5ODl9.UxI4_RjqCO10xF-EiOmDPYITJplB1o0vWlIrWzGo6pE','2025-12-09 12:23:09','2025-12-09 12:23:09'),(88,107,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTQxMDUwNywianRpIjoiOTA4YWFhZjItYzRhMC00ZmVhLThhOGItZGQ2NTUyMWE1YTQ3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDciLCJuYmYiOjE3NjU0MTA1MDcsImNzcmYiOiJlN2MyY2E4OS1mNDRjLTQ5YTMtYjVmNy0xNjc4M2I1NDg5MTYiLCJleHAiOjE3NjgwMDI1MDd9.6DwtPc8T1c6RMkLcKuWcewX73hkui3ZP_wJQit8roro','2025-12-10 23:48:28','2025-12-10 23:48:28'),(90,116,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTQzMDY5NSwianRpIjoiMTVkZjY0YzEtNWZiYi00NjVlLWE5YjMtM2U1ZGUyMjEwMzFmIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTYiLCJuYmYiOjE3NjU0MzA2OTUsImNzcmYiOiJhMmQ3ZTg1Yi01MzA1LTRlYjgtOGQ2MC0wMWQwZWIyM2M0YzUiLCJleHAiOjE3NjgwMjI2OTV9.nOcc2oXFg-KHHbtHUXAKZEMg_bU76DyPy7cx_Oo0JcE','2025-12-11 05:24:56','2025-12-11 05:24:56'),(93,117,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTQ5MDg1MywianRpIjoiYzJmNmVjMGYtODFiNy00ZjI3LTljZjYtYzE5ZTExMTBiMTJhIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTciLCJuYmYiOjE3NjU0OTA4NTMsImNzcmYiOiIxNjFhZTRiYy05Nzc5LTQwM2UtOTdlNS0xZDU2MGM4MjgxYjUiLCJleHAiOjE3NjgwODI4NTN9.9sT8FKma6FixLy9lpqsrDDzHttDEACULvVJSQ3ZnB_k','2025-12-11 22:07:34','2025-12-11 22:07:34'),(109,108,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTY4NDkxOSwianRpIjoiMmY5NzQ0Y2MtNThiMi00MGQ0LTg1ZGQtNjBiZDk5OWVlYTM5IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDgiLCJuYmYiOjE3NjU2ODQ5MTksImNzcmYiOiIwN2RiM2FmYS0xYWEyLTRlOTUtOTY3MC0zMmJhZmI5NzllNjciLCJleHAiOjE3NjgyNzY5MTl9.5zuF253IHzfBVxwVmad9ACk94RSbKATYwZPuO_s-OAQ','2025-12-14 04:02:00','2025-12-14 04:02:00'),(110,100,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTY4NzY1OCwianRpIjoiYWI2ZmM3NTgtYWQ5ZS00MmZlLTgyN2ItMTVkNTFmYjAzZWMyIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDAiLCJuYmYiOjE3NjU2ODc2NTgsImNzcmYiOiIwZDNkOGM5YS05MTY1LTRkNjktYTE4MS02NTBjMzRkOGU2MmUiLCJleHAiOjE3NjgyNzk2NTh9.yk8oPnwy8XWpSJd_l6wk1t8k8eJj96KqbGy7XrnnoRs','2025-12-14 04:47:39','2025-12-14 04:47:39'),(115,118,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTc3NjM2NywianRpIjoiZGE5ZDIwNDctNmVjMC00MzEyLWI0NmMtZDM4ZjFkOTY4OTc0IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMTgiLCJuYmYiOjE3NjU3NzYzNjcsImNzcmYiOiIwZGM2MGE2NS04NDc2LTQ4NzktOTlhMi1kMzEyYjg4MDY3ZDUiLCJleHAiOjE3NjgzNjgzNjd9.lzh2m1VvLo2iDe8GqzKiSFSKc42wVNeBedZCw3rDosE','2025-12-15 05:26:07','2025-12-15 05:26:07'),(116,104,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NTgyMDgyOSwianRpIjoiZTc3OTQ5YWEtNzY2Ny00ZTVlLTg1YTItMGJjODM3ZGY0YTljIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDQiLCJuYmYiOjE3NjU4MjA4MjksImNzcmYiOiJjNjM3NzY1Mi05ODhhLTRkNzEtOWQzNS1hMGI2MGFiNGI1NzEiLCJleHAiOjE3Njg0MTI4Mjl9.BN9Jd7N-JP6o6fAxs4ydkYZnpr9mQU7W8kWDMSxH5EA','2025-12-15 17:47:10','2025-12-15 17:47:10');
/*!40000 ALTER TABLE `refresh_tokens` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_downloads`
--

DROP TABLE IF EXISTS `resource_downloads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_downloads` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resource_id` int NOT NULL,
  `user_id` int NOT NULL,
  `downloaded_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `resource_id` (`resource_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `resource_downloads_ibfk_1` FOREIGN KEY (`resource_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resource_downloads_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_downloads`
--

LOCK TABLES `resource_downloads` WRITE;
/*!40000 ALTER TABLE `resource_downloads` DISABLE KEYS */;
/*!40000 ALTER TABLE `resource_downloads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_likes`
--

DROP TABLE IF EXISTS `resource_likes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_likes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resource_id` int NOT NULL,
  `user_id` int NOT NULL,
  `liked_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `resource_id` (`resource_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `resource_likes_ibfk_1` FOREIGN KEY (`resource_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resource_likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_likes`
--

LOCK TABLES `resource_likes` WRITE;
/*!40000 ALTER TABLE `resource_likes` DISABLE KEYS */;
/*!40000 ALTER TABLE `resource_likes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_views`
--

DROP TABLE IF EXISTS `resource_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_views` (
  `id` int NOT NULL AUTO_INCREMENT,
  `resource_id` int NOT NULL,
  `user_id` int NOT NULL,
  `viewed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `resource_id` (`resource_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `resource_views_ibfk_1` FOREIGN KEY (`resource_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE,
  CONSTRAINT `resource_views_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_views`
--

LOCK TABLES `resource_views` WRITE;
/*!40000 ALTER TABLE `resource_views` DISABLE KEYS */;
/*!40000 ALTER TABLE `resource_views` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `startup_bookmarks`
--

DROP TABLE IF EXISTS `startup_bookmarks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `startup_bookmarks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `startup_id` int NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content_preview` text,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `startup_bookmarks_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `startup_bookmarks_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `startup_bookmarks`
--

LOCK TABLES `startup_bookmarks` WRITE;
/*!40000 ALTER TABLE `startup_bookmarks` DISABLE KEYS */;
/*!40000 ALTER TABLE `startup_bookmarks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `startup_documents`
--

DROP TABLE IF EXISTS `startup_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `startup_documents` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startup_id` int NOT NULL,
  `filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `file_url` varchar(500) DEFAULT NULL,
  `content_type` varchar(100) NOT NULL,
  `document_type` varchar(50) DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `uploaded_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  CONSTRAINT `startup_documents_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `startup_documents`
--

LOCK TABLES `startup_documents` WRITE;
/*!40000 ALTER TABLE `startup_documents` DISABLE KEYS */;
INSERT INTO `startup_documents` VALUES (1,21,'1000055985.pdf','E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_25647868.pdf',NULL,'application/pdf','general',6024385,'2025-11-25 18:41:20'),(2,21,'checkList.docx','E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_948cbc55.docx',NULL,'application/vnd.openxmlformats-officedocument.wordprocessingml.document','general',16549,'2025-11-25 18:41:20'),(3,22,'SX.pdf','E:\\LLMs_test\\uploads\\startups\\22\\20251125_192849_d2785b85.pdf',NULL,'application/pdf','general',89974,'2025-11-25 19:28:49'),(4,23,'nice.pdf','E:\\LLMs_test\\uploads\\startups\\23\\20251125_202432_4d3f81f8_nice.pdf','/api/startups/23/documents/20251125_202432_4d3f81f8_nice.pdf','application/pdf','general',52367,'2025-11-25 20:24:32'),(5,24,'checkList.docx','E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_be06e303_checkList.docx','/startups/24/documents/20251126_184943_be06e303_checkList.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document','general',16549,'2025-11-26 18:49:43'),(6,24,'Weekly Working Hours Availability (12_11_25 - 15_11_25) - Google Forms.pdf','E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_b70ecc95_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf','/startups/24/documents/20251126_184943_b70ecc95_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf','application/pdf','general',63779,'2025-11-26 18:49:43'),(7,0,'Nouveau Microsoft Word Document (2).docx','/opt/render/project/src/uploads/startups/0/20251128_023402_6f8f1976_Nouveau_Microsoft_Word_Document_2.docx','/startups/0/documents/20251128_023402_6f8f1976_Nouveau_Microsoft_Word_Document_2.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document','general',0,'2025-11-28 02:34:02'),(8,0,'Schema For The Ai Interviewer Based On The Dashboa.pdf','/opt/render/project/src/uploads/startups/0/20251128_023403_1efe6daf_Schema_For_The_Ai_Interviewer_Based_On_The_Dashboa.pdf','/startups/0/documents/20251128_023403_1efe6daf_Schema_For_The_Ai_Interviewer_Based_On_The_Dashboa.pdf','application/pdf','general',70534,'2025-11-28 02:34:03'),(9,0,'Weekly Working Hours Availability (12_11_25 - 15_11_25) - Google Forms.pdf','/opt/render/project/src/uploads/startups/0/20251128_023403_e23d53e0_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf','/startups/0/documents/20251128_023403_e23d53e0_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf','application/pdf','general',63779,'2025-11-28 02:34:04');
/*!40000 ALTER TABLE `startup_documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `startup_members`
--

DROP TABLE IF EXISTS `startup_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `startup_members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startup_id` int NOT NULL,
  `user_id` int NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `role` enum('founder','contributor','investor','advisor','mentor','partner','admin','moderator','member','technical_lead','engineering_manager','backend_engineer','frontend_engineer','fullstack_engineer','mobile_engineer','software_architect','qa_engineer','test_automation_engineer','devops_engineer','cloud_engineer','sre','infrastructure_engineer','platform_engineer','cybersecurity_engineer','data_scientist','data_engineer','machine_learning_engineer','ai_engineer','mlops_engineer','data_analyst','ai_researcher','product_manager','product_owner','ux_designer','ui_designer','product_designer','ux_researcher','growth_engineer','growth_marketer','seo_specialist','content_strategist') DEFAULT NULL,
  `joined_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `startup_members_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`) ON DELETE CASCADE,
  CONSTRAINT `startup_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `startup_members`
--

LOCK TABLES `startup_members` WRITE;
/*!40000 ALTER TABLE `startup_members` DISABLE KEYS */;
INSERT INTO `startup_members` VALUES (1,21,11,'','','founder','2025-11-25 18:41:20',1,'2025-11-25 18:41:20','2025-11-25 18:41:20'),(2,22,11,'Oskar','Alaoui','founder','2025-11-25 19:28:49',1,'2025-11-25 19:28:49','2025-11-25 19:28:49'),(3,23,11,'Oskar','ufgyufyu','founder','2025-11-25 20:24:32',1,'2025-11-25 20:24:32','2025-11-25 20:24:32'),(4,24,11,'','','founder','2025-11-26 18:49:43',1,'2025-11-26 18:49:43','2025-11-26 18:49:43'),(5,0,100,'Mohamed','','founder','2025-11-28 02:34:04',1,'2025-11-28 02:34:04','2025-11-28 02:34:04');
/*!40000 ALTER TABLE `startup_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `startups`
--

DROP TABLE IF EXISTS `startups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `startups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `industry` varchar(100) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text,
  `stage` enum('idea','validation','early','growth','scale') DEFAULT NULL,
  `revenue` float DEFAULT NULL,
  `funding_amount` float DEFAULT NULL,
  `funding_round` varchar(50) DEFAULT NULL,
  `burn_rate` float DEFAULT NULL,
  `runway_months` int DEFAULT NULL,
  `valuation` float DEFAULT NULL,
  `financial_notes` text,
  `logo_path` varchar(500) DEFAULT NULL,
  `logo_content_type` varchar(100) DEFAULT NULL,
  `banner_path` varchar(500) DEFAULT NULL,
  `banner_content_type` varchar(100) DEFAULT NULL,
  `logo_url` varchar(500) DEFAULT NULL,
  `banner_url` varchar(500) DEFAULT NULL,
  `tech_stack` json NOT NULL,
  `positions` int DEFAULT NULL,
  `roles` json DEFAULT NULL,
  `creator_id` int NOT NULL,
  `creator_first_name` varchar(100) DEFAULT NULL,
  `creator_last_name` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `member_count` int DEFAULT NULL,
  `views` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `creator_id` (`creator_id`),
  CONSTRAINT `startups_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `startups`
--

LOCK TABLES `startups` WRITE;
/*!40000 ALTER TABLE `startups` DISABLE KEYS */;
INSERT INTO `startups` VALUES (21,'InterviewGenieAI','Manufacturing','MOROCCO ','edazdazd','idea',1000,1000,'pre-seed',1000,1,1000,'lzekjklzejdkjzed','E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_da634bd8.png','image/png','E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_6cf5cf0f.png','image/png','/startups/23/logo','/startups/23/banner','[\"JavaScript\", \"TypeScript\", \"Python\", \"React\"]',2,'{\"backend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 1}, \"frontend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 1}}',11,'','','active',1,4,'2025-11-25 18:41:20','2025-12-14 04:54:46'),(22,'SF MANAGER','Technology','MOROCCO ','azsazsaz','idea',1000,2000,'pre-seed',1000,1,1000,'erferferf','E:\\LLMs_test\\uploads\\startups\\22\\20251125_192849_1b0e0ba2.jpg','image/jpeg',NULL,'image/jpeg','/startups/23/logo','/startups/23/banner','[\"JavaScript\", \"TypeScript\", \"Python\", \"React\"]',3,'{\"backend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 2}, \"frontend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 1}}',11,'Oskar','Alaoui','active',1,4,'2025-11-25 19:28:49','2025-12-11 18:57:11'),(23,'new startup','Technology','Morocco','zertfyguhiokplhgfg','idea',1000,1000,'pre-seed',1000,1,1000,'xeyuiop;m','E:\\LLMs_test\\uploads\\startups\\23\\20251125_202431_052e644a_file_000000000a9861f5868855fffc87f260.png','image/png','E:\\LLMs_test\\uploads\\startups\\23\\20251125_202431_2f276357_Capture_decran_2025-11-05_230140.png','image/png','/startups/23/logo','/startups/23/banner','[\"JavaScript\", \"Python\"]',3,'{\"AI Engineer\": {\"roleType\": \"Full Time\", \"positionsNumber\": 3}}',11,'Oskar','ufgyufyu','active',1,430,'2025-11-25 20:24:31','2025-12-12 03:24:30'),(24,'SF COLLAB','Technology','USA','sjkhkldjklsjd','idea',2000,2000,'pre-seed',1000,1,3000,'notess','E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_5256296a_stars.png','image/png','E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_906abcb6_ChatGPT_Image_5_nov._2025_00_44_28.png','image/png','/startups/24/logo','/startups/24/banner','[\"JavaScript\", \"Angular\", \"Python\"]',6,'{\"backend\": {\"roleType\": \"Intern\", \"positionsNumber\": 2}, \"frontend \": {\"roleType\": \"Intern\", \"positionsNumber\": 4}}',104,'','','active',1,12,'2025-11-26 18:49:43','2025-12-14 04:54:02'),(25,'PatternsChange','Finance','Morocco','uhdihzdz \"Tell us more about your vision and stage\r\n\"','',4000,35000,'pre-seed',4000,2,4000,'zkladjlazjdkazd','/opt/render/project/src/uploads/startups/0/20251128_023402_e5d23a3a_file_000000000a9861f5868855fffc87f260.png','image/png','/opt/render/project/src/uploads/startups/0/20251128_023402_8a64f726_file_0000000037f46246aaeebb8a0c79b3fd.png','image/png','/startups/0/logo','/startups/0/banner','[\"JavaScript\", \"TypeScript\", \"React\"]',4,'{\"backend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 2}, \"frontend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 2}}',104,'Mohamed','','active',1,2,'2025-11-28 02:34:02','2025-11-28 14:42:34');
/*!40000 ALTER TABLE `startups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stories`
--

DROP TABLE IF EXISTS `stories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `media_url` varchar(500) NOT NULL,
  `caption` text,
  `type` enum('image','video') DEFAULT NULL,
  `views` int DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `stories_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `stories_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stories`
--

LOCK TABLES `stories` WRITE;
/*!40000 ALTER TABLE `stories` DISABLE KEYS */;
/*!40000 ALTER TABLE `stories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `story_views`
--

DROP TABLE IF EXISTS `story_views`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `story_views` (
  `id` int NOT NULL AUTO_INCREMENT,
  `story_id` int NOT NULL,
  `user_id` int NOT NULL,
  `viewed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `story_id` (`story_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `story_views_ibfk_1` FOREIGN KEY (`story_id`) REFERENCES `stories` (`id`) ON DELETE CASCADE,
  CONSTRAINT `story_views_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `story_views`
--

LOCK TABLES `story_views` WRITE;
/*!40000 ALTER TABLE `story_views` DISABLE KEYS */;
/*!40000 ALTER TABLE `story_views` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suggestions`
--

DROP TABLE IF EXISTS `suggestions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suggestions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idea_id` int NOT NULL,
  `content` text NOT NULL,
  `author_id` int NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `status` enum('pending','accepted','rejected') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `author_id` (`author_id`),
  KEY `idea_id` (`idea_id`),
  CONSTRAINT `suggestions_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  CONSTRAINT `suggestions_ibfk_2` FOREIGN KEY (`idea_id`) REFERENCES `ideas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suggestions`
--

LOCK TABLES `suggestions` WRITE;
/*!40000 ALTER TABLE `suggestions` DISABLE KEYS */;
/*!40000 ALTER TABLE `suggestions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tasks`
--

DROP TABLE IF EXISTS `tasks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `startup_id` int DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `priority` enum('low','medium','high') DEFAULT NULL,
  `status` enum('today','in_progress','completed','overdue') DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `labels` json DEFAULT NULL,
  `due_date` datetime DEFAULT NULL,
  `completed_date` datetime DEFAULT NULL,
  `estimated_hours` float DEFAULT NULL,
  `actual_hours` float DEFAULT NULL,
  `assigned_to` int DEFAULT NULL,
  `created_by` int NOT NULL,
  `is_on_time` tinyint(1) DEFAULT NULL,
  `progress_percentage` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `assigned_to` (`assigned_to`),
  KEY `created_by` (`created_by`),
  KEY `startup_id` (`startup_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `tasks_ibfk_1` FOREIGN KEY (`assigned_to`) REFERENCES `users` (`id`),
  CONSTRAINT `tasks_ibfk_2` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`),
  CONSTRAINT `tasks_ibfk_3` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`),
  CONSTRAINT `tasks_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tasks`
--

LOCK TABLES `tasks` WRITE;
/*!40000 ALTER TABLE `tasks` DISABLE KEYS */;
/*!40000 ALTER TABLE `tasks` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team_members`
--

DROP TABLE IF EXISTS `team_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team_members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `idea_id` int NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `position` varchar(255) DEFAULT NULL,
  `skills` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idea_id` (`idea_id`),
  CONSTRAINT `team_members_ibfk_1` FOREIGN KEY (`idea_id`) REFERENCES `ideas` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team_members`
--

LOCK TABLES `team_members` WRITE;
/*!40000 ALTER TABLE `team_members` DISABLE KEYS */;
INSERT INTO `team_members` VALUES (1,17,'Jane Smith','CTO','\"Python, React, AWS\"'),(2,17,'Jane Smith','CTO','\"Python, React, AWS\"');
/*!40000 ALTER TABLE `team_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team_performance`
--

DROP TABLE IF EXISTS `team_performance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team_performance` (
  `id` int NOT NULL AUTO_INCREMENT,
  `startup_id` int NOT NULL,
  `score_percentage` float DEFAULT NULL,
  `active_members` int DEFAULT NULL,
  `tasks_completed` int DEFAULT NULL,
  `productivity_level` enum('low','medium','high') DEFAULT NULL,
  `period_start` datetime NOT NULL,
  `period_end` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `startup_id` (`startup_id`),
  CONSTRAINT `team_performance_ibfk_1` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team_performance`
--

LOCK TABLES `team_performance` WRITE;
/*!40000 ALTER TABLE `team_performance` DISABLE KEYS */;
/*!40000 ALTER TABLE `team_performance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_achievements`
--

DROP TABLE IF EXISTS `user_achievements`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_achievements` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `achievement_id` int NOT NULL,
  `unlocked_at` datetime DEFAULT NULL,
  `progress_percentage` int DEFAULT NULL,
  `is_completed` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `achievement_id` (`achievement_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `user_achievements_ibfk_1` FOREIGN KEY (`achievement_id`) REFERENCES `achievements` (`id`),
  CONSTRAINT `user_achievements_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_achievements`
--

LOCK TABLES `user_achievements` WRITE;
/*!40000 ALTER TABLE `user_achievements` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_achievements` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `key` varchar(100) NOT NULL,
  `description` text,
  `category` varchar(50) DEFAULT 'General',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`),
  KEY `ix_permissions_key` (`key`),
  KEY `ix_permissions_category` (`category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` (`key`, `description`, `category`) VALUES
('app_access', 'Access to the application', 'Basic'),
('profile_edit', 'Edit own profile', 'Basic'),
('notifications_view', 'View notifications', 'Basic'),
('idea_create', 'Create ideas', 'Content'),
('idea_edit', 'Edit own ideas', 'Content'),
('knowledge_create', 'Create knowledge posts', 'Content'),
('knowledge_edit', 'Edit own knowledge posts', 'Content'),
('post_create', 'Create posts', 'Content'),
('post_edit', 'Edit own posts', 'Content'),
('startup_create', 'Create startups', 'Content'),
('startup_edit', 'Edit own startups', 'Content'),
('comment_create', 'Create comments', 'Social'),
('like_content', 'Like content', 'Social'),
('follow_users', 'Follow other users', 'Social'),
('send_messages', 'Send messages', 'Social'),
('admin', 'Full admin access', 'Administration'),
('admin_dashboard', 'Access admin dashboard', 'Administration'),
('user_management', 'Manage users', 'Administration'),
('content_moderation', 'Moderate content', 'Administration'),
('system_settings', 'Manage system settings', 'Administration'),
('chat_ai_access', 'Access AI chat features', 'AI Tools'),
('chat_ai_qwen', 'Access Qwen AI model', 'AI Tools'),
('chat_ai_gemini', 'Access Gemini AI model', 'AI Tools'),
('tools_image_generate', 'Generate images', 'Media Tools'),
('tools_image_edit', 'Edit images', 'Media Tools'),
('tools_background_remove', 'Remove image backgrounds', 'Media Tools'),
('tools_anime_convert', 'Convert images to anime style', 'Media Tools'),
('tools_pdf_sign', 'Sign PDF documents', 'Document Tools'),
('tools_pdf_edit', 'Edit PDF documents', 'Document Tools'),
('tools_logo_generate', 'Generate logos', 'Document Tools'),
('tools_business_plan', 'Create business plans', 'Document Tools');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `is_email_verified` tinyint(1) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `status` enum('active','deleted') DEFAULT NULL,
  `role` enum('founder','contributor','investor','advisor','mentor','partner','admin','moderator','member','technical_lead','engineering_manager','backend_engineer','frontend_engineer','fullstack_engineer','mobile_engineer','software_architect','qa_engineer','test_automation_engineer','devops_engineer','cloud_engineer','sre','infrastructure_engineer','platform_engineer','cybersecurity_engineer','data_scientist','data_engineer','machine_learning_engineer','ai_engineer','mlops_engineer','data_analyst','ai_researcher','product_manager','product_owner','ux_designer','ui_designer','product_designer','ux_researcher','growth_engineer','growth_marketer','seo_specialist','content_strategist') DEFAULT NULL,
  `xp_points` int DEFAULT NULL,
  `streak_days` int DEFAULT NULL,
  `last_activity_date` date DEFAULT NULL,
  `total_revenue` float DEFAULT NULL,
  `satisfaction_percentage` float DEFAULT NULL,
  `active_startups_count` int DEFAULT NULL,
  `profile_picture` varchar(500) DEFAULT NULL,
  `profile_bio` text,
  `profile_company` varchar(255) DEFAULT NULL,
  `profile_social_links` json DEFAULT NULL,
  `profile_country` varchar(100) DEFAULT NULL,
  `profile_city` varchar(100) DEFAULT NULL,
  `profile_timezone` varchar(50) DEFAULT NULL,
  `pref_email_notifications` tinyint(1) DEFAULT NULL,
  `pref_push_notifications` tinyint(1) DEFAULT NULL,
  `pref_privacy` enum('public','private') DEFAULT NULL,
  `pref_language` varchar(10) DEFAULT NULL,
  `pref_timezone` varchar(50) DEFAULT NULL,
  `pref_theme` enum('light','dark') DEFAULT NULL,
  `notif_new_comments` tinyint(1) DEFAULT NULL,
  `notif_new_likes` tinyint(1) DEFAULT NULL,
  `notif_new_suggestions` tinyint(1) DEFAULT NULL,
  `notif_join_requests` tinyint(1) DEFAULT NULL,
  `notif_approvals` tinyint(1) DEFAULT NULL,
  `notif_story_views` tinyint(1) DEFAULT NULL,
  `notif_post_engagement` tinyint(1) DEFAULT NULL,
  `notif_email_digest` enum('daily','weekly','monthly') DEFAULT NULL,
  `notif_quiet_hours_enabled` tinyint(1) DEFAULT NULL,
  `notif_quiet_hours_start` varchar(5) DEFAULT NULL,
  `notif_quiet_hours_end` varchar(5) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=119 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (11,'John','Admin','admin@startup.com','$2b$12$LQv3c1yqBWVHxkd0L8k7uO9P0tYY0tR8k8D6eB6QY8YdX7vL5sYfC',1,'2024-01-15 09:30:00','active','admin',5000,45,'2024-01-15',25000,95.5,3,'https://example.com/images/admin-profile.jpg','Experienced startup founder and mentor with 10+ years in tech industry.','TechStart Inc.','{\"github\": \"https://github.com/johnadmin\", \"twitter\": \"https://twitter.com/johnadmin\", \"linkedin\": \"https://linkedin.com/in/johnadmin\"}','United States','San Francisco','America/Los_Angeles',1,1,'public','en','America/Los_Angeles','dark',1,1,1,1,1,0,1,'daily',1,'22:00','07:00','2023-01-10 08:00:00','2024-01-15 09:30:00'),(12,'Sarah','Chen','sarah.chen@startup.com','$2b$12$K8v9c2zR.CVHxjd0M9l8vN0Q1uZZ1uS9l9E7fC7RZ9ZeY8wM6tZhD',1,'2024-01-15 10:15:00','active','founder',3200,30,'2024-01-15',15000,88.2,2,'https://example.com/images/sarah-profile.jpg','Passionate about AI and machine learning. Building the next generation of intelligent applications.','AI Innovations LLC','{\"twitter\": \"https://twitter.com/sarahchenai\", \"linkedin\": \"https://linkedin.com/in/sarahchen\"}','Canada','Toronto','America/Toronto',1,1,'public','en','America/Toronto','light',1,1,1,1,1,1,1,'weekly',0,'23:00','08:00','2023-03-15 14:20:00','2024-01-15 10:15:00'),(13,'Mike','Rodriguez','mike.rodriguez@startup.com','$2b$12$N9w0d3A.SDWJyl1N0m9wO1R2vAA2vT0m0F8gD8SA0AfZd9xN7uAiE',1,'2024-01-14 16:45:00','active','member',1800,25,'2024-01-14',8000,92,1,'https://example.com/images/mike-profile.jpg','Product manager with expertise in SaaS platforms and user experience design.','ProductLabs','{\"linkedin\": \"https://linkedin.com/in/mikerodriguez\", \"portfolio\": \"https://mikerodriguez.design\"}','Spain','Barcelona','Europe/Madrid',1,0,'','en','Europe/Madrid','light',1,0,1,0,1,0,1,'weekly',1,'21:00','07:00','2023-05-20 11:10:00','2024-01-14 16:45:00'),(14,'Emily','Watson','emily.watson@startup.com','$2b$12$P0x1e4B.TEXKzm2O1n0xP2S3wBB3wU1n1G9hE9TB1BgAe0yO8vBjF',1,'2024-01-15 08:20:00','active','',2500,60,'2024-01-15',12000,96.8,1,'https://example.com/images/emily-profile.jpg','Full-stack developer specializing in React, Node.js, and cloud architecture.','DevCraft Studios','{\"github\": \"https://github.com/emilywatson\", \"twitter\": \"https://twitter.com/emilydev\", \"linkedin\": \"https://linkedin.com/in/emilywatson\"}','United Kingdom','London','Europe/London',1,1,'public','en','Europe/London','dark',1,1,0,0,0,1,1,'',0,'22:00','08:00','2023-02-10 09:45:00','2024-01-15 08:20:00'),(15,'Alex','Kumar','alex.kumar@startup.com','$2b$12$Q1y2f5C.UFYLAn3P2o1yQ3T4xCC4xV2o2H0iF0UC2ChBf1zP9wCkG',1,'2024-01-13 14:30:00','active','',1500,15,'2024-01-13',6000,85.5,0,'https://example.com/images/alex-profile.jpg','Digital marketing expert focused on growth hacking and content strategy for tech startups.','GrowthHack Media','{\"twitter\": \"https://twitter.com/alexgrowth\", \"linkedin\": \"https://linkedin.com/in/alexkumar\", \"instagram\": \"https://instagram.com/alexkumar\"}','India','Bangalore','Asia/Kolkata',1,1,'public','en','Asia/Kolkata','light',1,1,1,1,1,1,1,'daily',1,'23:30','09:00','2023-07-05 16:20:00','2024-01-13 14:30:00'),(16,'David','Wilson','david.wilson@startup.com','$2b$12$R2z3g6D.VGZMBo4Q3p2zR4U5yDD5yW3p3I1jG1VD3DiCg2A0x1DlH',1,'2024-01-05 11:00:00','','member',800,0,'2024-01-05',3000,75,0,'https://example.com/images/david-profile.jpg','Former startup advisor taking a break from the ecosystem.',NULL,'{\"linkedin\": \"https://linkedin.com/in/davidwilson\"}','Australia','Sydney','Australia/Sydney',0,0,'private','en','Australia/Sydney','light',0,0,0,0,0,0,0,'',0,'22:00','08:00','2023-04-12 10:15:00','2024-01-10 09:00:00'),(17,'Lisa','Johnson','lisa.johnson@startup.com','$2b$12$S3a4h7E.WHAMCp5R4q3aT5V6zEE6zX4q4J2kH2WE4EjDh3B1y2EmI',0,NULL,'active','member',100,1,'2024-01-15',0,100,0,NULL,NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2024-01-15 12:00:00','2024-01-15 12:00:00'),(18,'Robert','Thompson','robert.thompson@startup.com','$2b$12$T4b5i8F.XIBNQq6S5r4bU6W7aFF7aY5r5K3lI3XF5FkEi4C2z3FnJ',1,'2024-01-14 17:20:00','active','investor',4200,90,'2024-01-14',50000,91.2,0,'https://example.com/images/robert-profile.jpg','Angel investor focused on early-stage tech startups. Always looking for innovative ideas.','Thompson Ventures','{\"twitter\": \"https://twitter.com/robthompsonvc\", \"website\": \"https://thompsonventures.com\", \"linkedin\": \"https://linkedin.com/in/robertthompson\"}','United States','New York','America/New_York',1,1,'','en','America/New_York','dark',1,0,1,1,1,0,0,'daily',1,'20:00','06:00','2022-11-08 13:45:00','2024-01-14 17:20:00'),(19,'Maria','Garcia','maria.garcia@startup.com','$2b$12$U5c6j9G.YJCOTr7T6s5cV7X8bGG8bZ6s6L4mJ4YG6GlFj5D3a4GoK',1,'2024-01-15 11:30:00','active','',1900,22,'2024-01-15',7500,89.5,1,'https://example.com/images/maria-profile.jpg','UI/UX designer passionate about creating beautiful and functional interfaces.','DesignCraft Studio','{\"behance\": \"https://behance.net/mariagarcia\", \"dribbble\": \"https://dribbble.com/mariagarcia\"}','Mexico','Mexico City','America/Mexico_City',1,1,'public','es','America/Mexico_City','light',1,1,1,0,1,1,1,'weekly',0,'23:00','08:00','2023-06-18 15:20:00','2024-01-15 11:30:00'),(20,'James','Lee','james.lee@startup.com','$2b$12$V6d7k0H.ZKDPSu8U7t6dW8Y9cHH9cA7t7M5nK5ZH7HmGk6E4b5HpL',1,'2024-01-14 13:45:00','active','',2800,40,'2024-01-14',11000,94.2,1,'https://example.com/images/james-profile.jpg','Backend developer specializing in microservices and database architecture.','CodeForge Solutions','{\"github\": \"https://github.com/jameslee\", \"linkedin\": \"https://linkedin.com/in/jameslee\"}','South Korea','Seoul','Asia/Seoul',1,0,'','ko','Asia/Seoul','dark',1,0,0,0,0,0,1,'',1,'00:00','09:00','2023-03-22 08:30:00','2024-01-14 13:45:00'),(100,'Mohamed','','mohamed311@gmail.com','scrypt:32768:8:1$k33uICRwHJuqIN7v$b575b790a096bd99a112cd1ad20b0d65c6e360da3e6983823405298c7833392102cad8c9bf370bfde137178f561e50cdce7dddfa1ece32d01fcac3b0ffa32622',1,'2025-12-14 04:47:38','active','member',0,0,'2025-12-14',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocKWikJW89KC1-jcYZqnOimQSUVKZGF-MH379Jikz1maz_33FQ=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-11-28 02:24:03','2025-12-14 04:47:38'),(101,'Aung','Marma','aungmarma582@gmail.com','scrypt:32768:8:1$id1nTJheh5PXBFwy$762ed30483c49dc808951de0e16f700cf142e7456dd1904e7d0e858cbe2f38c2b37dd5c816aa1a188771098d7c61b064197bc06b30d0071daf1fc6e5ae0e6c45',1,'2025-11-28 03:25:32','active','member',0,0,'2025-11-28',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocIXgcQroBTmAZJ-M5qWrbtW_dkLLn_u0lIirTtI9Hhl_DLGIQ=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-11-28 03:25:32','2025-11-28 03:25:33'),(102,'George ','Zaher','zahergeorge00@gmail.com','scrypt:32768:8:1$GSiGFnMKqzjwxkMX$5cbd50d1f8c10d5128ed190532865c15561e8073cb5eabde56cce1fb090458eff57777485d9432cbec2943aa955ee504f9cb86bec9b456655825ffbde083114d',0,'2025-11-28 18:06:51','active','member',0,0,'2025-11-28',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocIJ5S5u53qsbdQR9kvMH7lMnm4ZG7RkQv8FzfJgEHj82tdYBA=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-11-28 18:05:01','2025-11-28 18:06:51'),(103,'Hfxx','Cxsjbb','cxsjbbhfxx@gmail.com','scrypt:32768:8:1$dxFxvKC7maLX4pOW$1a0923b44efd17406651268c03b68dbad6f75eccfbe69702c28d48c4d049155fa012537701f5164302491667feeba098ca1e0be568d8e9ae89c315153a7bebce',1,'2025-11-28 18:07:42','active','member',0,0,'2025-11-28',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocJNiTLqthO-ybVz1IRN3c4gwyZ1235pb2QlQD2hqMIgJMskZg=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-11-28 18:06:00','2025-11-28 18:07:42'),(104,'','','885@gmail.com','scrypt:32768:8:1$dtFtQoxJz2p9D1s2$47749aad553d96e63727b4ddc2e28d45c2f24dc4a176c5fc0f549d12fb63e3ad0c0361443c0c7a2bf9e08d08b37f8332d1c514d50d22a5c0f3270f01f2f888a8',1,'2025-12-15 17:47:03','active','member',0,0,'2025-12-15',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocLnTyUMJA0bBCZzwQwoVK0ZwaKV9DSxb9OVXlR3e4EL7Eyktg=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-11-28 18:16:37','2025-12-15 17:47:06'),(105,'Krystian','','krystian09536@gmail.com','scrypt:32768:8:1$x2re4v7K1Hz5HgJB$37e7e7363dbe4b39dab239bb2d72b3861e385336ad0f370bb2b4eb49e26742ee735019555746df18f639dcf0ff27d1c5f0b3e1fd0d308010ca7ec203da880960',1,'2025-11-28 20:15:57','active','member',0,0,'2025-11-28',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocKS1J7GrRB2PgPzHrP5w9kLu6x5ne0f3fh4GMyaaLfDBrxSjQ=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-11-28 20:11:41','2025-11-28 20:15:57'),(106,'Mujib','Azeez','gbolahunazeez1305@gmail.com','scrypt:32768:8:1$paTqtjkEgsBKplMT$76a137f8e1a4eac49f45c89996d19092e65925b96f3bdf76b96c5b3583ea033572c362633aaa6f83508e3b91c3ddc3d024625a18ad886348a382a4b69cdff081',1,'2025-12-01 17:59:40','active','member',0,0,'2025-12-01',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocIxMWhBoszfjmF0SCdP5rxcywBh0nBzRgttCFuna6MMY8vFGRk=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-01 17:52:28','2025-12-01 17:59:40'),(107,'','','-code-9723@github.oauth','scrypt:32768:8:1$z2fPoGuPiBevnfno$60496e581b5637349cc2ecf48abaf4469d7ff6fcd38efee475a6cce821dd59b5a2dd5e6ad619bde08f01e90a4014973e93425d5dfc54806988fcf3a93b46d1b7',0,'2025-12-10 23:48:27','active','member',0,0,'2025-12-10',0,100,0,'https://avatars.githubusercontent.com/u/122914650?v=4',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-04 22:34:09','2025-12-10 23:48:27'),(108,'Oskar','Oskar','oskarrro777@gmail.com','scrypt:32768:8:1$6y0jAlkicXxm7V6B$60c90cb6f01def48c0ee0a98fb992f4bc85384f63d6d369020b81c234239e904a04eb8a6a3513f4992e091b62e12480da24c9158fbd601b2ff7d38d8ccde4eb3',1,'2025-12-14 04:01:59','active','member',0,0,'2025-12-14',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocK8xcYC3FE4iyrYTx5LdbVNYUpYuJc3ijkknGYUUus2vKFOHF0=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-07 02:34:14','2025-12-14 04:01:59'),(109,'Yash','Rajput','yashrajput3768@gmail.com','scrypt:32768:8:1$3QPeeufmStK81zDe$6e92441e2a23cfe944c0ff6749f586e5e75c83add925b2cf770ea76bda8ba8d599bd98b07d4083ad74410064b87a77a9b4f4f3910b0935556ee41a846707efbe',1,'2025-12-07 04:48:48','active','member',0,0,'2025-12-07',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocJSqbCKXyBM4tByAmYYHEjEMzdT4SfaTWFcnBgsDAefKzPGPQ=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-07 04:45:40','2025-12-07 04:48:48'),(110,'Arise','','arise693@gmail.com','scrypt:32768:8:1$zY2nqbI7W7APhhTL$9307acc2c2971f680c6c8caa26a3cd37f120d147521390d719c18eac0c94ebedbba9d73f383728b1457f934f718e3e9548086472d3246f229935219a5f580957',1,'2025-12-07 17:21:07','active','member',0,0,'2025-12-07',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocJKsrCGIh5IA_alMRiewkYT1m7aOmkhiTb-xFvpe7NkUz0QAg=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-07 17:21:05','2025-12-07 17:21:07'),(111,'David','Jeremiah','ohiodavid30@gmail.com','scrypt:32768:8:1$O03u4zcJTc0FGd4O$12e52672c40aa1cc7e229df2fb9739c5bc196cc739b6009f302e18117d359c638bf758dee3de5827d7c8bfe260d65f877e0913763c1e4d5e763ff0dbdd5270be',1,'2025-12-07 19:53:34','active','member',0,0,'2025-12-07',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocKHjFIxmTfvWmrY2UPOwienUKkG8oWFwCrSh3MHUAMLZ4pzl2F_=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-07 17:21:11','2025-12-07 19:53:34'),(112,'Kayraopi','08','kayraopi@gmail.com','scrypt:32768:8:1$clLLGAnaSXWerMXw$3e0bb52f7a448a9773b047e96dce195e346da15d4116372a5b785b386d9791d6c076b92c3bb8e7237a591bcb71481ff37b97ca20dad30d6b1fdcdc1dd08eb68e',1,'2025-12-07 19:25:09','active','member',0,0,'2025-12-07',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocLz0xSISqDMCMYJXlEH8dWVTblg2uoBsj48dbdw0YgjCtelObWr=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-07 19:25:08','2025-12-07 19:25:09'),(113,'Deep kumar','Patel','pateldeep555@gmail.com','scrypt:32768:8:1$lkrEboQraKOpj0bA$d905d3c222a64dc57c8c3d30451c410ebd803fa54669b82d742f4c40ceaf514bb073c93fdeb207545a48a0603c23233edd98cfb1babde473329aa96c913885c0',1,'2025-12-08 16:23:02','active','member',0,0,'2025-12-08',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocLPx43oXsr676RGO5EaVnrT5lTuOmA5vOSSeRIpomz8bfnD5eS_=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-08 16:23:00','2025-12-08 16:23:02'),(114,'Cletus','Newman','cletusnewman@gmail.com','scrypt:32768:8:1$YGr8XsTnIMeEu5IY$d8e0c5c196d16fd70ab0a36722b1f3bfc9cc656302cb0eafffba454ab414cac53c90f74316e801366bb5af141cb06cb49131f1b89190aaca5fc4985950d50b14',1,'2025-12-09 12:15:12','active','member',0,0,'2025-12-09',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocKaTjXNHEGewmaSpOo2Xvm73oI7oxOEfl_zN0Px4WJP_ldulBjN=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-09 12:13:08','2025-12-09 12:15:12'),(115,'Manglam','Pandey','manglampandey911@gmail.com','scrypt:32768:8:1$0qIgtrz7GkVQZGhR$426457c23c35145d98985e174cb1c6cd01a267f3948a06b0be427c064ff9d2757acdcaf71421d7ae7e4ffc9827079b09d163c2fb97d33d346c0177f6a4155459',1,'2025-12-09 12:23:08','active','member',0,0,'2025-12-09',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocLVWX-cEb-cs5FEoO4riIi-ErtZI6Hvh3fYvHm15sizp8UMy3U=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-09 12:23:08','2025-12-09 12:23:08'),(116,'Mr','Molian','lemangeurdepitta@gmail.com','scrypt:32768:8:1$xuOStDATkqrUuoaH$e5d4c3a17637b04a99483db5df2db057d98b6a4f096683375e2d4f6d8d1433fc07dc9f48893ef80d2b655239b8f0d7b5d7d935eab527eb8fdd500003c4783148',1,'2025-12-11 05:24:55','active','member',0,0,'2025-12-11',0,100,0,'https://lh3.googleusercontent.com/a/ACg8ocJ0pjYg3H6uVgoP2KRWjx0psCYFvM1GeMQF-1MyetoqSigJpjs6=s96-c',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-11 05:24:54','2025-12-11 05:24:55'),(117,'Ahmed','Alaoui','ahmed@gmail.com','scrypt:32768:8:1$ZA5D7ju2AJVZTL56$a94cbe8a729205370f7fc6931ef22a6b00a6983f2c495f3c3251dc8e054c0891ed3db9a1e73fbb0e1c25cfbba2dfbc1d761ab8377883fd84f004e4d9b28bfb85',0,NULL,'active','member',0,0,NULL,0,100,0,NULL,NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-11 22:07:33','2025-12-11 22:07:33'),(118,'University','6','universallearn.2024@gmail.com','scrypt:32768:8:1$uXR6h3AwMm89CWEY$22a244614cb6e22033ff25c7674e6db913006148737e5912393a6ca2915c2e4dd481fe1f1548d2b05f2f882a206f3789d98e61bd66280f3c1a4de4c2d1f56531',0,'2025-12-15 05:26:07','active','member',0,0,'2025-12-15',0,100,0,'/api/users/uploads/20251215_052458_118_Gemini_Generated_Image_azbwe3azbwe3azbw.png',NULL,NULL,'{}',NULL,NULL,NULL,1,1,'public','en','UTC','light',1,1,1,1,1,1,1,'weekly',0,'22:00','08:00','2025-12-11 22:15:46','2025-12-15 05:26:07');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

--
-- Table structure for table `user_permissions`
--

DROP TABLE IF EXISTS `user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  `granted_by` int DEFAULT NULL,
  `starts_at` datetime DEFAULT NULL,
  `expires_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_permission` (`user_id`,`permission_id`),
  KEY `idx_user_permissions_user_id` (`user_id`),
  KEY `idx_user_permissions_permission_id` (`permission_id`),
  KEY `idx_user_permissions_expires` (`expires_at`),
  KEY `idx_user_permissions_active` (`user_id`,`permission_id`,`expires_at`),
  CONSTRAINT `fk_user_permissions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_permissions_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_permissions_granted_by` FOREIGN KEY (`granted_by`) REFERENCES `users` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_permissions`
--

LOCK TABLES `user_permissions` WRITE;
/*!40000 ALTER TABLE `user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `access_requests`
--

DROP TABLE IF EXISTS `access_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `access_requests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `reason` text,
  `reviewed_by` int DEFAULT NULL,
  `reviewed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_access_requests_user_id` (`user_id`),
  KEY `idx_access_requests_permission_id` (`permission_id`),
  KEY `idx_access_requests_status` (`status`),
  CONSTRAINT `fk_access_requests_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_access_requests_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_access_requests_reviewed_by` FOREIGN KEY (`reviewed_by`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `access_requests`
--

LOCK TABLES `access_requests` WRITE;
/*!40000 ALTER TABLE `access_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `access_requests` ENABLE KEYS */;
UNLOCK TABLES;

-- Dump completed on 2025-12-15 20:46:17
