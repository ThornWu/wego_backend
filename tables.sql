CREATE TABLE `user` (
	`userid`	integer(13),
	`username`	varchar(30) NOT NULL UNIQUE,
	`password`	varchar(64) NOT NULL,
	`email`	varchar(30) NOT NULL,
	`gender`	boolean NOT NULL,
	`profile`	varchar(30),
	`homecity`	varchar(30),
	'la_label' integer(4) default -2,
	'ny_label' integer(4) default -2,
	'isused' boolean default True,
	PRIMARY KEY(userid)
);

CREATE TABLE `venue` (
	`venueid`	varchar(24),
	`venuename`varchar(50) NOT NULL,
	`category`	varchar(24) NOT NULL,
	`latitude`	double NOT NULL,
	`longitude` double NOT NULL,
	`address`	varchar(100),
	`localcity`	varchar(30),
	'la_label' integer(4) default -2,
	'ny_label' integer(4) default -2,
	'isused' boolean default True,
	PRIMARY KEY(venueid)
);

CREATE TABLE `tip` (
	`userid` integer(13) NOT NULL,
	`venueid` varchar(24) NOT NULL,
	`createtime` integer(10) NOT NULL,
	PRIMARY KEY(userid,venueid,createtime)
);

CREATE TABLE `friendship` (
	`usera`	integer(13) NOT NULL,
	`userb` integer(13) NOT NULL,
	PRIMARY KEY(usera,userb)
);

CREATE TABLE `category` (
	`categoryid` varchar(24) primary key,
	`categoryname` varchar(30) not null,
	`parentid` varchar(24) not null
);

CREATE TABLE `favorite` (
	`userid` integer(13) not null,
	`venueid` varchar(24) not null,
	`createtime` integer(10) not null,
	PRIMARY KEY(userid,venueid)
);

CREATE TABLE `admin` (
	`username` varchar(30) NOT NULL UNIQUE,
	`password` varchar(64) NOT NULL,
	PRIMARY KEY(username)
);
