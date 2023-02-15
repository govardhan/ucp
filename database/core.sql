CREATE DATABASE IF NOT EXISTS core CHARACTER SET 'utf8';

USE core;

CREATE TABLE `tb_audio_prompts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `prompt_name` varchar(80) NOT NULL,
  `file_name` varchar(80) NOT NULL,
  `silence` int(11) NOT NULL DEFAULT '0',
  `dtmf_abort` varchar(40) NOT NULL DEFAULT '0123456789*#',
  `rep_count` int(11) NOT NULL DEFAULT '0',
  `action` varchar(100) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_cdr` (
  `uuid` varchar(40) NOT NULL DEFAULT '',
  `source` varchar(40) DEFAULT NULL,
  `src_telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `dialed_number` varchar(40) DEFAULT NULL,
  `destination` varchar(40) DEFAULT NULL,
  `dst_telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `feature_name` varchar(40) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `end_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `call_duration` varchar(40) DEFAULT NULL,
  `call_complete_type` enum('user_hangup','release','aborted') NOT NULL DEFAULT 'release',
  PRIMARY KEY (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_content` (
  `content_id` int(11) NOT NULL AUTO_INCREMENT,
  `msisdn` varchar(15) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `media_type` enum('text','audio','image','video') NOT NULL DEFAULT 'audio',
  `state` enum('new','old','del','save','abuse') NOT NULL DEFAULT 'new',
  `type` enum('tweet','selftweet','rep2tweet','rep2rep','share','name') NOT NULL DEFAULT 'tweet',
  `content` text,
  `create_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ttl` smallint(6) DEFAULT '10' COMMENT 'in days',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `length` smallint(6) NOT NULL,
  `tags` int(11) NOT NULL DEFAULT '1' COMMENT '1-all,2=friends,4=family,8=future_user',
  `ref_content_id` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`content_id`),
  KEY `content_msisdn_index` (`msisdn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_content_activity` (
  `activity_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `content_id` int(11) NOT NULL,
  `msisdn` varchar(15) NOT NULL,
  `activity` enum('like','rep2tweet','rep2rep','share','read','del','save','abuse') NOT NULL DEFAULT 'read',
  `activity_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`activity_id`),
  INDEX `content_id_index` (`content_id`),
  INDEX `content_action_msisdn_index` (`msisdn`),
  FOREIGN KEY (`content_id`) REFERENCES `tb_content` (`content_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_features` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `feature_name` varchar(40) DEFAULT NULL UNIQUE KEY,
  `feature_group` varchar(40) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_feature_map` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `in_pattern` varchar(20) DEFAULT NULL,
  `out_pattern` varchar(20) DEFAULT NULL,
  `telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `feature_name` varchar(40) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`feature_name`) REFERENCES `tb_features` (`feature_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_feature_profile` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `feature_name` varchar(40) NOT NULL DEFAULT '.*' COMMENT 'reg-ex',
  `telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `profile_key` varchar(40) DEFAULT NULL,
  `profile_value` varchar(40) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`feature_name`) REFERENCES `tb_features` (`feature_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_number_normalizer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `in_pattern` varchar(40) NOT NULL,
  `out_pattern` varchar(40) NOT NULL,
  `telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_number_denormalizer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `in_pattern` varchar(40) NOT NULL,
  `out_pattern` varchar(40) NOT NULL,
  `telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_number_telco_map` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `num_pattern` varchar(40) DEFAULT NULL,
  `telco_id` varchar(20) NOT NULL,
  `flags` varchar(40) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_relations` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `who` varchar(15) NOT NULL,
  `whom` varchar(15) NOT NULL,
  `relation` enum('one2one','follow','invite','barred','friend','family','tweet','reply','like','share') DEFAULT NULL,
  `state` enum('preactive','active','dormant','suspend','inactive','barred') DEFAULT NULL,
  `create_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `update_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  PRIMARY KEY (`id`),
  UNIQUE KEY `who` (`who`,`whom`,`relation`),
  KEY `tb_rel_who_index` (`who`),
  KEY `tb_rel_whom_index` (`whom`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_price` (
  `price_id` int(10) NOT NULL AUTO_INCREMENT,
  `price` int(10) NOT NULL,
  `duration` int(10) NOT NULL,
  `op_keyword1` varchar(40) DEFAULT NULL,
  `op_keyword2` varchar(40) DEFAULT NULL,
  `op_keyword3` varchar(40) DEFAULT NULL,
  `op_keyword4` varchar(40) DEFAULT NULL,
  `op_keyword5` varchar(40) DEFAULT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`price_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_services` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `service_name` varchar(40) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `price_id` int(10) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`price_id`) REFERENCES `tb_price` (`price_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_sms` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `template` varchar(40) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `lang` varchar(20) NOT NULL,
  `sms` varchar(20) NOT NULL,
  `sender_name` varchar(20) NOT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_subscription_cache` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `msisdn` varchar(15) NOT NULL,
  `service_name` varchar(40) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `price_id` int(10) NOT NULL,
  `state` enum('wait4op','completed') NOT NULL DEFAULT 'wait4op',
  `uuid` varchar(40) NOT NULL,
  `txn_id` varchar(40) DEFAULT NULL,
  `aux_data` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subcache_msisdn_service_name_uk` (`msisdn`,`service_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_content_provider` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `cp_name` varchar(40) NOT NULL ,
  `service_name` varchar(20) NOT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cp_name` (`cp_name`,`service_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_subscription` (
  `sub_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `msisdn` varchar(15) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `service_name` int(11) unsigned NOT NULL,
  `state` enum('presub','sub','renew','unsub','suspend','barred') DEFAULT 'presub',
  `presub_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `sub_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `renew_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `unsub_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `suspend_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `barred_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `updated_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`sub_id`),
  UNIQUE KEY `sub_msisdn_service_name_uk` (`msisdn`,`service_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_subscription_activity` (
  `sub_act_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `sub_id` int(11) unsigned NOT NULL,
  `msisdn` varchar(15) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `service_name` int(11) unsigned DEFAULT NULL,
  `activity` enum('presub','sub','trialsub','renew','unsub','suspend','barred') DEFAULT 'presub',
  `create_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`sub_act_id`),
  INDEX `sub_activity_sub_id_index` (`sub_id`),
  FOREIGN KEY (`sub_id`) REFERENCES `tb_subscription` (`sub_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `tb_telcos` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `telco_id` varchar(40) NOT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `telco_id` (`telco_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


CREATE TABLE `tb_telco_profile` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `telco_id` varchar(40) NOT NULL,
  `profile_key` varchar(40) NOT NULL,
  `profile_value` varchar(120) NOT NULL,
  `remarks` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `telco_id` (`telco_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


CREATE TABLE `tb_premium_tweeter_discovery` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `telco_id` varchar(20) NOT NULL DEFAULT '.*',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','web') NOT NULL DEFAULT 'ivr',
  `start_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `end_ts` timestamp NOT NULL DEFAULT '2020-12-31 00:00:00',
  `tweeter_list` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


CREATE TABLE `tb_user_profile` (
  `msisdn` varchar(15) NOT NULL,
  `lang` varchar(20) NOT NULL,
  `telco_id` varchar(20) NOT NULL,
  `state` enum('preactive','active','dormant','suspend','inactive','barred') NOT NULL DEFAULT 'active',
  `user_type` enum('premium','community','promoted','group','grp_modr') NOT NULL DEFAULT 'community',
  `created_ts` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `updated_ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `privacy` enum('public','private') NOT NULL DEFAULT 'public',
  `user_name` varchar(15) NOT NULL,
  `blog_box_size` smallint(6) NOT NULL DEFAULT '10',
  `new_inbox_size` smallint(6) NOT NULL DEFAULT '10',
  `heard_inbox_size` smallint(6) NOT NULL DEFAULT '10',
  `save_inbox_size` smallint(6) NOT NULL DEFAULT '10',
  `fwd_inbox_size` smallint(6) NOT NULL DEFAULT '10',
  `blog_box_ttl` smallint(6) NOT NULL DEFAULT '30',
  `new_inbox_ttl` smallint(6) NOT NULL DEFAULT '10',
  `heard_inbox_ttl` smallint(6) NOT NULL DEFAULT '10',
  `save_inbox_ttl` smallint(6) NOT NULL DEFAULT '30',
  `fwd_inbox_ttl` smallint(6) NOT NULL DEFAULT '10',
  `notify_pref` enum('sms','obd','email') NOT NULL DEFAULT 'sms',
  `email` varchar(40) DEFAULT NULL,
  `display_name` varchar(10) DEFAULT NULL,
  `tariff_id` smallint(6) NOT NULL DEFAULT '1',
  `password` varchar(10) DEFAULT NULL,
  `location` char(2) NOT NULL DEFAULT 'SG' COMMENT 'ISO2 country codes',
  `channel` enum('ivr','sms','cli','ussd','callback','facebook','twitter','web','ios','android','.*') NOT NULL DEFAULT 'ivr',
  `device_id` varchar(40) DEFAULT NULL COMMENT 'smart phone devide id',
  `user_desc` varchar(160) DEFAULT NULL,
  `profile_url` varchar(120) DEFAULT NULL COMMENT 'profile url',
  `intro_audio_url` varchar(120) DEFAULT NULL COMMENT 'introduction audio url',
  `image_url` varchar(120) DEFAULT NULL COMMENT 'profile avatar image',
  `current_location` varchar(160) DEFAULT NULL,
  `facebook_id` varchar(20) DEFAULT NULL COMMENT 'facebook account id',
  `facebook_username` varchar(40) DEFAULT NULL,
  `facebook_screenname` varchar(40) DEFAULT NULL,
  `twitter_username` varchar(40) DEFAULT NULL,
  `facebook_token` varchar(260) DEFAULT NULL,
  `twitter_id` int(11) DEFAULT '1',
  `twitter_token` varchar(260) DEFAULT NULL,
  `twitter_token_secret` varchar(260) DEFAULT NULL,
  `twitter_screenname` varchar(40) DEFAULT NULL,
  `block_list` text,
  PRIMARY KEY (`msisdn`),
  UNIQUE KEY `up_uname` (`user_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


