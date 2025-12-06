-- phpMyAdmin SQL Dump
-- version 4.7.1
-- https://www.phpmyadmin.net/
--
-- Hôte : sql7.freesqldatabase.com
-- Généré le :  lun. 01 déc. 2025 à 22:31
-- Version du serveur :  5.5.62-0ubuntu0.14.04.1
-- Version de PHP :  7.0.33-0ubuntu0.16.04.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `sql7809695`
--

-- --------------------------------------------------------

--
-- Structure de la table `achievements`
--

CREATE TABLE IF NOT EXISTS `achievements` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `icon` varchar(100) DEFAULT NULL,
  `category` enum('task','social','learning','milestone') DEFAULT NULL,
  `points` int(11) DEFAULT NULL,
  `requirement_type` varchar(50) DEFAULT NULL,
  `requirement_value` int(11) DEFAULT NULL,
  `badge_color` varchar(20) DEFAULT NULL,
  `rarity` enum('common','rare','epic','legendary') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `achievements`
--

INSERT INTO `achievements` (`id`, `title`, `description`, `icon`, `category`, `points`, `requirement_type`, `requirement_value`, `badge_color`, `rarity`, `created_at`) VALUES
(100, 'First Idea', 'Create your first business idea', '💡', 'milestone', 100, 'ideas_created', 1, NULL, 'common', NULL),
(101, 'Idea Machine', 'Create 10 business ideas', '🚀', 'milestone', 500, 'ideas_created', 10, NULL, 'rare', NULL),
(102, 'Idea Factory', 'Create 50 business ideas', '🏭', 'milestone', 1000, 'ideas_created', 50, NULL, 'epic', NULL),
(103, 'Idea Visionary', 'Create 100 business ideas', '🔭', 'milestone', 2500, 'ideas_created', 100, NULL, 'legendary', NULL),
(104, 'First Task', 'Complete your first task', '☑️', 'milestone', 50, 'tasks_completed', 1, NULL, 'common', NULL),
(105, 'Task Master', 'Complete 50 tasks', '✅', 'milestone', 300, 'tasks_completed', 50, NULL, 'rare', NULL),
(106, 'Productivity Guru', 'Complete 200 tasks', '⚡', 'milestone', 800, 'tasks_completed', 200, NULL, 'epic', NULL),
(107, 'Task Titan', 'Complete 500 tasks', '🏆', 'milestone', 2000, 'tasks_completed', 500, NULL, 'legendary', NULL),
(108, '7-Day Streak', 'Maintain a 7-day activity streak', '🔥', 'milestone', 150, 'streak_days', 7, NULL, 'common', NULL),
(109, 'Month of Momentum', 'Maintain a 30-day activity streak', '📅', 'milestone', 500, 'streak_days', 30, NULL, 'rare', NULL),
(110, 'Dedicated Developer', 'Maintain a 90-day activity streak', '💪', 'milestone', 1500, 'streak_days', 90, NULL, 'epic', NULL),
(111, 'Unstoppable Force', 'Maintain a 365-day activity streak', '🌟', 'milestone', 5000, 'streak_days', 365, NULL, 'legendary', NULL),
(112, 'First Comment', 'Make your first comment', '💬', 'social', 50, 'comments_made', 1, NULL, 'common', NULL),
(113, 'Comment Contributor', 'Make 25 comments on ideas', '💬', 'social', 200, 'comments_made', 25, NULL, 'common', NULL),
(114, 'Active Commenter', 'Make 100 comments', '🗣️', 'social', 500, 'comments_made', 100, NULL, 'rare', NULL),
(115, 'Discussion Leader', 'Make 500 comments', '👑', 'social', 1200, 'comments_made', 500, NULL, 'epic', NULL),
(116, 'First Like', 'Receive your first like', '👍', 'social', 25, 'likes_received', 1, NULL, 'common', NULL),
(117, 'Popular Idea', 'Get 100 likes on your ideas', '❤️', 'social', 400, 'likes_received', 100, NULL, 'epic', NULL),
(118, 'Community Favorite', 'Get 500 likes on your ideas', '⭐', 'social', 1000, 'likes_received', 500, NULL, 'epic', NULL),
(119, 'Internet Sensation', 'Get 1000 likes on your ideas', '🌐', 'social', 2500, 'likes_received', 1000, NULL, 'legendary', NULL),
(120, 'First Follower', 'Gain your first follower', '👥', 'social', 100, 'followers_gained', 1, NULL, 'common', NULL),
(121, 'Growing Audience', 'Gain 10 followers', '📈', 'social', 300, 'followers_gained', 10, NULL, 'common', NULL),
(122, 'Influencer', 'Gain 50 followers', '📢', 'social', 800, 'followers_gained', 50, NULL, 'rare', NULL),
(123, 'Thought Leader', 'Gain 200 followers', '🎯', 'social', 2000, 'followers_gained', 200, NULL, 'epic', NULL),
(124, 'Early Bird', 'Complete a task before its due date', '🐦', 'task', 75, 'tasks_completed_early', 1, NULL, 'common', NULL),
(125, 'Time Manager', 'Complete 25 tasks early', '⏰', 'task', 400, 'tasks_completed_early', 25, NULL, 'rare', NULL),
(126, 'Last Minute Hero', 'Complete a task on the due date', '🦸', 'task', 50, 'tasks_completed_on_time', 1, NULL, 'common', NULL),
(127, 'Perfect Timing', 'Complete 50 tasks on their due date', '🎯', 'task', 600, 'tasks_completed_on_time', 50, NULL, 'rare', NULL),
(128, 'Task Explorer', 'Create tasks in 5 different categories', '🧭', 'task', 200, 'task_categories_used', 5, NULL, 'common', NULL),
(129, 'Organized Mind', 'Create tasks in 10 different categories', '🗂️', 'task', 500, 'task_categories_used', 10, NULL, 'rare', NULL),
(130, 'Detailed Thinker', 'Create an idea with 500+ characters', '📝', '', 150, 'detailed_ideas', 1, NULL, 'common', NULL),
(131, 'Thorough Planner', 'Create 10 detailed ideas', '📋', '', 600, 'detailed_ideas', 10, NULL, 'rare', NULL),
(132, 'Idea Architect', 'Create an idea with attached documents', '🏗️', '', 200, 'ideas_with_attachments', 1, NULL, 'common', NULL),
(133, 'Resourceful Creator', 'Create 20 ideas with attachments', '📎', '', 800, 'ideas_with_attachments', 20, NULL, 'rare', NULL),
(134, 'Team Player', 'Collaborate on 5 different ideas', '🤝', '', 300, 'ideas_collaborated', 5, NULL, 'common', NULL),
(135, 'Idea Partner', 'Collaborate on 20 different ideas', '👥', '', 800, 'ideas_collaborated', 20, NULL, 'rare', NULL),
(136, 'Master Collaborator', 'Collaborate on 50 different ideas', '🌟', '', 2000, 'ideas_collaborated', 50, NULL, 'epic', NULL),
(137, 'Helpful Mentor', 'Get 10 helpful votes on your comments', '💡', '', 400, 'helpful_votes_received', 10, NULL, 'rare', NULL),
(138, 'Weekend Warrior', 'Complete tasks on 5 different weekends', '🎪', '', 300, 'weekend_activities', 5, NULL, 'rare', NULL),
(139, 'Night Owl', 'Create ideas between 10 PM and 2 AM', '🦉', '', 250, 'late_night_activities', 5, NULL, 'rare', NULL),
(140, 'Early Riser', 'Create ideas between 5 AM and 8 AM', '🌅', '', 250, 'early_morning_activities', 5, NULL, 'rare', NULL),
(141, 'Platform Explorer', 'Use all major platform features', '🧩', '', 400, 'features_used', 10, NULL, 'rare', NULL),
(142, 'Power User', 'Use platform for 30 consecutive days', '⚡', '', 600, 'consecutive_days_used', 30, NULL, 'epic', NULL),
(143, 'Platform Veteran', 'Use platform for 180 days total', '🛡️', '', 1500, 'total_days_used', 180, NULL, 'epic', NULL),
(144, 'Creative Spark', 'Create ideas in 3 different categories', '🎨', '', 200, 'idea_categories_used', 3, NULL, 'common', NULL),
(145, 'Diverse Thinker', 'Create ideas in 10 different categories', '🌈', '', 700, 'idea_categories_used', 10, NULL, 'rare', NULL),
(146, 'Innovation Master', 'Create ideas in 20 different categories', '💎', '', 1500, 'idea_categories_used', 20, NULL, 'epic', NULL),
(147, 'First Share', 'Share your first idea externally', '📤', 'social', 100, 'ideas_shared', 1, NULL, 'common', NULL),
(148, 'Social Butterfly', 'Share 25 ideas externally', '🦋', 'social', 500, 'ideas_shared', 25, NULL, 'rare', NULL),
(149, 'Bookworm', 'Read 50 idea descriptions completely', '📚', '', 300, 'ideas_read_completely', 50, NULL, 'common', NULL),
(150, 'Knowledge Seeker', 'Read 200 idea descriptions completely', '🔍', '', 800, 'ideas_read_completely', 200, NULL, 'rare', NULL),
(151, 'Feedback Provider', 'Give feedback on 10 different ideas', '📝', '', 400, 'feedbacks_given', 10, NULL, 'common', NULL),
(152, 'Constructive Critic', 'Give feedback on 50 different ideas', '🏗️', '', 1000, 'feedbacks_given', 50, NULL, 'rare', NULL),
(153, 'Idea Refiner', 'Update and improve 10 existing ideas', '✨', '', 500, 'ideas_improved', 10, NULL, 'rare', NULL),
(154, 'Perfectionist', 'Update and improve 50 existing ideas', '🎭', '', 1200, 'ideas_improved', 50, NULL, 'epic', NULL),
(155, 'Mobile User', 'Use the platform on mobile device', '📱', '', 100, 'mobile_sessions', 1, NULL, 'common', NULL),
(156, 'On-the-Go', 'Use platform on mobile 50 times', '🚶', '', 400, 'mobile_sessions', 50, NULL, 'rare', NULL),
(157, 'Desktop Commander', 'Use platform on desktop 100 times', '💻', '', 500, 'desktop_sessions', 100, NULL, 'rare', NULL),
(158, 'Multi-Platform', 'Use platform on 3 different devices', '🔄', '', 300, 'devices_used', 3, NULL, 'common', NULL),
(159, 'Seasoned Veteran', 'Use platform for 1 year', '🎂', 'milestone', 1000, 'account_age_days', 365, NULL, 'epic', NULL),
(160, 'Long-term Visionary', 'Use platform for 2 years', '⌛', 'milestone', 2500, 'account_age_days', 730, NULL, 'legendary', NULL),
(161, 'Idea Collector', 'Save 20 ideas to your favorites', '⭐', '', 300, 'ideas_saved', 20, NULL, 'common', NULL),
(162, 'Curator', 'Save 100 ideas to your favorites', '🏛️', '', 800, 'ideas_saved', 100, NULL, 'rare', NULL),
(163, 'Archivist', 'Save 500 ideas to your favorites', '📚', '', 2000, 'ideas_saved', 500, NULL, 'epic', NULL),
(164, 'Tag Master', 'Use 50 different tags on ideas', '🏷️', '', 400, 'unique_tags_used', 50, NULL, 'rare', NULL),
(165, 'Organized Mind', 'Create 10 custom categories', '🗃️', '', 500, 'custom_categories_created', 10, NULL, 'rare', NULL),
(166, 'Template Creator', 'Create 5 idea templates', '📄', '', 600, 'templates_created', 5, NULL, 'epic', NULL),
(167, 'Quick Draw', 'Complete a task within 1 hour of creating it', '⚡', 'task', 150, 'quick_tasks_completed', 1, NULL, 'common', NULL),
(168, 'Speed Demon', 'Complete 20 tasks within 1 hour', '🎯', 'task', 600, 'quick_tasks_completed', 20, NULL, 'rare', NULL),
(169, 'Weekly Regular', 'Use platform 4 weeks in a row', '📆', '', 300, 'consecutive_weeks', 4, NULL, 'common', NULL),
(170, 'Monthly Champion', 'Use platform 6 months in a row', '🏅', '', 1000, 'consecutive_months', 6, NULL, 'epic', NULL),
(171, 'Welcome Committee', 'Welcome 10 new users', '👋', '', 400, 'new_users_welcomed', 10, NULL, 'rare', NULL),
(172, 'Community Builder', 'Welcome 50 new users', '🏘️', '', 1200, 'new_users_welcomed', 50, NULL, 'epic', NULL),
(173, 'Quick Learner', 'Complete the platform tutorial', '🎓', 'learning', 200, 'tutorial_completed', 1, NULL, 'common', NULL),
(174, 'Feature Expert', 'Use all advanced features', '🧠', 'learning', 800, 'advanced_features_used', 10, NULL, 'epic', NULL),
(175, 'New Year Innovator', 'Create an idea on January 1st', '🎆', '', 250, 'new_years_idea', 1, NULL, 'rare', NULL),
(176, 'Summer Thinker', 'Create ideas during summer months', '☀️', '', 300, 'summer_ideas', 5, NULL, 'common', NULL),
(177, 'Challenge Accepted', 'Participate in your first challenge', '🎪', '', 200, 'challenges_participated', 1, NULL, 'common', NULL),
(178, 'Challenge Champion', 'Win 5 challenges', '🏆', '', 1500, 'challenges_won', 5, NULL, 'epic', NULL),
(179, 'Level Up', 'Reach level 10', '⬆️', '', 500, 'user_level', 10, NULL, 'common', NULL),
(180, 'Master Level', 'Reach level 50', '🎯', '', 2000, 'user_level', 50, NULL, 'epic', NULL),
(181, 'Achievement Hunter', 'Earn 50 different achievements', '🏹', '', 1000, 'achievements_earned', 50, NULL, 'rare', NULL),
(182, 'Completionist', 'Earn 100 different achievements', '💯', '', 3000, 'achievements_earned', 100, NULL, 'legendary', NULL),
(183, 'First Project', 'Create your first project', '📁', 'milestone', 150, 'projects_created', 1, NULL, 'common', NULL),
(184, 'Project Manager', 'Create 10 projects', '👨‍💼', 'milestone', 600, 'projects_created', 10, NULL, 'rare', NULL),
(185, 'Portfolio Builder', 'Create 25 projects', '💼', 'milestone', 1200, 'projects_created', 25, NULL, 'epic', NULL),
(186, 'Enterprise Architect', 'Create 50 projects', '🏢', 'milestone', 2500, 'projects_created', 50, NULL, 'legendary', NULL),
(187, 'Task Streak', 'Complete tasks for 7 days straight', '📊', 'task', 400, 'task_streak_days', 7, NULL, 'rare', NULL),
(188, 'Task Marathon', 'Complete tasks for 30 days straight', '🏃', 'task', 1000, 'task_streak_days', 30, NULL, 'epic', NULL),
(189, 'Priority Handler', 'Complete 20 high priority tasks', '🔴', 'task', 500, 'high_priority_tasks', 20, NULL, 'rare', NULL),
(190, 'Urgent Expert', 'Complete 50 urgent tasks', '🚨', 'task', 1200, 'urgent_tasks', 50, NULL, 'epic', NULL),
(191, 'Like Giver', 'Like 50 different ideas', '👍', 'social', 300, 'likes_given', 50, NULL, 'common', NULL),
(192, 'Supportive Member', 'Like 200 different ideas', '💝', 'social', 800, 'likes_given', 200, NULL, 'rare', NULL),
(193, 'Community Pillar', 'Like 500 different ideas', '🏛️', 'social', 1500, 'likes_given', 500, NULL, 'epic', NULL),
(194, 'Following Active', 'Follow 20 other users', '👀', 'social', 300, 'users_followed', 20, NULL, 'common', NULL),
(195, 'Network Builder', 'Follow 50 other users', '🕸️', 'social', 700, 'users_followed', 50, NULL, 'rare', NULL),
(196, 'Well Structured', 'Create idea with multiple sections', '📑', '', 200, 'structured_ideas', 1, NULL, 'common', NULL),
(197, 'Detailed Planner', 'Create 15 well-structured ideas', '📋', '', 600, 'structured_ideas', 15, NULL, 'rare', NULL),
(198, 'Research Expert', 'Add research to 10 ideas', '🔬', '', 800, 'researched_ideas', 10, NULL, 'epic', NULL),
(199, 'Market Analyst', 'Conduct market research for 5 ideas', '📊', '', 1000, 'market_researched_ideas', 5, NULL, 'epic', NULL),
(200, 'Team Builder', 'Invite 5 users to collaborate', '👥', '', 400, 'collaborators_invited', 5, NULL, 'common', NULL),
(201, 'Collaboration Champion', 'Invite 20 users to collaborate', '🤝', '', 1000, 'collaborators_invited', 20, NULL, 'rare', NULL),
(202, 'Feedback Receiver', 'Receive feedback on 10 ideas', '📥', '', 300, 'feedbacks_received', 10, NULL, 'common', NULL),
(203, 'Open to Feedback', 'Receive feedback on 50 ideas', '🎁', '', 800, 'feedbacks_received', 50, NULL, 'rare', NULL),
(204, 'Settings Explorer', 'Customize your profile settings', '⚙️', '', 100, 'settings_customized', 1, NULL, 'common', NULL),
(205, 'Profile Perfect', 'Complete your profile 100%', '👤', '', 300, 'profile_completed', 1, NULL, 'common', NULL),
(206, 'Notification Master', 'Configure all notification settings', '🔔', '', 200, 'notifications_configured', 1, NULL, 'common', NULL),
(207, 'Theme Customizer', 'Change your theme', '🎨', '', 150, 'theme_changed', 1, NULL, 'common', NULL),
(208, 'Brainstormer', 'Create 5 ideas in one day', '🌪️', '', 400, 'ideas_in_one_day', 5, NULL, 'rare', NULL),
(209, 'Idea Storm', 'Create 10 ideas in one day', '⛈️', '', 1000, 'ideas_in_one_day', 10, NULL, 'epic', NULL),
(210, 'Creative Flow', 'Create ideas for 5 days straight', '🌊', '', 600, 'creative_streak_days', 5, NULL, 'rare', NULL),
(211, 'Inspiration Wave', 'Create ideas for 14 days straight', '🌀', '', 1500, 'creative_streak_days', 14, NULL, 'epic', NULL),
(212, 'Category Expert', 'Use 10 different categories', '📂', '', 400, 'categories_used', 10, NULL, 'common', NULL),
(213, 'Tag Innovator', 'Create 10 custom tags', '🏷️', '', 300, 'custom_tags_created', 10, NULL, 'common', NULL),
(214, 'Folder Organizer', 'Organize ideas into folders', '📁', '', 200, 'folders_created', 1, NULL, 'common', NULL),
(215, 'System Architect', 'Create complex organization system', '🏗️', '', 800, 'organization_systems', 1, NULL, 'epic', NULL),
(216, 'Daily Visitor', 'Visit platform for 10 consecutive days', '📅', '', 300, 'consecutive_visits', 10, NULL, 'common', NULL),
(217, 'Loyal User', 'Visit platform for 30 consecutive days', '💝', '', 800, 'consecutive_visits', 30, NULL, 'rare', NULL),
(218, 'Platform Advocate', 'Refer 5 friends to the platform', '📢', '', 500, 'friends_referred', 5, NULL, 'rare', NULL),
(219, 'Community Ambassador', 'Refer 20 friends to the platform', '🎓', '', 1500, 'friends_referred', 20, NULL, 'epic', NULL),
(220, 'Holiday Creator', 'Create idea on a holiday', '🎄', '', 300, 'holiday_ideas', 1, NULL, 'rare', NULL),
(221, 'Birthday Idea', 'Create idea on your birthday', '🎂', '', 400, 'birthday_ideas', 1, NULL, 'rare', NULL),
(222, 'Anniversary User', 'Use platform on account anniversary', '🎉', '', 500, 'anniversary_activities', 1, NULL, 'epic', NULL),
(223, 'Challenge Regular', 'Participate in 10 challenges', '🎪', '', 600, 'challenges_participated', 10, NULL, 'rare', NULL),
(224, 'Challenge Expert', 'Participate in 25 challenges', '🏅', '', 1200, 'challenges_participated', 25, NULL, 'epic', NULL),
(225, 'Top Performer', 'Finish in top 3 of a challenge', '🥇', '', 800, 'top_3_finishes', 1, NULL, 'epic', NULL),
(226, 'Challenge Dominator', 'Finish in top 3 of 10 challenges', '👑', '', 2500, 'top_3_finishes', 10, NULL, 'legendary', NULL),
(227, 'Rising Star', 'Reach level 5', '⭐', '', 200, 'user_level', 5, NULL, 'common', NULL),
(228, 'Experienced User', 'Reach level 20', '🎯', '', 800, 'user_level', 20, NULL, 'rare', NULL),
(229, 'Veteran User', 'Reach level 75', '🛡️', '', 3000, 'user_level', 75, NULL, 'legendary', NULL),
(230, 'Max Level', 'Reach maximum level', '🏔️', '', 5000, 'user_level', 100, NULL, 'legendary', NULL),
(231, 'Trophy Collector', 'Earn 10 rare achievements', '🏆', '', 800, 'rare_achievements', 10, NULL, 'rare', NULL),
(232, 'Epic Collector', 'Earn 5 epic achievements', '💎', '', 1200, 'epic_achievements', 5, NULL, 'epic', NULL),
(233, 'Legendary Collector', 'Earn 3 legendary achievements', '🌟', '', 2000, 'legendary_achievements', 3, NULL, 'legendary', NULL),
(234, 'Achievement Master', 'Earn all common achievements', '🎓', '', 1500, 'common_achievements_all', 1, NULL, 'epic', NULL);

