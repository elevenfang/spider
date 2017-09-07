package com.elevenfang.blog.config;

import org.springframework.context.annotation.Configuration;

import com.elevenfang.blog.constant.BlogConstant;
import com.google.inject.AbstractModule;
import com.google.inject.name.Names;
import com.mongodb.MongoClient;

public class BlogModule extends AbstractModule {

	@Override
	protected void configure() {
		bindDB();
	}

	private void bindDB() {
		MongoClient client = new MongoClient("127.0.0.1", 27017);
		bind(MongoClient.class).annotatedWith(Names.named(BlogConstant.BLOG_MONGO_DB_NAME)).toInstance(client);

	}

}
