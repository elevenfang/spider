package com.elevenfang.blog.mongo.impl;

import java.util.List;

import com.elevenfang.blog.model.User;
import com.elevenfang.blog.mongo.MongoSerive;

public class UserMongoServiceImpl extends MongoSerive<User> {

	public void batchInsertUser(List<User> users) {
		super.batchInsert(users);
	}

	public void sigleInsertUser(User user) {
		super.insert(user);
	}

	public long getNextSequence(String sequenceName) {
		long sequence = super.getNextSequence(sequenceName);
		logger.info("sequence number:{}", sequence);
		return sequence;
	}
}
