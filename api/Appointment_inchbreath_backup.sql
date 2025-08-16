-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: e4uqm9.h.filess.io    Database: Appointment_inchbreath
-- ------------------------------------------------------
-- Server version	8.0.36-28

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

--
-- Table structure for table `appointments`
--

DROP TABLE IF EXISTS `appointments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appointments` (
  `appointment_id` int NOT NULL AUTO_INCREMENT,
  `business_user_id` int NOT NULL,
  `patient_id` int NOT NULL,
  `doctor_id` int NOT NULL,
  `appointment_number` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `appointment_date` date DEFAULT NULL,
  `appointment_time` datetime DEFAULT NULL,
  `appointment_type` enum('Consultation','Follow-up','Emergency','Surgery','Checkup') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `appointment_status` enum('Scheduled','Confirmed','Completed','Cancelled','No-show') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `symptoms` text COLLATE utf8mb4_general_ci,
  `diagnosis` text COLLATE utf8mb4_general_ci,
  `prescription` text COLLATE utf8mb4_general_ci,
  `notes` text COLLATE utf8mb4_general_ci,
  `consultation_fee` decimal(10,2) DEFAULT NULL,
  `payment_status` enum('Pending','Paid','Partial') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`appointment_id`),
  UNIQUE KEY `appointment_number` (`appointment_number`),
  KEY `business_user_id` (`business_user_id`),
  KEY `patient_id` (`patient_id`),
  KEY `doctor_id` (`doctor_id`),
  KEY `ix_appointments_appointment_id` (`appointment_id`),
  CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`business_user_id`) REFERENCES `business_users` (`business_user_id`),
  CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`patient_id`),
  CONSTRAINT `appointments_ibfk_3` FOREIGN KEY (`doctor_id`) REFERENCES `staff` (`staff_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appointments`
--

LOCK TABLES `appointments` WRITE;
/*!40000 ALTER TABLE `appointments` DISABLE KEYS */;
/*!40000 ALTER TABLE `appointments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `audit_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `business_user_id` int DEFAULT NULL,
  `action_type` enum('CREATE','UPDATE','DELETE','LOGIN','LOGOUT','EXPORT','IMPORT','PAYMENT','BOOKING','CANCELLATION') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `table_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `record_id` int DEFAULT NULL,
  `old_values` json DEFAULT NULL,
  `new_values` json DEFAULT NULL,
  `ip_address` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `user_agent` text COLLATE utf8mb4_general_ci,
  `session_id` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  PRIMARY KEY (`audit_id`),
  KEY `user_id` (`user_id`),
  KEY `business_user_id` (`business_user_id`),
  KEY `ix_audit_logs_audit_id` (`audit_id`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `audit_logs_ibfk_2` FOREIGN KEY (`business_user_id`) REFERENCES `business_users` (`business_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bookings`
--

DROP TABLE IF EXISTS `bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `business_user_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `room_id` int NOT NULL,
  `booking_number` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `check_in_date` datetime NOT NULL,
  `check_out_date` datetime NOT NULL,
  `check_in_time` datetime DEFAULT NULL,
  `check_out_time` datetime DEFAULT NULL,
  `total_nights` int DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `advance_amount` decimal(10,2) DEFAULT NULL,
  `payment_status` enum('Pending','Paid','Partial','Refunded') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `booking_status` enum('Confirmed','Cancelled','Completed','No-show','Checked-in','Checked-out') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `special_requests` text COLLATE utf8mb4_general_ci,
  `cancellation_reason` text COLLATE utf8mb4_general_ci,
  `cancelled_by` int DEFAULT NULL,
  `cancelled_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`booking_id`),
  UNIQUE KEY `booking_number` (`booking_number`),
  KEY `business_user_id` (`business_user_id`),
  KEY `customer_id` (`customer_id`),
  KEY `room_id` (`room_id`),
  KEY `cancelled_by` (`cancelled_by`),
  KEY `ix_bookings_booking_id` (`booking_id`),
  CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`business_user_id`) REFERENCES `business_users` (`business_user_id`),
  CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`room_id`),
  CONSTRAINT `bookings_ibfk_4` FOREIGN KEY (`cancelled_by`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bookings`
--

LOCK TABLES `bookings` WRITE;
/*!40000 ALTER TABLE `bookings` DISABLE KEYS */;
/*!40000 ALTER TABLE `bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `business_categories`
--

DROP TABLE IF EXISTS `business_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `business_categories` (
  `business_category_id` int NOT NULL AUTO_INCREMENT,
  `business_type_id` int NOT NULL,
  `business_category_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `business_category_short_name` varchar(300) COLLATE utf8mb4_general_ci NOT NULL,
  `business_category_code` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `business_category_media` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `icon` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `business_category_description` text COLLATE utf8mb4_general_ci,
  `added_by` int DEFAULT NULL,
  `added_on` datetime NOT NULL DEFAULT (now()),
  `modified_by` int DEFAULT NULL,
  `modified_on` datetime NOT NULL DEFAULT (now()),
  `is_deleted` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `deleted_by` int DEFAULT NULL,
  `deleted_on` datetime DEFAULT NULL,
  PRIMARY KEY (`business_category_id`),
  KEY `business_type_id` (`business_type_id`),
  KEY `ix_business_categories_business_category_id` (`business_category_id`),
  CONSTRAINT `business_categories_ibfk_1` FOREIGN KEY (`business_type_id`) REFERENCES `business_types` (`business_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `business_categories`
--

LOCK TABLES `business_categories` WRITE;
/*!40000 ALTER TABLE `business_categories` DISABLE KEYS */;
/*!40000 ALTER TABLE `business_categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `business_types`
--

DROP TABLE IF EXISTS `business_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `business_types` (
  `business_type_id` int NOT NULL AUTO_INCREMENT,
  `type_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `description` text COLLATE utf8mb4_general_ci,
  `business_media` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `icon` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `color` varchar(7) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `features` text COLLATE utf8mb4_general_ci,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`business_type_id`),
  UNIQUE KEY `type_name` (`type_name`),
  KEY `ix_business_types_business_type_id` (`business_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `business_types`
--

LOCK TABLES `business_types` WRITE;
/*!40000 ALTER TABLE `business_types` DISABLE KEYS */;
/*!40000 ALTER TABLE `business_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `business_users`
--

DROP TABLE IF EXISTS `business_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `business_users` (
  `business_user_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `business_type_id` int NOT NULL,
  `business_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `business_description` text COLLATE utf8mb4_general_ci,
  `business_logo` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `business_banner` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `business_address` text COLLATE utf8mb4_general_ci,
  `business_phone` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `business_email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `business_website` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `gst_number` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `pan_number` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `business_license` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `subscription_plan` enum('FREE','BASIC','PREMIUM','ENTERPRISE') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `subscription_status` enum('Active','Inactive','Expired','Suspended') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `subscription_start_date` datetime DEFAULT NULL,
  `subscription_end_date` datetime DEFAULT NULL,
  `monthly_limit` int DEFAULT NULL,
  `current_month_usage` int DEFAULT NULL,
  `is_verified` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `is_featured` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `rating` decimal(3,2) DEFAULT NULL,
  `total_reviews` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `updated_at` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`business_user_id`),
  KEY `user_id` (`user_id`),
  KEY `business_type_id` (`business_type_id`),
  KEY `ix_business_users_business_user_id` (`business_user_id`),
  CONSTRAINT `business_users_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `business_users_ibfk_2` FOREIGN KEY (`business_type_id`) REFERENCES `business_types` (`business_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `business_users`
--

LOCK TABLES `business_users` WRITE;
/*!40000 ALTER TABLE `business_users` DISABLE KEYS */;
/*!40000 ALTER TABLE `business_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `catering_orders`
--

DROP TABLE IF EXISTS `catering_orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `catering_orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `business_user_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `order_number` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `order_date` datetime DEFAULT NULL,
  `delivery_date` datetime DEFAULT NULL,
  `delivery_time` datetime DEFAULT NULL,
  `delivery_address` text COLLATE utf8mb4_general_ci,
  `guest_count` int DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `order_status` enum('Pending','Confirmed','In Progress','Delivered','Cancelled') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `special_instructions` text COLLATE utf8mb4_general_ci,
  `delivery_charges` decimal(10,2) DEFAULT NULL,
  `tax_amount` decimal(10,2) DEFAULT NULL,
  `discount_amount` decimal(10,2) DEFAULT NULL,
  `final_amount` decimal(10,2) DEFAULT NULL,
  `payment_status` enum('Pending','Paid','Partial') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`order_id`),
  UNIQUE KEY `order_number` (`order_number`),
  KEY `business_user_id` (`business_user_id`),
  KEY `customer_id` (`customer_id`),
  KEY `ix_catering_orders_order_id` (`order_id`),
  CONSTRAINT `catering_orders_ibfk_1` FOREIGN KEY (`business_user_id`) REFERENCES `business_users` (`business_user_id`),
  CONSTRAINT `catering_orders_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `catering_orders`
--

LOCK TABLES `catering_orders` WRITE;
/*!40000 ALTER TABLE `catering_orders` DISABLE KEYS */;
/*!40000 ALTER TABLE `catering_orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `customer_id` int NOT NULL AUTO_INCREMENT,
  `business_user_id` int NOT NULL,
  `full_name` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `id_proof_type` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `id_proof_number` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_general_ci,
  `emergency_contact` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `emergency_contact_name` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `customer_type` enum('Regular','VIP','Student','Corporate') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `total_bookings` int DEFAULT NULL,
  `total_spent` decimal(10,2) DEFAULT NULL,
  `last_visit_date` datetime DEFAULT NULL,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`customer_id`),
  KEY `business_user_id` (`business_user_id`),
  KEY `ix_customers_customer_id` (`customer_id`),
  CONSTRAINT `customers_ibfk_1` FOREIGN KEY (`business_user_id`) REFERENCES `business_users` (`business_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_otps`
--

DROP TABLE IF EXISTS `email_otps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_otps` (
  `otp_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `email` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `otp_hash` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `purpose` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `attempts` int NOT NULL,
  `is_used` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT (now()),
  `expires_at` datetime NOT NULL,
  `used_at` datetime DEFAULT NULL,
  `last_sent_at` datetime DEFAULT NULL,
  `send_count` int NOT NULL,
  PRIMARY KEY (`otp_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_email_otps_email` (`email`),
  KEY `ix_email_otps_otp_id` (`otp_id`),
  CONSTRAINT `email_otps_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_otps`
--

LOCK TABLES `email_otps` WRITE;
/*!40000 ALTER TABLE `email_otps` DISABLE KEYS */;
/*!40000 ALTER TABLE `email_otps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `garage_bookings`
--

DROP TABLE IF EXISTS `garage_bookings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `garage_bookings` (
  `booking_id` int NOT NULL AUTO_INCREMENT,
  `business_user_id` int NOT NULL,
  `customer_id` int NOT NULL,
  `vehicle_id` int NOT NULL,
  `service_id` int NOT NULL,
  `booking_number` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `booking_date` date DEFAULT NULL,
  `booking_time` datetime DEFAULT NULL,
  `estimated_duration` int DEFAULT NULL,
  `total_amount` decimal(10,2) DEFAULT NULL,
  `status` enum('Scheduled','In Progress','Completed','Cancelled') COLLATE utf8mb4_general_ci DEFAULT NULL,
  `notes` text COLLATE utf8mb4_general_ci,
  `technician_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`booking_id`),
  UNIQUE KEY `booking_number` (`booking_number`),
  KEY `business_user_id` (`business_user_id`),
  KEY `customer_id` (`customer_id`),
  KEY `vehicle_id` (`vehicle_id`),
  KEY `service_id` (`service_id`),
  KEY `technician_id` (`technician_id`),
  KEY `ix_garage_bookings_booking_id` (`booking_id`),
  CONSTRAINT `garage_bookings_ibfk_1` FOREIGN KEY (`business_user_id`) REFERENCES `business_users` (`business_user_id`),
  CONSTRAINT `garage_bookings_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  CONSTRAINT `garage_bookings_ibfk_3` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicles` (`vehicle_id`),
  CONSTRAINT `garage_bookings_ibfk_4` FOREIGN KEY (`service_id`) REFERENCES `services` (`service_id`),
  CONSTRAINT `garage_bookings_ibfk_5` FOREIGN KEY (`technician_id`) REFERENCES `staff` (`staff_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `garage_bookings`
--

LOCK TABLES `garage_bookings` WRITE;
/*!40000 ALTER TABLE `garage_bookings` DISABLE KEYS */;
/*!40000 ALTER TABLE `garage_bookings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location_active_pincodes`
--

DROP TABLE IF EXISTS `location_active_pincodes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location_active_pincodes` (
  `pincode_id` int NOT NULL AUTO_INCREMENT,
  `pincode` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `location_id` int NOT NULL,
  `location_status` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `added_by` int DEFAULT NULL,
  `added_on` datetime NOT NULL DEFAULT (now()),
  `modified_by` int DEFAULT NULL,
  `modified_on` datetime NOT NULL DEFAULT (now()),
  `deleted_by` int DEFAULT NULL,
  `deleted_on` datetime DEFAULT NULL,
  `is_deleted` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`pincode_id`),
  UNIQUE KEY `ix_location_active_pincodes_pincode` (`pincode`),
  KEY `location_id` (`location_id`),
  KEY `ix_location_active_pincodes_pincode_id` (`pincode_id`),
  CONSTRAINT `location_active_pincodes_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location_master` (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location_active_pincodes`
--

LOCK TABLES `location_active_pincodes` WRITE;
/*!40000 ALTER TABLE `location_active_pincodes` DISABLE KEYS */;
/*!40000 ALTER TABLE `location_active_pincodes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location_master`
--

DROP TABLE IF EXISTS `location_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location_master` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `location_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `location_city_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `location_dist_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `location_state_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `location_country_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `location_desc` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `added_by` int DEFAULT NULL,
  `added_on` datetime NOT NULL DEFAULT (now()),
  `modified_by` int DEFAULT NULL,
  `modified_on` datetime NOT NULL DEFAULT (now()),
  `deleted_by` int DEFAULT NULL,
  `deleted_on` datetime DEFAULT NULL,
  `is_deleted` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`location_id`),
  UNIQUE KEY `ix_location_master_location_name` (`location_name`),
  KEY `ix_location_master_location_id` (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location_master`
--

LOCK TABLES `location_master` WRITE;
/*!40000 ALTER TABLE `location_master` DISABLE KEYS */;
/*!40000 ALTER TABLE `location_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `location_user_addresses`
--

DROP TABLE IF EXISTS `location_user_addresses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location_user_addresses` (
  `user_address_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `location_id` int NOT NULL,
  `pincode_id` int NOT NULL,
  `address_line1` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `address_line2` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `city` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `pincode` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `longitude` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `latitude` varchar(20) COLLATE utf8mb4_general_ci NOT NULL,
  `map_location_url` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `address_type` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `is_default` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `is_active` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  `added_by` int DEFAULT NULL,
  `added_on` datetime NOT NULL DEFAULT (now()),
  `modified_by` int DEFAULT NULL,
  `modified_on` datetime NOT NULL DEFAULT (now()),
  `deleted_by` int DEFAULT NULL,
  `deleted_on` datetime DEFAULT NULL,
  `is_deleted` enum('Y','N') COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`user_address_id`),
  UNIQUE KEY `ix_location_user_addresses_address_line1` (`address_line1`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  KEY `pincode_id` (`pincode_id`),
  KEY `ix_location_user_addresses_user_address_id` (`user_address_id`),
  CONSTRAINT `location_user_addresses_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `location_user_addresses_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `location_master` (`location_id`),
  CONSTRAINT `location_user_addresses_ibfk_3` FOREIGN KEY (`pincode_id`) REFERENCES `location_active_pincodes` (`pincode_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location_user_addresses`
--

LOCK TABLES `location_user_addresses` WRITE;
/*!40000 ALTER TABLE `location_user_addresses` DISABLE KEYS */;