-- --------------------------------------------------------

--
-- Structure de la table `alembic_version`
--

CREATE TABLE IF NOT EXISTS `alembic_version` (
  `version_num` varchar(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `alembic_version`
--

INSERT INTO `alembic_version` (`version_num`) VALUES
('d659945d25c6');

-- --------------------------------------------------------

--
-- Structure de la table `calendar_events`
--

CREATE TABLE IF NOT EXISTS `calendar_events` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `startup_id` int(11) DEFAULT NULL,
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
  `reminder_minutes` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `calendar_events`
--

INSERT INTO `calendar_events` (`id`, `user_id`, `startup_id`, `title`, `description`, `start_date`, `end_date`, `all_day`, `category`, `color`, `location`, `is_recurring`, `recurrence_rule`, `reminder_minutes`, `created_at`, `updated_at`) VALUES
(1, 104, 24, 'Weekly Team Sync', 'Weekly team meeting to discuss progress, blockers, and priorities for the upcoming week.', '2025-11-10 10:00:00', '2025-11-10 11:00:00', 0, 'meeting', '#3B82F6', 'Zoom: https://zoom.us/j/123456789', 1, 'FREQ=WEEKLY;BYDAY=MO', 15, '2025-11-01 17:20:56', '2025-11-01 17:20:56'),
(2, 104, 24, 'Investor Pitch Practice', 'Practice session for upcoming investor pitch. Focus on demo flow and Q&A.', '2025-11-17 14:00:00', '2025-11-17 16:00:00', 0, 'meeting', '#8B5CF6', 'Conference Room A', 0, NULL, 30, '2025-11-06 17:20:56', '2025-11-06 17:20:56'),
(3, 104, 24, 'Beta Launch Deadline', 'Soft launch of beta version to first 100 users.', '2025-11-24 00:00:00', NULL, 1, 'deadline', '#EF4444', NULL, 0, NULL, 60, '2025-11-11 17:20:56', '2025-11-26 17:20:56'),
(4, 104, 24, 'Tech Innovation Summit', 'Annual tech conference. Network with potential partners and investors.', '2025-12-06 09:00:00', '2025-12-06 18:00:00', 0, 'event', '#10B981', 'Convention Center, Main Hall', 0, NULL, 60, '2025-11-16 17:20:56', '2025-12-01 17:20:56'),
(5, 104, 24, 'Co-founder Sync', 'Weekly sync with co-founder to discuss strategy and operational items.', '2025-11-17 16:00:00', '2025-11-17 17:00:00', 0, 'meeting', '#F59E0B', 'Co-working Space', 1, 'FREQ=WEEKLY;BYDAY=WE', 10, '2025-11-03 17:20:56', '2025-11-03 17:20:56'),
(6, 104, 24, 'Customer Feedback Session', 'User testing session with 5 beta customers to gather feedback on new features.', '2025-12-03 13:00:00', '2025-12-03 15:00:00', 0, 'meeting', '#06B6D4', 'User Testing Lab', 0, NULL, 15, '2025-11-21 17:20:56', '2025-11-29 17:20:56'),
(7, 104, 24, 'Q3 Roadmap Review', 'Quarterly product roadmap review with the product team.', '2025-12-08 11:00:00', '2025-12-08 13:00:00', 0, 'meeting', '#8B5CF6', 'Product War Room', 0, NULL, 30, '2025-11-23 17:20:56', '2025-12-01 17:20:56'),
(8, 104, 24, 'Startup Anniversary', 'Celebrating 1 year since founding! Team lunch and retrospective.', '2025-12-11 00:00:00', NULL, 1, 'event', '#EC4899', 'Office & Nearby Restaurant', 0, NULL, 1440, '2025-11-26 17:20:56', '2025-12-01 17:20:56'),
(9, 104, 24, 'VC Firm Meeting', 'Meeting with potential investors from Sequoia Capital.', '2025-12-04 15:00:00', '2025-12-04 16:30:00', 0, 'meeting', '#6366F1', 'VC Office - Downtown', 0, NULL, 60, '2025-11-24 17:20:56', '2025-12-01 17:20:56'),
(10, 104, 24, 'Sprint Planning Session', 'Two-week sprint planning with engineering and product teams.', '2025-12-02 09:30:00', '2025-12-02 12:00:00', 0, 'meeting', '#059669', 'Engineering Hub', 1, 'FREQ=WEEKLY;INTERVAL=2;BYDAY=FR', 10, '2025-11-17 17:20:56', '2025-11-28 17:20:56'),
(11, 104, 24, 'Team Building: Escape Room', 'Monthly team building activity to boost morale and collaboration.', '2025-12-08 17:00:00', '2025-12-08 20:00:00', 0, 'event', '#F97316', 'Escape Room Downtown', 1, 'FREQ=MONTHLY;BYDAY=3FR', 60, '2025-11-19 17:20:56', '2025-12-01 17:20:56'),
(12, 104, 24, 'New Feature Launch', 'Launch of AI-powered recommendation engine feature.', '2025-12-15 00:00:00', NULL, 1, 'reminder', '#84CC16', NULL, 0, NULL, 1440, '2025-11-25 17:20:56', '2025-12-01 17:20:56'),
(13, 104, 24, 'Legal Consultation: IP Protection', 'Meeting with legal team to discuss patent filing and IP strategy.', '2025-12-05 10:00:00', '2025-12-05 11:30:00', 0, 'meeting', '#78716C', 'Law Firm Offices', 0, NULL, 30, '2025-11-22 17:20:56', '2025-11-30 17:20:56'),
(14, 104, 24, 'Demo Day Dry Run', 'Full run-through of demo day presentation with mentors.', '2025-12-07 14:00:00', '2025-12-07 17:00:00', 0, 'meeting', '#DC2626', 'Accelerator Space', 0, NULL, 15, '2025-11-27 17:20:56', '2025-12-01 17:20:56'),
(15, 104, 24, 'Monthly Metrics Review', 'Review key performance indicators and metrics with leadership team.', '2025-12-09 09:00:00', '2025-12-09 10:30:00', 0, 'meeting', '#0EA5E9', 'Board Room', 1, 'FREQ=MONTHLY;BYMONTHDAY=15', 30, '2025-11-09 17:20:56', '2025-11-24 17:20:56'),
(16, 104, NULL, 'Dentist Appointment', 'Regular dental check-up and cleaning.', '2025-12-03 16:00:00', '2025-12-03 17:00:00', 0, 'reminder', '#6B7280', 'Family Dental Clinic', 0, NULL, 60, '2025-11-26 17:20:57', '2025-12-01 17:20:57'),
(17, 104, NULL, 'Friend\'s Birthday Party', 'Celebrating Sarah\'s 30th birthday.', '2025-12-04 19:00:00', '2025-12-04 23:00:00', 0, 'event', '#EC4899', 'The Rooftop Bar', 0, NULL, 120, '2025-11-28 17:20:57', '2025-12-01 17:20:57'),
(18, 104, NULL, 'Gym Session', 'Personal training session', '2025-12-02 07:00:00', '2025-12-02 08:00:00', 0, 'reminder', '#10B981', 'Fitness Center', 1, 'FREQ=WEEKLY;BYDAY=MO,WE,FR', 10, '2025-11-01 17:20:57', '2025-11-01 17:20:57');

-- --------------------------------------------------------

--
-- Structure de la table `chat_conversations`
--

CREATE TABLE IF NOT EXISTS `chat_conversations` (
  `id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `conversation_type` varchar(20) DEFAULT NULL,
  `created_by_id` int(11) NOT NULL,
  `description` text,
  `avatar_url` varchar(500) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `settings` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `unread_count` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `chat_conversations`
--

INSERT INTO `chat_conversations` (`id`, `name`, `conversation_type`, `created_by_id`, `description`, `avatar_url`, `is_active`, `settings`, `created_at`, `updated_at`, `unread_count`) VALUES
(1, 'Test Group Chat', 'group', 11, 'This is a test group', NULL, 1, '{}', '2025-11-21 22:40:34', '2025-11-26 05:46:14', NULL),
(2, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-22 01:40:06', '2025-11-22 03:28:37', NULL),
(3, 'sf collab group', 'group', 11, 'sf collab group group chat', NULL, 1, '{}', '2025-11-22 03:44:55', '2025-11-24 08:13:16', NULL),
(4, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-22 04:39:20', '2025-11-26 19:35:12', NULL),
(100, 'new', 'group', 11, 'new group chat', NULL, 1, '{}', '2025-11-28 04:52:48', '2025-11-28 04:52:48', 0),
(101, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:16', '2025-11-28 16:52:16', 0),
(102, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:22', '2025-11-28 16:52:22', 0),
(103, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:27', '2025-11-28 16:52:27', 0),
(104, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:32', '2025-11-28 16:53:33', 0),
(105, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:38', '2025-11-28 16:52:38', 0),
(106, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:43', '2025-11-28 16:52:43', 0),
(107, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:48', '2025-11-28 16:52:48', 0),
(108, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:54', '2025-11-28 16:52:54', 0),
(109, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:52:59', '2025-11-28 16:52:59', 0),
(110, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:53:04', '2025-11-28 16:53:04', 0),
(111, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:53:10', '2025-11-28 16:53:10', 0),
(112, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:53:15', '2025-11-28 16:53:15', 0),
(113, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:53:20', '2025-11-28 16:53:20', 0),
(114, NULL, 'direct', 11, NULL, NULL, 1, '{}', '2025-11-28 16:53:26', '2025-11-28 16:53:26', 0);

-- --------------------------------------------------------

--
-- Structure de la table `chat_messages`
--

CREATE TABLE IF NOT EXISTS `chat_messages` (
  `id` int(11) NOT NULL,
  `conversation_id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `original_content` text NOT NULL,
  `sender_timezone` varchar(50) DEFAULT NULL,
  `message_type` varchar(20) DEFAULT NULL,
  `metadata_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `is_edited` tinyint(1) DEFAULT NULL,
  `edited_at` datetime DEFAULT NULL,
  `reply_to_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `file_url` varchar(500) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` int(11) DEFAULT NULL,
  `file_type` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `chat_messages`
--

INSERT INTO `chat_messages` (`id`, `conversation_id`, `sender_id`, `original_content`, `sender_timezone`, `message_type`, `metadata_data`, `is_edited`, `edited_at`, `reply_to_id`, `created_at`, `updated_at`, `file_url`, `file_name`, `file_size`, `file_type`) VALUES
(24, 4, 11, 'hello emily', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-24 02:17:28', '2025-11-24 02:17:28', NULL, NULL, NULL, NULL),
(25, 4, 11, 'landing', 'America/Los_Angeles', 'file', '{\"file_info\": {\"original_name\": \"Capture_decran_2025-10-06_230716.png\", \"size\": 899917, \"type\": \"image/png\", \"uploaded_at\": \"2025-11-24T02:18:08.303870\"}}', 0, NULL, NULL, '2025-11-24 02:18:08', '2025-11-24 02:18:08', '/api/chat/uploads/20251124_021808_11_Capture_decran_2025-10-06_230716.png', 'Capture_decran_2025-10-06_230716.png', 899917, 'image/png'),
(26, 3, 11, 'hello guys', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-24 02:19:54', '2025-11-24 02:19:54', NULL, NULL, NULL, NULL),
(27, 3, 11, 'here\'s database schema', 'America/Los_Angeles', 'file', '{\"file_info\": {\"original_name\": \"Database_Schema_Design.pdf\", \"size\": 77573, \"type\": \"application/pdf\", \"uploaded_at\": \"2025-11-24T02:20:24.338693\"}}', 0, NULL, NULL, '2025-11-24 02:20:24', '2025-11-24 02:20:24', '/api/chat/uploads/20251124_022024_11_Database_Schema_Design.pdf', 'Database_Schema_Design.pdf', 77573, 'application/pdf'),
(28, 3, 11, 'last update', 'America/Los_Angeles', 'file', '{\"file_info\": {\"original_name\": \"checkList.docx\", \"size\": 16549, \"type\": \"application/vnd.openxmlformats-officedocument.wordprocessingml.document\", \"uploaded_at\": \"2025-11-24T02:21:02.026498\"}}', 0, NULL, NULL, '2025-11-24 02:21:02', '2025-11-24 02:21:02', '/api/chat/uploads/20251124_022102_11_checkList.docx', 'checkList.docx', 16549, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
(31, 1, 11, 'nice to meet you', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-24 06:36:09', '2025-11-24 06:36:09', NULL, NULL, NULL, NULL),
(32, 1, 12, 'hello ', 'America/Toronto', 'text', '{}', 0, NULL, NULL, '2025-11-24 06:44:29', '2025-11-24 06:44:29', NULL, NULL, NULL, NULL),
(33, 4, 11, 'that\'s good bro', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-24 08:11:54', '2025-11-24 08:11:54', NULL, NULL, NULL, NULL),
(34, 1, 13, 'hello guys', 'Europe/Madrid', 'text', '{}', 0, NULL, NULL, '2025-11-24 08:13:02', '2025-11-24 08:13:02', NULL, NULL, NULL, NULL),
(35, 3, 13, 'good job', 'Europe/Madrid', 'text', '{}', 0, NULL, NULL, '2025-11-24 08:13:16', '2025-11-24 08:13:16', NULL, NULL, NULL, NULL),
(36, 4, 14, 'Sent a file', 'Europe/London', 'file', '{\"file_info\": {\"original_name\": \"checkList.docx\", \"size\": 16549, \"type\": \"application/vnd.openxmlformats-officedocument.wordprocessingml.document\", \"uploaded_at\": \"2025-11-24T08:48:53.441124\"}}', 0, NULL, NULL, '2025-11-24 08:48:53', '2025-11-24 08:48:53', '/api/chat/uploads/20251124_084853_14_checkList.docx', 'checkList.docx', 16549, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
(37, 4, 14, 'updated content', 'Europe/London', 'file', '{\"file_info\": {\"original_name\": \"1000055985.pdf\", \"size\": 6024385, \"type\": \"application/pdf\", \"uploaded_at\": \"2025-11-24T08:49:29.209309\"}}', 1, '2025-11-24 08:50:48', NULL, '2025-11-24 08:49:29', '2025-11-24 08:50:48', '/api/chat/uploads/20251124_084929_14_1000055985.pdf', '1000055985.pdf', 6024385, 'application/pdf'),
(38, 1, 11, 'hello', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-24 22:43:13', '2025-11-24 22:43:13', NULL, NULL, NULL, NULL),
(39, 1, 11, 'hello guys no time no seen ', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-26 05:46:14', '2025-11-26 05:46:14', NULL, NULL, NULL, NULL),
(100, 104, 11, 'meeting at 19', 'America/Los_Angeles', 'text', '{}', 0, NULL, NULL, '2025-11-28 16:53:33', '2025-11-28 16:53:33', NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Structure de la table `conversation_participants`
--

CREATE TABLE IF NOT EXISTS `conversation_participants` (
  `conversation_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `joined_at` datetime DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `conversation_participants`
--

INSERT INTO `conversation_participants` (`conversation_id`, `user_id`, `joined_at`, `role`) VALUES
(1, 11, '2025-11-21 22:40:34', 'admin'),
(1, 12, '2025-11-21 22:40:34', 'member'),
(1, 13, '2025-11-21 22:40:34', 'member'),
(2, 11, '2025-11-22 01:40:06', 'admin'),
(2, 12, '2025-11-22 01:40:06', 'member'),
(2, 13, '2025-11-22 01:40:06', 'member'),
(3, 11, '2025-11-22 03:44:56', 'admin'),
(3, 13, '2025-11-22 03:44:56', 'member'),
(3, 14, '2025-11-22 03:44:56', 'member'),
(3, 15, '2025-11-22 03:44:56', 'member'),
(4, 11, '2025-11-22 04:39:20', 'admin'),
(4, 14, '2025-11-22 04:39:20', 'member'),
(100, 11, '2025-11-28 04:52:48', 'admin'),
(100, 12, '2025-11-28 04:52:49', 'member'),
(100, 13, '2025-11-28 04:52:50', 'member'),
(101, 11, '2025-11-28 16:52:17', 'admin'),
(101, 14, '2025-11-28 16:52:18', 'member'),
(102, 11, '2025-11-28 16:52:22', 'admin'),
(102, 14, '2025-11-28 16:52:23', 'member'),
(103, 11, '2025-11-28 16:52:28', 'admin'),
(103, 14, '2025-11-28 16:52:29', 'member'),
(104, 11, '2025-11-28 16:52:33', 'admin'),
(104, 14, '2025-11-28 16:52:34', 'member'),
(105, 11, '2025-11-28 16:52:38', 'admin'),
(105, 14, '2025-11-28 16:52:39', 'member'),
(106, 11, '2025-11-28 16:52:44', 'admin'),
(106, 14, '2025-11-28 16:52:45', 'member'),
(107, 11, '2025-11-28 16:52:49', 'admin'),
(107, 14, '2025-11-28 16:52:50', 'member'),
(108, 11, '2025-11-28 16:52:54', 'admin'),
(108, 14, '2025-11-28 16:52:55', 'member'),
(109, 11, '2025-11-28 16:53:00', 'admin'),
(109, 14, '2025-11-28 16:53:01', 'member'),
(110, 11, '2025-11-28 16:53:05', 'admin'),
(110, 14, '2025-11-28 16:53:06', 'member'),
(111, 11, '2025-11-28 16:53:10', 'admin'),
(111, 14, '2025-11-28 16:53:11', 'member'),
(112, 11, '2025-11-28 16:53:16', 'admin'),
(112, 14, '2025-11-28 16:53:17', 'member'),
(113, 11, '2025-11-28 16:53:21', 'admin'),
(113, 14, '2025-11-28 16:53:22', 'member'),
(114, 11, '2025-11-28 16:53:26', 'admin'),
(114, 14, '2025-11-28 16:53:27', 'member');

-- --------------------------------------------------------

--
-- Structure de la table `conversation_user_reads`
--

CREATE TABLE IF NOT EXISTS `conversation_user_reads` (
  `conversation_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `last_read_at` datetime DEFAULT NULL,
  `unread_count` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `conversation_user_reads`
--

INSERT INTO `conversation_user_reads` (`conversation_id`, `user_id`, `last_read_at`, `unread_count`) VALUES
(1, 11, '2025-11-26 19:33:11', 0),
(1, 12, '2025-11-24 06:43:26', 3),
(1, 13, '2025-11-24 08:12:47', 2),
(2, 11, '2025-11-24 08:13:24', 0),
(2, 13, '2025-11-24 08:12:21', 0),
(3, 11, '2025-11-24 22:38:46', 0),
(3, 13, '2025-11-24 08:13:04', 0),
(3, 14, '2025-11-24 10:24:44', 0),
(3, 15, '2025-11-24 08:13:16', 1),
(4, 11, '2025-11-28 02:41:59', 0),
(4, 14, '2025-11-24 10:26:08', 1),
(104, 14, '2025-11-28 16:53:33', 1);

-- --------------------------------------------------------

--
-- Structure de la table `goal_milestones`
--

CREATE TABLE IF NOT EXISTS `goal_milestones` (
  `id` int(11) NOT NULL,
  `goal_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `order` int(11) DEFAULT NULL,
  `is_completed` tinyint(1) DEFAULT NULL,
  `completed_date` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `growth_metrics`
--

CREATE TABLE IF NOT EXISTS `growth_metrics` (
  `id` int(11) NOT NULL,
  `startup_id` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
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
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `ideas`
--

CREATE TABLE IF NOT EXISTS `ideas` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `project_details` text NOT NULL,
  `industry` varchar(100) NOT NULL,
  `stage` varchar(100) NOT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `creator_id` int(11) NOT NULL,
  `creator_first_name` varchar(100) DEFAULT NULL,
  `creator_last_name` varchar(100) DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `views` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `privacy` enum('public','private') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `ideas`
--

INSERT INTO `ideas` (`id`, `title`, `description`, `project_details`, `industry`, `stage`, `tags`, `creator_id`, `creator_first_name`, `creator_last_name`, `status`, `likes`, `views`, `created_at`, `updated_at`, `privacy`) VALUES
(16, 'AI-Powered Learning Platform for Kids', 'An adaptive learning platform that uses AI to personalize educational content for children based on their learning style and pace.', 'The platform will use machine learning algorithms to analyze student performance and adapt content difficulty. Will include gamification elements and progress tracking for parents.', 'Education Technology', 'Concept', '[\"AI\", \"Education\", \"Machine Learning\", \"EdTech\", \"Children\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 177, 779, '2025-11-01 17:07:35', '2025-11-29 17:07:35', 'public'),
(17, 'Sustainable Vertical Farming System', 'A modular vertical farming system for urban environments that uses 90% less water than traditional farming.', 'System includes automated nutrient delivery, LED lighting optimized for plant growth, and IoT sensors for monitoring plant health. Targeting restaurants and urban communities.', 'Agriculture', 'Prototype', '[\"Sustainability\", \"Agriculture\", \"Urban Farming\", \"IoT\", \"Green Tech\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 150, 803, '2025-11-06 17:07:35', '2025-11-26 17:07:35', 'public'),
(18, 'Blockchain-Based Digital Identity Solution', 'A decentralized digital identity system that gives users control over their personal data and verification credentials.', 'Using blockchain technology to create tamper-proof digital identities. Solution includes mobile app for identity management and API for third-party verification.', 'FinTech', 'Research', '[\"Blockchain\", \"Security\", \"Digital Identity\", \"Privacy\", \"FinTech\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 55, 349, '2025-11-11 17:07:35', '2025-11-30 17:07:35', 'private'),
(19, 'Mental Health Companion App', 'An AI-powered mental health app that provides daily check-ins, coping strategies, and connects users with resources.', 'Features include mood tracking, guided meditation, cognitive behavioral therapy exercises, and emergency resource directory. Will use natural language processing for conversational support.', 'Healthcare', 'Planning', '[\"Mental Health\", \"AI\", \"Healthcare\", \"Wellness\", \"Mobile App\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 87, 510, '2025-11-16 17:07:35', '2025-11-28 17:07:35', 'public'),
(20, 'Smart Waste Management System', 'IoT-based waste management system that optimizes collection routes and schedules based on fill levels.', 'Smart bins with sensors transmit fill level data to central system. Algorithm optimizes collection routes to reduce fuel consumption and operational costs.', 'Clean Tech', 'Development', '[\"IoT\", \"Sustainability\", \"Smart Cities\", \"Waste Management\", \"Clean Tech\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 152, 654, '2025-11-21 17:07:35', '2025-12-01 17:07:35', 'public'),
(21, 'AR Interior Design Platform', 'Augmented Reality app that lets users visualize furniture and decor in their space before purchasing.', 'Users upload room dimensions or use phone camera to create AR overlay of products. Integration with furniture retailers and interior design services.', 'Retail Technology', 'Concept', '[\"AR\", \"Interior Design\", \"Retail\", \"Mobile App\", \"Visualization\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 101, 944, '2025-11-23 17:07:35', '2025-11-30 17:07:35', 'public'),
(22, 'Remote Team Collaboration Tool', 'Virtual workspace designed for distributed teams with integrated project management and communication features.', 'Includes virtual whiteboards, task management, video conferencing, and document collaboration. Focus on reducing meeting fatigue and improving asynchronous work.', 'SaaS', 'Beta', '[\"Remote Work\", \"SaaS\", \"Collaboration\", \"Productivity\", \"B2B\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 144, 147, '2025-11-26 17:07:35', '2025-12-01 17:07:35', 'private'),
(23, 'Plant-Based Meat Alternatives Marketplace', 'Online platform connecting consumers with local producers of plant-based meat alternatives.', 'Subscription box service and a la carte ordering. Focus on locally-sourced, sustainable plant-based proteins with transparent sourcing information.', 'Food Tech', 'Planning', '[\"Food Tech\", \"Sustainability\", \"Plant-Based\", \"E-commerce\", \"Health\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 18, 399, '2025-11-28 17:07:35', '2025-12-01 17:07:35', 'public'),
(24, 'Renewable Energy Microgrid Controller', 'Smart controller for managing microgrids with mixed renewable energy sources (solar, wind, battery storage).', 'Uses AI to predict energy production and consumption, optimizing energy distribution and storage. Targets rural communities and commercial campuses.', 'Energy', 'Research', '[\"Renewable Energy\", \"AI\", \"Smart Grid\", \"Sustainability\", \"Clean Energy\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 47, 370, '2025-11-29 17:07:35', '2025-12-01 17:07:35', 'public'),
(25, 'Personal Finance AI Assistant', 'AI-powered financial advisor that helps users with budgeting, saving, and investment decisions.', 'Analyzes spending patterns, suggests budgets, identifies saving opportunities, and provides personalized investment recommendations based on risk profile.', 'FinTech', 'Concept', '[\"FinTech\", \"AI\", \"Personal Finance\", \"Investing\", \"Budgeting\"]', 104, 'MOHAMMED', 'DHIMNI', 'active', 131, 545, '2025-11-30 17:07:35', '2025-12-01 17:07:35', 'public');

-- --------------------------------------------------------

--
-- Structure de la table `idea_bookmarks`
--

CREATE TABLE IF NOT EXISTS `idea_bookmarks` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `idea_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content_preview` text,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `idea_comments`
--

CREATE TABLE IF NOT EXISTS `idea_comments` (
  `id` int(11) NOT NULL,
  `idea_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `join_requests`
--

CREATE TABLE IF NOT EXISTS `join_requests` (
  `id` int(11) NOT NULL,
  `startup_id` int(11) NOT NULL,
  `startup_name` varchar(255) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `message` text,
  `role` varchar(100) DEFAULT NULL,
  `status` enum('pending','approved','rejected') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `knowledge`
--

CREATE TABLE IF NOT EXISTS `knowledge` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `title_description` text NOT NULL,
  `content_preview` text NOT NULL,
  `category` varchar(100) NOT NULL,
  `file_url` varchar(500) DEFAULT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `status` enum('active','inactive') DEFAULT NULL,
  `views` int(11) DEFAULT NULL,
  `downloads` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `image_buffer` blob,
  `image_content_type` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `knowledge_bookmarks`
--

CREATE TABLE IF NOT EXISTS `knowledge_bookmarks` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `knowledge_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content_preview` text,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `knowledge_comments`
--

CREATE TABLE IF NOT EXISTS `knowledge_comments` (
  `id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `notifications`
--

CREATE TABLE IF NOT EXISTS `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `title` varchar(255) DEFAULT NULL,
  `message` text,
  `data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `is_read` tinyint(1) DEFAULT NULL,
  `read_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `type`, `title`, `message`, `data`, `is_read`, `read_at`, `created_at`, `updated_at`) VALUES
(1, 104, 'system', 'Welcome to the Platform', 'Thank you for joining our platform! We are excited to have you here.', '{\"action\": \"welcome\", \"page\": \"dashboard\"}', 0, NULL, '2025-11-29 03:44:24', '2025-11-29 03:44:24'),
(2, 104, 'system', 'Profile Update Required', 'Please complete your profile information to get the most out of our platform.', '{\"action\": \"update_profile\", \"page\": \"profile\"}', 1, '2025-11-29 04:44:24', '2025-11-29 02:44:24', '2025-11-29 04:44:24'),
(3, 104, 'suggestion', 'New Suggestion Available', 'You have a new suggestion waiting for your review.', '{\"suggestion_id\": 456, \"status\": \"pending\", \"type\": \"feature\"}', 1, '2025-11-29 05:47:13', '2025-11-29 05:14:24', '2025-11-29 05:47:13'),
(4, 104, 'suggestion', 'Suggestion Approved', 'Your suggestion \"Dark Mode Feature\" has been approved by the admin.', '{\"suggestion_id\": 123, \"status\": \"approved\", \"title\": \"Dark Mode Feature\"}', 1, '2025-11-29 05:29:24', '2025-11-29 04:59:24', '2025-11-29 05:29:24'),
(5, 104, 'system', 'Weekly Summary', 'Here is your weekly activity summary. You have been very active this week!', '{\"period\": \"week\", \"activities\": 15, \"achievements\": 3}', 1, '2025-11-29 05:47:10', '2025-11-29 05:34:24', '2025-11-29 05:47:10'),
(6, 104, 'system', 'System Maintenance', 'Scheduled maintenance will occur this weekend. The system may be unavailable for 2 hours.', '{\"maintenance_date\": \"2024-01-15\", \"duration\": \"2 hours\"}', 1, '2025-11-28 03:44:24', '2025-11-27 23:44:24', '2025-11-28 03:44:24'),
(7, 104, 'suggestion', 'Suggestion Feedback', 'Your suggestion needs some modifications before it can be approved.', '{\"suggestion_id\": 789, \"status\": \"rejected\", \"feedback\": \"Please provide more details about implementation\"}', 1, '2025-11-29 00:44:24', '2025-11-28 21:44:24', '2025-11-29 00:44:24'),
(8, 104, 'urgent', 'Security Alert', 'Unusual login activity detected on your account. Please review your account security.', '{\"alert_level\": \"high\", \"action_required\": true, \"ip_address\": \"192.168.1.100\"}', 1, '2025-11-29 05:46:57', '2025-11-29 05:39:24', '2025-11-29 05:46:57');

-- --------------------------------------------------------

--
-- Structure de la table `posts`
--

CREATE TABLE IF NOT EXISTS `posts` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `content` text NOT NULL,
  `type` enum('professional','social','image','video') DEFAULT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `likes` int(11) DEFAULT NULL,
  `comments_count` int(11) DEFAULT NULL,
  `shares` int(11) DEFAULT NULL,
  `saves` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `post_comments`
--

CREATE TABLE IF NOT EXISTS `post_comments` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `post_likes`
--

CREATE TABLE IF NOT EXISTS `post_likes` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `liked_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `post_media`
--

CREATE TABLE IF NOT EXISTS `post_media` (
  `id` int(11) NOT NULL,
  `post_id` int(11) NOT NULL,
  `data` blob,
  `content_type` varchar(100) DEFAULT NULL,
  `file_name` varchar(255) DEFAULT NULL,
  `file_size` int(11) DEFAULT NULL,
  `caption` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `project_goals`
--

CREATE TABLE IF NOT EXISTS `project_goals` (
  `id` int(11) NOT NULL,
  `startup_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `progress_percentage` float DEFAULT NULL,
  `milestones_completed` int(11) DEFAULT NULL,
  `milestones_total` int(11) DEFAULT NULL,
  `is_on_track` tinyint(1) DEFAULT NULL,
  `next_milestone` varchar(255) DEFAULT NULL,
  `target_date` datetime DEFAULT NULL,
  `completed_date` datetime DEFAULT NULL,
  `status` enum('active','completed','on_hold','cancelled') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `refresh_tokens`
--

CREATE TABLE IF NOT EXISTS `refresh_tokens` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `token` varchar(500) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `refresh_tokens`
--

INSERT INTO `refresh_tokens` (`id`, `user_id`, `token`, `created_at`, `updated_at`) VALUES
(1, 0, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDI5NTM3OSwianRpIjoiMTA5MGZmMTItNWUwOC00NTM2LTlmN2UtNWU3N2ZmMjU0Y2U1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIwIiwibmJmIjoxNzY0Mjk1Mzc5LCJjc3JmIjoiZWFhZjg3ZjMtZmIzMC00ZWEzLWFiMjYtMDNmYTljMDExZDk0IiwiZXhwIjoxNzY2ODg3Mzc5fQ.cxyGKlrka7LsGsIzLhhVhyn4zbBflqiA_6ZYgGq2CPY', '2025-11-28 02:02:59', '2025-11-28 02:02:59'),
(2, 21, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDI5NTQ4MiwianRpIjoiZWI2NjM4NWUtNzZhZS00ODE1LWFkYzMtNDFlOWZmMTI0N2I5IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIyMSIsIm5iZiI6MTc2NDI5NTQ4MiwiY3NyZiI6IjhhZjA4NWNjLWEyNGYtNDRlZC1iYzhhLTc2NTA0OTVkMzMwZSIsImV4cCI6MTc2Njg4NzQ4Mn0.1SyaQyWulSG2Z-xC_rv1o9pdTDsxQPoiFb1vepeTXPE', '2025-11-28 02:04:42', '2025-11-28 02:04:42'),
(4, 101, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDMwMDMzMywianRpIjoiY2YwZTQ5ODktNDA4NS00NDI0LWE1Y2QtM2ViMjBjYWQxOWUzIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDEiLCJuYmYiOjE3NjQzMDAzMzMsImNzcmYiOiI1OTg1ODFiZi1lYzhmLTQ5NDUtYjUyNy1hY2M5NDg3MTY2ZjgiLCJleHAiOjE3NjY4OTIzMzN9.lryZtBB7yOdgCSD9ocgWbRT69KOC-8hC_46sGyXsYsw', '2025-11-28 03:25:33', '2025-11-28 03:25:33'),
(11, 102, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM1MzIxMiwianRpIjoiOTAxODk4OGQtNDk1My00ZTQ1LWFiYjQtNGZhNTk3MGYxMTYzIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDIiLCJuYmYiOjE3NjQzNTMyMTIsImNzcmYiOiI5YjY2Zjk4ZC1jNDJhLTQyNjUtOGUxNi01YWU2OWQzZTY4OWQiLCJleHAiOjE3NjY5NDUyMTJ9.9tjcx6EMy2f13q0hmnr5MQugQfWEkl9WsOBiG81N6Kk', '2025-11-28 18:06:52', '2025-11-28 18:06:52'),
(13, 103, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM1MzI2MywianRpIjoiNjI2NmM2OWQtODE3MC00MzNhLThkYmEtZjZmMjEyNzI2M2Q3IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDMiLCJuYmYiOjE3NjQzNTMyNjMsImNzcmYiOiI5YjQyNjIwNS0zMDc2LTQxMDUtYWRmMC0xNDIyZTdlMzQ1ZTgiLCJleHAiOjE3NjY5NDUyNjN9.5AiYV_8YZ1ON8z-bFaVUN59HbcbsNl2P6U0YirmX4EM', '2025-11-28 18:07:43', '2025-11-28 18:07:43'),
(20, 105, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM2MDk1OCwianRpIjoiNWQ5YmYyZTMtNDZmNC00Y2RhLThhYTEtMDEyMDE1ZGEwMjEzIiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDUiLCJuYmYiOjE3NjQzNjA5NTgsImNzcmYiOiJkM2NmMDQzZC03Mzg1LTQxODgtODVhMi02NDJiN2Q4YWZiOGMiLCJleHAiOjE3NjY5NTI5NTh9.8akyIhkXC7pqiem3LKIhfCD2SYZTea-AN5IrS7yJSwg', '2025-11-28 20:15:58', '2025-11-28 20:15:58'),
(22, 100, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDM4NzE5MSwianRpIjoiOTg1MjM1MjItOTMwZC00M2VmLTg5YTMtMGM4M2VhNWE0ZTc1IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDAiLCJuYmYiOjE3NjQzODcxOTEsImNzcmYiOiJjNmFjZjQ3Yi1lOTFkLTQ3NTItOTU1Ny1iYWY5NGY2ZGY4MTkiLCJleHAiOjE3NjY5NzkxOTF9.hu_PQeSknxuL8FhHrBmLdm0OPtTv-X5QSFuCXLWhM2o', '2025-11-29 03:33:11', '2025-11-29 03:33:11'),
(37, 106, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDYxMTk4MSwianRpIjoiZGViYmUyNTMtNWFlNC00ODIxLWE2MjQtYmM0NzYwZTlhNDg4IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDYiLCJuYmYiOjE3NjQ2MTE5ODEsImNzcmYiOiJlMDYxZTE0OS1lZDhlLTRlYTctYThlNC0wYjBhNmYxOTFkM2QiLCJleHAiOjE3NjcyMDM5ODF9.RSf-JBZMfyPZNdlXvVu7IL9a6ESmXyfS4MVcSL8Aohk', '2025-12-01 17:59:41', '2025-12-01 17:59:41'),
(38, 104, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2NDYxODcxMiwianRpIjoiNDNmYjU0NGMtZTJlOC00MzZkLWE4MjAtNDY5NTExZGIwZGI0IiwidHlwZSI6InJlZnJlc2giLCJzdWIiOiIxMDQiLCJuYmYiOjE3NjQ2MTg3MTIsImNzcmYiOiIxOWM1MDI1Ny01ODNiLTRjNjgtODYyMi1iZDRhZjJiNGJlMDYiLCJleHAiOjE3NjcyMTA3MTJ9.aJWUmtYXI_ADBLxKk9zhcU3WUCr9mXqmS5EsIWxx9w8', '2025-12-01 19:51:53', '2025-12-01 19:51:53');

-- --------------------------------------------------------

--
-- Structure de la table `resource_downloads`
--

CREATE TABLE IF NOT EXISTS `resource_downloads` (
  `id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `downloaded_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `resource_likes`
--

CREATE TABLE IF NOT EXISTS `resource_likes` (
  `id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `liked_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `resource_views`
--

CREATE TABLE IF NOT EXISTS `resource_views` (
  `id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `viewed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `startups`
--

CREATE TABLE IF NOT EXISTS `startups` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `industry` varchar(100) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `description` text,
  `stage` enum('idea','early','growth','scale') DEFAULT NULL,
  `logo_content_type` varchar(100) DEFAULT NULL,
  `banner_content_type` varchar(100) DEFAULT NULL,
  `positions` int(11) DEFAULT NULL,
  `roles` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `creator_id` int(11) NOT NULL,
  `creator_first_name` varchar(100) DEFAULT NULL,
  `creator_last_name` varchar(100) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `member_count` int(11) DEFAULT NULL,
  `views` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `revenue` float DEFAULT NULL,
  `funding_amount` float DEFAULT NULL,
  `funding_round` varchar(50) DEFAULT NULL,
  `burn_rate` float DEFAULT NULL,
  `runway_months` int(11) DEFAULT NULL,
  `valuation` float DEFAULT NULL,
  `financial_notes` text,
  `logo_path` varchar(500) DEFAULT NULL,
  `banner_path` varchar(500) DEFAULT NULL,
  `tech_stack` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `logo_url` varchar(500) DEFAULT NULL,
  `banner_url` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `startups`
--

INSERT INTO `startups` (`id`, `name`, `industry`, `location`, `description`, `stage`, `logo_content_type`, `banner_content_type`, `positions`, `roles`, `creator_id`, `creator_first_name`, `creator_last_name`, `status`, `member_count`, `views`, `created_at`, `updated_at`, `revenue`, `funding_amount`, `funding_round`, `burn_rate`, `runway_months`, `valuation`, `financial_notes`, `logo_path`, `banner_path`, `tech_stack`, `logo_url`, `banner_url`) VALUES
(21, 'InterviewGenieAI', 'Manufacturing', 'MOROCCO ', 'edazdazd', 'idea', 'image/png', 'image/png', 2, '{\"frontend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 1}, \"backend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 1}}', 11, 'Mohammed', 'Dhimni', 'active', 1, 0, '2025-11-25 18:41:20', '2025-11-25 18:41:20', 1000, 1000, 'pre-seed', 1000, 1, 1000, 'lzekjklzejdkjzed', 'E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_da634bd8.png', 'E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_6cf5cf0f.png', '[\"JavaScript\", \"TypeScript\", \"Python\", \"React\"]', '/startups/23/logo', '/startups/23/banner'),
(22, 'SF MANAGER', 'Technology', 'MOROCCO ', 'azsazsaz', 'idea', 'image/jpeg', 'image/jpeg', 3, '{\"frontend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 1}, \"backend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 2}}', 11, 'Oskar', 'Alaoui', 'active', 1, 1, '2025-11-25 19:28:49', '2025-11-26 05:42:39', 1000, 2000, 'pre-seed', 1000, 1, 1000, 'erferferf', 'E:\\LLMs_test\\uploads\\startups\\22\\20251125_192849_1b0e0ba2.jpg', NULL, '[\"JavaScript\", \"TypeScript\", \"Python\", \"React\"]', '/startups/23/logo', '/startups/23/banner'),
(23, 'new startup', 'Technology', 'Morocco', 'zertfyguhiokplhgfg', 'idea', 'image/png', 'image/png', 3, '{\"AI Engineer\": {\"roleType\": \"Full Time\", \"positionsNumber\": 3}}', 11, 'Oskar', 'ufgyufyu', 'active', 1, 429, '2025-11-25 20:24:31', '2025-11-28 04:55:58', 1000, 1000, 'pre-seed', 1000, 1, 1000, 'xeyuiop;m', 'E:\\LLMs_test\\uploads\\startups\\23\\20251125_202431_052e644a_file_000000000a9861f5868855fffc87f260.png', 'E:\\LLMs_test\\uploads\\startups\\23\\20251125_202431_2f276357_Capture_decran_2025-11-05_230140.png', '[\"JavaScript\", \"Python\"]', '/startups/23/logo', '/startups/23/banner'),
(24, 'SF COLLAB', 'Technology', 'USA', 'sjkhkldjklsjd', 'idea', 'image/png', 'image/png', 6, '{\"frontend \": {\"roleType\": \"Intern\", \"positionsNumber\": 4}, \"backend\": {\"roleType\": \"Intern\", \"positionsNumber\": 2}}', 104, 'Mohammed', 'Dhimni', 'active', 1, 9, '2025-11-26 18:49:43', '2025-12-01 19:28:09', 2000, 2000, 'pre-seed', 1000, 1, 3000, 'notess', 'E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_5256296a_stars.png', 'E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_906abcb6_ChatGPT_Image_5_nov._2025_00_44_28.png', '[\"JavaScript\", \"Angular\", \"Python\"]', '/startups/24/logo', '/startups/24/banner'),
(25, 'PatternsChange', 'Finance', 'Morocco', 'uhdihzdz \"Tell us more about your vision and stage\r\n\"', '', 'image/png', 'image/png', 4, '{\"frontend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 2}, \"backend\": {\"roleType\": \"Full Time\", \"positionsNumber\": 2}}', 104, 'Mohamed', 'Dhimni', 'active', 1, 2, '2025-11-28 02:34:02', '2025-11-28 14:42:34', 4000, 35000, 'pre-seed', 4000, 2, 4000, 'zkladjlazjdkazd', '/opt/render/project/src/uploads/startups/0/20251128_023402_e5d23a3a_file_000000000a9861f5868855fffc87f260.png', '/opt/render/project/src/uploads/startups/0/20251128_023402_8a64f726_file_0000000037f46246aaeebb8a0c79b3fd.png', '[\"JavaScript\", \"TypeScript\", \"React\"]', '/startups/0/logo', '/startups/0/banner');

-- --------------------------------------------------------

--
-- Structure de la table `startup_bookmarks`
--

CREATE TABLE IF NOT EXISTS `startup_bookmarks` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `startup_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `content_preview` text,
  `url` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `startup_documents`
--

CREATE TABLE IF NOT EXISTS `startup_documents` (
  `id` int(11) NOT NULL,
  `startup_id` int(11) NOT NULL,
  `filename` varchar(255) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `content_type` varchar(100) NOT NULL,
  `document_type` varchar(50) DEFAULT NULL,
  `file_size` int(11) DEFAULT NULL,
  `uploaded_at` datetime DEFAULT NULL,
  `file_url` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `startup_documents`
--

INSERT INTO `startup_documents` (`id`, `startup_id`, `filename`, `file_path`, `content_type`, `document_type`, `file_size`, `uploaded_at`, `file_url`) VALUES
(1, 21, '1000055985.pdf', 'E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_25647868.pdf', 'application/pdf', 'general', 6024385, '2025-11-25 18:41:20', NULL),
(2, 21, 'checkList.docx', 'E:\\LLMs_test\\uploads\\startups\\21\\20251125_184120_948cbc55.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'general', 16549, '2025-11-25 18:41:20', NULL),
(3, 22, 'SX.pdf', 'E:\\LLMs_test\\uploads\\startups\\22\\20251125_192849_d2785b85.pdf', 'application/pdf', 'general', 89974, '2025-11-25 19:28:49', NULL),
(4, 23, 'nice.pdf', 'E:\\LLMs_test\\uploads\\startups\\23\\20251125_202432_4d3f81f8_nice.pdf', 'application/pdf', 'general', 52367, '2025-11-25 20:24:32', '/api/startups/23/documents/20251125_202432_4d3f81f8_nice.pdf'),
(5, 24, 'checkList.docx', 'E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_be06e303_checkList.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'general', 16549, '2025-11-26 18:49:43', '/startups/24/documents/20251126_184943_be06e303_checkList.docx'),
(6, 24, 'Weekly Working Hours Availability (12_11_25 - 15_11_25) - Google Forms.pdf', 'E:\\LLMs_test\\uploads\\startups\\24\\20251126_184943_b70ecc95_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf', 'application/pdf', 'general', 63779, '2025-11-26 18:49:43', '/startups/24/documents/20251126_184943_b70ecc95_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf'),
(7, 0, 'Nouveau Microsoft Word Document (2).docx', '/opt/render/project/src/uploads/startups/0/20251128_023402_6f8f1976_Nouveau_Microsoft_Word_Document_2.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'general', 0, '2025-11-28 02:34:02', '/startups/0/documents/20251128_023402_6f8f1976_Nouveau_Microsoft_Word_Document_2.docx'),
(8, 0, 'Schema For The Ai Interviewer Based On The Dashboa.pdf', '/opt/render/project/src/uploads/startups/0/20251128_023403_1efe6daf_Schema_For_The_Ai_Interviewer_Based_On_The_Dashboa.pdf', 'application/pdf', 'general', 70534, '2025-11-28 02:34:03', '/startups/0/documents/20251128_023403_1efe6daf_Schema_For_The_Ai_Interviewer_Based_On_The_Dashboa.pdf'),
(9, 0, 'Weekly Working Hours Availability (12_11_25 - 15_11_25) - Google Forms.pdf', '/opt/render/project/src/uploads/startups/0/20251128_023403_e23d53e0_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf', 'application/pdf', 'general', 63779, '2025-11-28 02:34:04', '/startups/0/documents/20251128_023403_e23d53e0_Weekly_Working_Hours_Availability_12_11_25_-_15_11_25_-_Google_Forms.pdf');

-- --------------------------------------------------------

--
-- Structure de la table `startup_members`
--

CREATE TABLE IF NOT EXISTS `startup_members` (
  `id` int(11) NOT NULL,
  `startup_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `first_name` varchar(100) DEFAULT NULL,
  `last_name` varchar(100) DEFAULT NULL,
  `role` enum('founder','contributor','investor','advisor','mentor','partner','admin','moderator','member','technical_lead','engineering_manager','backend_engineer','frontend_engineer','fullstack_engineer','mobile_engineer','software_architect','qa_engineer','test_automation_engineer','devops_engineer','cloud_engineer','sre','infrastructure_engineer','platform_engineer','cybersecurity_engineer','data_scientist','data_engineer','machine_learning_engineer','ai_engineer','mlops_engineer','data_analyst','ai_researcher','product_manager','product_owner','ux_designer','ui_designer','product_designer','ux_researcher','growth_engineer','growth_marketer','seo_specialist','content_strategist') DEFAULT NULL,
  `joined_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `startup_members`
--

INSERT INTO `startup_members` (`id`, `startup_id`, `user_id`, `first_name`, `last_name`, `role`, `joined_at`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 21, 11, 'Mohammed', 'Dhimni', 'founder', '2025-11-25 18:41:20', 1, '2025-11-25 18:41:20', '2025-11-25 18:41:20'),
(2, 22, 11, 'Oskar', 'Alaoui', 'founder', '2025-11-25 19:28:49', 1, '2025-11-25 19:28:49', '2025-11-25 19:28:49'),
(3, 23, 11, 'Oskar', 'ufgyufyu', 'founder', '2025-11-25 20:24:32', 1, '2025-11-25 20:24:32', '2025-11-25 20:24:32'),
(4, 24, 11, 'Mohammed', 'Dhimni', 'founder', '2025-11-26 18:49:43', 1, '2025-11-26 18:49:43', '2025-11-26 18:49:43'),
(5, 0, 100, 'Mohamed', 'Dhimni', 'founder', '2025-11-28 02:34:04', 1, '2025-11-28 02:34:04', '2025-11-28 02:34:04');

-- --------------------------------------------------------

--
-- Structure de la table `stories`
--

CREATE TABLE IF NOT EXISTS `stories` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `media_url` varchar(500) NOT NULL,
  `caption` text,
  `type` enum('image','video') DEFAULT NULL,
  `views` int(11) DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `story_views`
--

CREATE TABLE IF NOT EXISTS `story_views` (
  `id` int(11) NOT NULL,
  `story_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `viewed_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `suggestions`
--

CREATE TABLE IF NOT EXISTS `suggestions` (
  `id` int(11) NOT NULL,
  `idea_id` int(11) NOT NULL,
  `content` text NOT NULL,
  `author_id` int(11) NOT NULL,
  `author_first_name` varchar(100) DEFAULT NULL,
  `author_last_name` varchar(100) DEFAULT NULL,
  `status` enum('pending','accepted','rejected') DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `tasks`
--

CREATE TABLE IF NOT EXISTS `tasks` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `startup_id` int(11) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `priority` enum('low','medium','high') DEFAULT NULL,
  `status` enum('today','in_progress','completed','overdue') DEFAULT NULL,
  `tags` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `labels` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
  `due_date` datetime DEFAULT NULL,
  `completed_date` datetime DEFAULT NULL,
  `estimated_hours` float DEFAULT NULL,
  `actual_hours` float DEFAULT NULL,
  `assigned_to` int(11) DEFAULT NULL,
  `created_by` int(11) NOT NULL,
  `is_on_time` tinyint(1) DEFAULT NULL,
  `progress_percentage` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `team_members`
--

CREATE TABLE IF NOT EXISTS `team_members` (
  `id` int(11) NOT NULL,
  `idea_id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `position` varchar(255) DEFAULT NULL,
  `skills` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `team_performance`
--

CREATE TABLE IF NOT EXISTS `team_performance` (
  `id` int(11) NOT NULL,
  `startup_id` int(11) NOT NULL,
  `score_percentage` float DEFAULT NULL,
  `active_members` int(11) DEFAULT NULL,
  `tasks_completed` int(11) DEFAULT NULL,
  `productivity_level` enum('low','medium','high') DEFAULT NULL,
  `period_start` datetime NOT NULL,
  `period_end` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Structure de la table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `email` varchar(191) NOT NULL,
  `password` varchar(255) NOT NULL,
  `is_email_verified` tinyint(1) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `status` enum('active','deleted') DEFAULT NULL,
  `role` enum('founder','contributor','investor','advisor','mentor','partner','admin','moderator','member','technical_lead','engineering_manager','backend_engineer','frontend_engineer','fullstack_engineer','mobile_engineer','software_architect','qa_engineer','test_automation_engineer','devops_engineer','cloud_engineer','sre','infrastructure_engineer','platform_engineer','cybersecurity_engineer','data_scientist','data_engineer','machine_learning_engineer','ai_engineer','mlops_engineer','data_analyst','ai_researcher','product_manager','product_owner','ux_designer','ui_designer','product_designer','ux_researcher','growth_engineer','growth_marketer','seo_specialist','content_strategist') DEFAULT NULL,
  `xp_points` int(11) DEFAULT NULL,
  `streak_days` int(11) DEFAULT NULL,
  `last_activity_date` date DEFAULT NULL,
  `total_revenue` float DEFAULT NULL,
  `satisfaction_percentage` float DEFAULT NULL,
  `active_startups_count` int(11) DEFAULT NULL,
  `profile_picture` varchar(500) DEFAULT NULL,
  `profile_bio` text,
  `profile_company` varchar(255) DEFAULT NULL,
  `profile_social_links` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,
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
  `updated_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Déchargement des données de la table `users`
--

INSERT INTO `users` (`id`, `first_name`, `last_name`, `email`, `password`, `is_email_verified`, `last_login`, `status`, `role`, `xp_points`, `streak_days`, `last_activity_date`, `total_revenue`, `satisfaction_percentage`, `active_startups_count`, `profile_picture`, `profile_bio`, `profile_company`, `profile_social_links`, `profile_country`, `profile_city`, `profile_timezone`, `pref_email_notifications`, `pref_push_notifications`, `pref_privacy`, `pref_language`, `pref_timezone`, `pref_theme`, `notif_new_comments`, `notif_new_likes`, `notif_new_suggestions`, `notif_join_requests`, `notif_approvals`, `notif_story_views`, `notif_post_engagement`, `notif_email_digest`, `notif_quiet_hours_enabled`, `notif_quiet_hours_start`, `notif_quiet_hours_end`, `created_at`, `updated_at`) VALUES
(11, 'John', 'Admin', 'admin@startup.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7uO9P0tYY0tR8k8D6eB6QY8YdX7vL5sYfC', 1, '2024-01-15 09:30:00', 'active', 'admin', 5000, 45, '2024-01-15', 25000, 95.5, 3, 'https://example.com/images/admin-profile.jpg', 'Experienced startup founder and mentor with 10+ years in tech industry.', 'TechStart Inc.', '{\"twitter\": \"https://twitter.com/johnadmin\", \"linkedin\": \"https://linkedin.com/in/johnadmin\", \"github\": \"https://github.com/johnadmin\"}', 'United States', 'San Francisco', 'America/Los_Angeles', 1, 1, 'public', 'en', 'America/Los_Angeles', 'dark', 1, 1, 1, 1, 1, 0, 1, 'daily', 1, '22:00', '07:00', '2023-01-10 08:00:00', '2024-01-15 09:30:00'),
(12, 'Sarah', 'Chen', 'sarah.chen@startup.com', '$2b$12$K8v9c2zR.CVHxjd0M9l8vN0Q1uZZ1uS9l9E7fC7RZ9ZeY8wM6tZhD', 1, '2024-01-15 10:15:00', 'active', 'founder', 3200, 30, '2024-01-15', 15000, 88.2, 2, 'https://example.com/images/sarah-profile.jpg', 'Passionate about AI and machine learning. Building the next generation of intelligent applications.', 'AI Innovations LLC', '{\"linkedin\": \"https://linkedin.com/in/sarahchen\", \"twitter\": \"https://twitter.com/sarahchenai\"}', 'Canada', 'Toronto', 'America/Toronto', 1, 1, 'public', 'en', 'America/Toronto', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '23:00', '08:00', '2023-03-15 14:20:00', '2024-01-15 10:15:00'),
(13, 'Mike', 'Rodriguez', 'mike.rodriguez@startup.com', '$2b$12$N9w0d3A.SDWJyl1N0m9wO1R2vAA2vT0m0F8gD8SA0AfZd9xN7uAiE', 1, '2024-01-14 16:45:00', 'active', 'member', 1800, 25, '2024-01-14', 8000, 92, 1, 'https://example.com/images/mike-profile.jpg', 'Product manager with expertise in SaaS platforms and user experience design.', 'ProductLabs', '{\"linkedin\": \"https://linkedin.com/in/mikerodriguez\", \"portfolio\": \"https://mikerodriguez.design\"}', 'Spain', 'Barcelona', 'Europe/Madrid', 1, 0, '', 'en', 'Europe/Madrid', 'light', 1, 0, 1, 0, 1, 0, 1, 'weekly', 1, '21:00', '07:00', '2023-05-20 11:10:00', '2024-01-14 16:45:00'),
(14, 'Emily', 'Watson', 'emily.watson@startup.com', '$2b$12$P0x1e4B.TEXKzm2O1n0xP2S3wBB3wU1n1G9hE9TB1BgAe0yO8vBjF', 1, '2024-01-15 08:20:00', 'active', '', 2500, 60, '2024-01-15', 12000, 96.8, 1, 'https://example.com/images/emily-profile.jpg', 'Full-stack developer specializing in React, Node.js, and cloud architecture.', 'DevCraft Studios', '{\"github\": \"https://github.com/emilywatson\", \"linkedin\": \"https://linkedin.com/in/emilywatson\", \"twitter\": \"https://twitter.com/emilydev\"}', 'United Kingdom', 'London', 'Europe/London', 1, 1, 'public', 'en', 'Europe/London', 'dark', 1, 1, 0, 0, 0, 1, 1, '', 0, '22:00', '08:00', '2023-02-10 09:45:00', '2024-01-15 08:20:00'),
(15, 'Alex', 'Kumar', 'alex.kumar@startup.com', '$2b$12$Q1y2f5C.UFYLAn3P2o1yQ3T4xCC4xV2o2H0iF0UC2ChBf1zP9wCkG', 1, '2024-01-13 14:30:00', 'active', '', 1500, 15, '2024-01-13', 6000, 85.5, 0, 'https://example.com/images/alex-profile.jpg', 'Digital marketing expert focused on growth hacking and content strategy for tech startups.', 'GrowthHack Media', '{\"linkedin\": \"https://linkedin.com/in/alexkumar\", \"twitter\": \"https://twitter.com/alexgrowth\", \"instagram\": \"https://instagram.com/alexkumar\"}', 'India', 'Bangalore', 'Asia/Kolkata', 1, 1, 'public', 'en', 'Asia/Kolkata', 'light', 1, 1, 1, 1, 1, 1, 1, 'daily', 1, '23:30', '09:00', '2023-07-05 16:20:00', '2024-01-13 14:30:00'),
(16, 'David', 'Wilson', 'david.wilson@startup.com', '$2b$12$R2z3g6D.VGZMBo4Q3p2zR4U5yDD5yW3p3I1jG1VD3DiCg2A0x1DlH', 1, '2024-01-05 11:00:00', '', 'member', 800, 0, '2024-01-05', 3000, 75, 0, 'https://example.com/images/david-profile.jpg', 'Former startup advisor taking a break from the ecosystem.', NULL, '{\"linkedin\": \"https://linkedin.com/in/davidwilson\"}', 'Australia', 'Sydney', 'Australia/Sydney', 0, 0, 'private', 'en', 'Australia/Sydney', 'light', 0, 0, 0, 0, 0, 0, 0, '', 0, '22:00', '08:00', '2023-04-12 10:15:00', '2024-01-10 09:00:00'),
(17, 'Lisa', 'Johnson', 'lisa.johnson@startup.com', '$2b$12$S3a4h7E.WHAMCp5R4q3aT5V6zEE6zX4q4J2kH2WE4EjDh3B1y2EmI', 0, NULL, 'active', 'member', 100, 1, '2024-01-15', 0, 100, 0, NULL, NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2024-01-15 12:00:00', '2024-01-15 12:00:00'),
(18, 'Robert', 'Thompson', 'robert.thompson@startup.com', '$2b$12$T4b5i8F.XIBNQq6S5r4bU6W7aFF7aY5r5K3lI3XF5FkEi4C2z3FnJ', 1, '2024-01-14 17:20:00', 'active', 'investor', 4200, 90, '2024-01-14', 50000, 91.2, 0, 'https://example.com/images/robert-profile.jpg', 'Angel investor focused on early-stage tech startups. Always looking for innovative ideas.', 'Thompson Ventures', '{\"linkedin\": \"https://linkedin.com/in/robertthompson\", \"twitter\": \"https://twitter.com/robthompsonvc\", \"website\": \"https://thompsonventures.com\"}', 'United States', 'New York', 'America/New_York', 1, 1, '', 'en', 'America/New_York', 'dark', 1, 0, 1, 1, 1, 0, 0, 'daily', 1, '20:00', '06:00', '2022-11-08 13:45:00', '2024-01-14 17:20:00'),
(19, 'Maria', 'Garcia', 'maria.garcia@startup.com', '$2b$12$U5c6j9G.YJCOTr7T6s5cV7X8bGG8bZ6s6L4mJ4YG6GlFj5D3a4GoK', 1, '2024-01-15 11:30:00', 'active', '', 1900, 22, '2024-01-15', 7500, 89.5, 1, 'https://example.com/images/maria-profile.jpg', 'UI/UX designer passionate about creating beautiful and functional interfaces.', 'DesignCraft Studio', '{\"behance\": \"https://behance.net/mariagarcia\", \"dribbble\": \"https://dribbble.com/mariagarcia\"}', 'Mexico', 'Mexico City', 'America/Mexico_City', 1, 1, 'public', 'es', 'America/Mexico_City', 'light', 1, 1, 1, 0, 1, 1, 1, 'weekly', 0, '23:00', '08:00', '2023-06-18 15:20:00', '2024-01-15 11:30:00'),
(20, 'James', 'Lee', 'james.lee@startup.com', '$2b$12$V6d7k0H.ZKDPSu8U7t6dW8Y9cHH9cA7t7M5nK5ZH7HmGk6E4b5HpL', 1, '2024-01-14 13:45:00', 'active', '', 2800, 40, '2024-01-14', 11000, 94.2, 1, 'https://example.com/images/james-profile.jpg', 'Backend developer specializing in microservices and database architecture.', 'CodeForge Solutions', '{\"github\": \"https://github.com/jameslee\", \"linkedin\": \"https://linkedin.com/in/jameslee\"}', 'South Korea', 'Seoul', 'Asia/Seoul', 1, 0, '', 'ko', 'Asia/Seoul', 'dark', 1, 0, 0, 0, 0, 0, 1, '', 1, '00:00', '09:00', '2023-03-22 08:30:00', '2024-01-14 13:45:00'),
(100, 'Mohamed', 'Dhimni', 'mohameddhimni311@gmail.com', 'scrypt:32768:8:1$k33uICRwHJuqIN7v$b575b790a096bd99a112cd1ad20b0d65c6e360da3e6983823405298c7833392102cad8c9bf370bfde137178f561e50cdce7dddfa1ece32d01fcac3b0ffa32622', 1, '2025-11-29 03:33:10', 'active', 'member', 0, 0, '2025-11-29', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocKWikJW89KC1-jcYZqnOimQSUVKZGF-MH379Jikz1maz_33FQ=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-11-28 02:24:03', '2025-11-29 03:33:10'),
(101, 'Aung', 'Marma', 'aungmarma582@gmail.com', 'scrypt:32768:8:1$id1nTJheh5PXBFwy$762ed30483c49dc808951de0e16f700cf142e7456dd1904e7d0e858cbe2f38c2b37dd5c816aa1a188771098d7c61b064197bc06b30d0071daf1fc6e5ae0e6c45', 1, '2025-11-28 03:25:32', 'active', 'member', 0, 0, '2025-11-28', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocIXgcQroBTmAZJ-M5qWrbtW_dkLLn_u0lIirTtI9Hhl_DLGIQ=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-11-28 03:25:32', '2025-11-28 03:25:33'),
(102, 'George ', 'Zaher', 'zahergeorge00@gmail.com', 'scrypt:32768:8:1$GSiGFnMKqzjwxkMX$5cbd50d1f8c10d5128ed190532865c15561e8073cb5eabde56cce1fb090458eff57777485d9432cbec2943aa955ee504f9cb86bec9b456655825ffbde083114d', 0, '2025-11-28 18:06:51', 'active', 'member', 0, 0, '2025-11-28', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocIJ5S5u53qsbdQR9kvMH7lMnm4ZG7RkQv8FzfJgEHj82tdYBA=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-11-28 18:05:01', '2025-11-28 18:06:51'),
(103, 'Hfxx', 'Cxsjbb', 'cxsjbbhfxx@gmail.com', 'scrypt:32768:8:1$dxFxvKC7maLX4pOW$1a0923b44efd17406651268c03b68dbad6f75eccfbe69702c28d48c4d049155fa012537701f5164302491667feeba098ca1e0be568d8e9ae89c315153a7bebce', 1, '2025-11-28 18:07:42', 'active', 'member', 0, 0, '2025-11-28', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocJNiTLqthO-ybVz1IRN3c4gwyZ1235pb2QlQD2hqMIgJMskZg=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-11-28 18:06:00', '2025-11-28 18:07:42'),
(104, 'MOHAMMED', 'DHIMNI', 'dhimnimohammed885@gmail.com', 'scrypt:32768:8:1$dtFtQoxJz2p9D1s2$47749aad553d96e63727b4ddc2e28d45c2f24dc4a176c5fc0f549d12fb63e3ad0c0361443c0c7a2bf9e08d08b37f8332d1c514d50d22a5c0f3270f01f2f888a8', 1, '2025-12-01 19:51:52', 'active', 'member', 0, 0, '2025-12-01', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocLnTyUMJA0bBCZzwQwoVK0ZwaKV9DSxb9OVXlR3e4EL7Eyktg=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-11-28 18:16:37', '2025-12-01 19:51:52'),
(105, 'Krystian', '', 'krystian09536@gmail.com', 'scrypt:32768:8:1$x2re4v7K1Hz5HgJB$37e7e7363dbe4b39dab239bb2d72b3861e385336ad0f370bb2b4eb49e26742ee735019555746df18f639dcf0ff27d1c5f0b3e1fd0d308010ca7ec203da880960', 1, '2025-11-28 20:15:57', 'active', 'member', 0, 0, '2025-11-28', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocKS1J7GrRB2PgPzHrP5w9kLu6x5ne0f3fh4GMyaaLfDBrxSjQ=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-11-28 20:11:41', '2025-11-28 20:15:57'),
(106, 'Mujib', 'Azeez', 'gbolahunazeez1305@gmail.com', 'scrypt:32768:8:1$paTqtjkEgsBKplMT$76a137f8e1a4eac49f45c89996d19092e65925b96f3bdf76b96c5b3583ea033572c362633aaa6f83508e3b91c3ddc3d024625a18ad886348a382a4b69cdff081', 1, '2025-12-01 17:59:40', 'active', 'member', 0, 0, '2025-12-01', 0, 100, 0, 'https://lh3.googleusercontent.com/a/ACg8ocIxMWhBoszfjmF0SCdP5rxcywBh0nBzRgttCFuna6MMY8vFGRk=s96-c', NULL, NULL, '{}', NULL, NULL, NULL, 1, 1, 'public', 'en', 'UTC', 'light', 1, 1, 1, 1, 1, 1, 1, 'weekly', 0, '22:00', '08:00', '2025-12-01 17:52:28', '2025-12-01 17:59:40');

-- --------------------------------------------------------

--
-- Structure de la table `user_achievements`
--

CREATE TABLE IF NOT EXISTS `user_achievements` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `achievement_id` int(11) NOT NULL,
  `unlocked_at` datetime DEFAULT NULL,
  `progress_percentage` int(11) DEFAULT NULL,
  `is_completed` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `achievements`
--
ALTER TABLE `achievements`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `calendar_events`
--
ALTER TABLE `calendar_events`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `startup_id` (`startup_id`);

--
-- Index pour la table `chat_conversations`
--
ALTER TABLE `chat_conversations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `created_by_id` (`created_by_id`);

--
-- Index pour la table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD PRIMARY KEY (`id`),
  ADD KEY `sender_id` (`sender_id`),
  ADD KEY `reply_to_id` (`reply_to_id`),
  ADD KEY `conversation_id` (`conversation_id`);

--
-- Index pour la table `conversation_participants`
--
ALTER TABLE `conversation_participants`
  ADD KEY `conversation_id` (`conversation_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `conversation_user_reads`
--
ALTER TABLE `conversation_user_reads`
  ADD KEY `conversation_id` (`conversation_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `goal_milestones`
--
ALTER TABLE `goal_milestones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `goal_id` (`goal_id`);

--
-- Index pour la table `growth_metrics`
--
ALTER TABLE `growth_metrics`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `startup_id` (`startup_id`);

--
-- Index pour la table `ideas`
--
ALTER TABLE `ideas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `creator_id` (`creator_id`);

--
-- Index pour la table `idea_bookmarks`
--
ALTER TABLE `idea_bookmarks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idea_id` (`idea_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `idea_comments`
--
ALTER TABLE `idea_comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idea_id` (`idea_id`),
  ADD KEY `author_id` (`author_id`);

--
-- Index pour la table `join_requests`
--
ALTER TABLE `join_requests`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `startup_id` (`startup_id`);

--
-- Index pour la table `knowledge`
--
ALTER TABLE `knowledge`
  ADD PRIMARY KEY (`id`),
  ADD KEY `author_id` (`author_id`);

--
-- Index pour la table `knowledge_bookmarks`
--
ALTER TABLE `knowledge_bookmarks`
  ADD PRIMARY KEY (`id`),
  ADD KEY `knowledge_id` (`knowledge_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `knowledge_comments`
--
ALTER TABLE `knowledge_comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `resource_id` (`resource_id`);

--
-- Index pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `author_id` (`author_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `post_comments`
--
ALTER TABLE `post_comments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `author_id` (`author_id`);

--
-- Index pour la table `post_likes`
--
ALTER TABLE `post_likes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Index pour la table `post_media`
--
ALTER TABLE `post_media`
  ADD PRIMARY KEY (`id`),
  ADD KEY `post_id` (`post_id`);

--
-- Index pour la table `project_goals`
--
ALTER TABLE `project_goals`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `startup_id` (`startup_id`);

--
-- Index pour la table `refresh_tokens`
--
ALTER TABLE `refresh_tokens`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `resource_downloads`
--
ALTER TABLE `resource_downloads`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `resource_likes`
--
ALTER TABLE `resource_likes`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `resource_views`
--
ALTER TABLE `resource_views`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `startups`
--
ALTER TABLE `startups`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `startup_bookmarks`
--
ALTER TABLE `startup_bookmarks`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `startup_documents`
--
ALTER TABLE `startup_documents`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `startup_members`
--
ALTER TABLE `startup_members`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `stories`
--
ALTER TABLE `stories`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `story_views`
--
ALTER TABLE `story_views`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `suggestions`
--
ALTER TABLE `suggestions`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `tasks`
--
ALTER TABLE `tasks`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `team_members`
--
ALTER TABLE `team_members`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `team_performance`
--
ALTER TABLE `team_performance`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `user_achievements`
--
ALTER TABLE `user_achievements`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `achievements`
--
ALTER TABLE `achievements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=235;
--
-- AUTO_INCREMENT pour la table `calendar_events`
--
ALTER TABLE `calendar_events`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;
--
-- AUTO_INCREMENT pour la table `chat_conversations`
--
ALTER TABLE `chat_conversations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=115;
--
-- AUTO_INCREMENT pour la table `chat_messages`
--
ALTER TABLE `chat_messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=101;
--
-- AUTO_INCREMENT pour la table `goal_milestones`
--
ALTER TABLE `goal_milestones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `growth_metrics`
--
ALTER TABLE `growth_metrics`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `ideas`
--
ALTER TABLE `ideas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
--
-- AUTO_INCREMENT pour la table `idea_bookmarks`
--
ALTER TABLE `idea_bookmarks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `idea_comments`
--
ALTER TABLE `idea_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `join_requests`
--
ALTER TABLE `join_requests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `knowledge`
--
ALTER TABLE `knowledge`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `knowledge_bookmarks`
--
ALTER TABLE `knowledge_bookmarks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `knowledge_comments`
--
ALTER TABLE `knowledge_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
--
-- AUTO_INCREMENT pour la table `posts`
--
ALTER TABLE `posts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `post_comments`
--
ALTER TABLE `post_comments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `post_likes`
--
ALTER TABLE `post_likes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `post_media`
--
ALTER TABLE `post_media`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `project_goals`
--
ALTER TABLE `project_goals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `refresh_tokens`
--
ALTER TABLE `refresh_tokens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;
--
-- AUTO_INCREMENT pour la table `resource_downloads`
--
ALTER TABLE `resource_downloads`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `resource_likes`
--
ALTER TABLE `resource_likes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `resource_views`
--
ALTER TABLE `resource_views`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `startups`
--
ALTER TABLE `startups`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;
--
-- AUTO_INCREMENT pour la table `startup_bookmarks`
--
ALTER TABLE `startup_bookmarks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `startup_documents`
--
ALTER TABLE `startup_documents`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
--
-- AUTO_INCREMENT pour la table `startup_members`
--
ALTER TABLE `startup_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT pour la table `stories`
--
ALTER TABLE `stories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `story_views`
--
ALTER TABLE `story_views`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `suggestions`
--
ALTER TABLE `suggestions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `tasks`
--
ALTER TABLE `tasks`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `team_members`
--
ALTER TABLE `team_members`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `team_performance`
--
ALTER TABLE `team_performance`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT pour la table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=107;
--
-- AUTO_INCREMENT pour la table `user_achievements`
--
ALTER TABLE `user_achievements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `calendar_events`
--
ALTER TABLE `calendar_events`
  ADD CONSTRAINT `calendar_events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `calendar_events_ibfk_2` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`);

--
-- Contraintes pour la table `chat_conversations`
--
ALTER TABLE `chat_conversations`
  ADD CONSTRAINT `chat_conversations_ibfk_1` FOREIGN KEY (`created_by_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `chat_messages`
--
ALTER TABLE `chat_messages`
  ADD CONSTRAINT `chat_messages_ibfk_1` FOREIGN KEY (`sender_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `chat_messages_ibfk_2` FOREIGN KEY (`reply_to_id`) REFERENCES `chat_messages` (`id`),
  ADD CONSTRAINT `chat_messages_ibfk_3` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`);

--
-- Contraintes pour la table `conversation_participants`
--
ALTER TABLE `conversation_participants`
  ADD CONSTRAINT `conversation_participants_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  ADD CONSTRAINT `conversation_participants_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `conversation_user_reads`
--
ALTER TABLE `conversation_user_reads`
  ADD CONSTRAINT `conversation_user_reads_ibfk_1` FOREIGN KEY (`conversation_id`) REFERENCES `chat_conversations` (`id`),
  ADD CONSTRAINT `conversation_user_reads_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `goal_milestones`
--
ALTER TABLE `goal_milestones`
  ADD CONSTRAINT `goal_milestones_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `goal_milestones_ibfk_2` FOREIGN KEY (`goal_id`) REFERENCES `project_goals` (`id`);

--
-- Contraintes pour la table `growth_metrics`
--
ALTER TABLE `growth_metrics`
  ADD CONSTRAINT `growth_metrics_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `growth_metrics_ibfk_2` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`);

--
-- Contraintes pour la table `ideas`
--
ALTER TABLE `ideas`
  ADD CONSTRAINT `ideas_ibfk_1` FOREIGN KEY (`creator_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `idea_bookmarks`
--
ALTER TABLE `idea_bookmarks`
  ADD CONSTRAINT `idea_bookmarks_ibfk_1` FOREIGN KEY (`idea_id`) REFERENCES `ideas` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `idea_bookmarks_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `idea_comments`
--
ALTER TABLE `idea_comments`
  ADD CONSTRAINT `idea_comments_ibfk_1` FOREIGN KEY (`idea_id`) REFERENCES `ideas` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `idea_comments_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `join_requests`
--
ALTER TABLE `join_requests`
  ADD CONSTRAINT `join_requests_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `join_requests_ibfk_2` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `knowledge`
--
ALTER TABLE `knowledge`
  ADD CONSTRAINT `knowledge_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `knowledge_bookmarks`
--
ALTER TABLE `knowledge_bookmarks`
  ADD CONSTRAINT `knowledge_bookmarks_ibfk_1` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `knowledge_bookmarks_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `knowledge_comments`
--
ALTER TABLE `knowledge_comments`
  ADD CONSTRAINT `knowledge_comments_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `knowledge_comments_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `knowledge` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `posts`
--
ALTER TABLE `posts`
  ADD CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `posts_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `post_comments`
--
ALTER TABLE `post_comments`
  ADD CONSTRAINT `post_comments_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `post_comments_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`);

--
-- Contraintes pour la table `post_likes`
--
ALTER TABLE `post_likes`
  ADD CONSTRAINT `post_likes_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `post_likes_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `post_media`
--
ALTER TABLE `post_media`
  ADD CONSTRAINT `post_media_ibfk_1` FOREIGN KEY (`post_id`) REFERENCES `posts` (`id`) ON DELETE CASCADE;

--
-- Contraintes pour la table `project_goals`
--
ALTER TABLE `project_goals`
  ADD CONSTRAINT `project_goals_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `project_goals_ibfk_2` FOREIGN KEY (`startup_id`) REFERENCES `startups` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
