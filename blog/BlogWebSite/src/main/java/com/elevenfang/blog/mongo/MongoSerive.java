package com.elevenfang.blog.mongo;

import java.lang.reflect.ParameterizedType;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

import org.jongo.Jongo;
import org.jongo.MongoCollection;
import org.jongo.MongoCursor;
import org.jongo.marshall.jackson.JacksonMapper;
import org.slf4j.LoggerFactory;
import org.slf4j.Logger;

import com.elevenfang.blog.constant.BlogConstant;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.MapperFeature;
import com.google.inject.Injector;
import com.google.inject.Key;
import com.google.inject.name.Names;
import com.mongodb.DB;
import com.mongodb.MongoClient;

public abstract class MongoSerive<T> {

	public Logger logger = LoggerFactory.getLogger(getClass());

	private Class<T> kind;

	private static final Object[] NO_PARAMETERS = {};

	private MongoCollection mongoSequence;

	private Injector inject;

	@SuppressWarnings("unchecked")
	public MongoSerive() {
		this.kind = (Class<T>) ((ParameterizedType) this.getClass().getGenericSuperclass()).getActualTypeArguments()[0];
	}

	public void insert(T t) {
		int N = this.getCollection().insert(t).getN();
		logger.info("success insert record:{}", N);
	}

	public void batchInsert(List<T> targets) {
		int N = this.getCollection().insert(targets).getN();
		logger.info("success batch insert record:{}", N);
	}

	public T findOne(String query) {
		return this.findOne(query, NO_PARAMETERS);
	}

	protected T findOne(String query, Object... objects) {
		return this.getCollection().findOne(query, NO_PARAMETERS).as(kind);
	}

	protected int remove(String query) {
		return this.remove(query, NO_PARAMETERS);
	}

	protected int remove(String query, Object[] noParameters) {
		return this.getCollection().remove(query, NO_PARAMETERS).getN();
	}

	protected int update(T newValue, String query) {
		return this.update(newValue, query, NO_PARAMETERS);
	}

	protected int update(T newValue, String query, Object... objects) {
		return this.getCollection().update(query, objects).with(newValue).getN();
	}

	protected int upSert(T newValue, String query, Object... objects) {
		return this.getCollection().update(query, objects).upsert().with(newValue).getN();
	}

	protected List<T> queryForList(String query) {
		return this.cursorList(this.getCollection().find(query, NO_PARAMETERS).as(kind));
	}

	protected List<T> queryForList(String query, Object... objects) {
		return this.cursorList(this.getCollection().find(query, objects).as(kind));
	}

	protected List<T> queryForListByAscSorted(String query, String sortFieldName, Object... objects) {
		return this.cursorList(this.getCollection().find(query, objects).sort("{" + sortFieldName + ": -1}").as(kind));
	}

	protected List<T> queryForListByDescSorted(String query, String sortFieldName, Object... objects) {
		return this.cursorList(this.getCollection().find(query, objects).sort("{" + sortFieldName + ": 1}").as(kind));
	}

	protected long getCount(String query) {
		return this.getCollection().count(query, NO_PARAMETERS);
	}

	protected long getCount(String query, Object... objects) {
		return this.getCollection().count(query, objects);
	}

	private List<T> cursorList(MongoCursor<T> cursor) {
		List<T> list = new ArrayList<>();
		Iterator<T> iterator = cursor.iterator();
		while (iterator.hasNext()) {
			list.add(iterator.next());
		}
		return list;
	}

	public String getCollectionName() {
		return kind.getSimpleName();
	}

	protected MongoCollection getCollection() {
		String collectionName = getCollectionName();
		return this.getJongo().getCollection(collectionName);
	}

	private Jongo getJongo() {
		MongoClient client = inject
				.getInstance(Key.get(MongoClient.class, Names.named(BlogConstant.BLOG_MONGO_DB_NAME)));
		DB db = client.getDB(BlogConstant.BLOG_MONGO_DB_NAME);
		return new Jongo(db,
				new JacksonMapper.Builder().enable(MapperFeature.AUTO_DETECT_SETTERS)
						.enable(MapperFeature.AUTO_DETECT_GETTERS)
						.disable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES).build());
	}

	protected long getNextSequence(String sequenceName) {
		if (mongoSequence == null) {
			mongoSequence = this.getJongo().getCollection(MongoSequence.class.getSimpleName());
		}
		return mongoSequence.findAndModify("{name:#}", sequenceName).with("{$inc:{value:1}}").as(MongoSequence.class)
				.getValue();
	}

	public Injector getInject() {
		return inject;
	}

	public void setInject(Injector inject) {
		this.inject = inject;
	}

}
