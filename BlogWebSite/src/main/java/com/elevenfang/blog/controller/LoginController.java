package com.elevenfang.blog.controller;

import java.util.ArrayList;
import java.util.List;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import com.elevenfang.blog.model.User;
import com.elevenfang.blog.mongo.impl.UserMongoServiceImpl;
import com.google.inject.Inject;

@Controller
public class LoginController {

	private final Logger logger = LoggerFactory.getLogger(getClass());

	@Inject
	private UserMongoServiceImpl mongoServiceImpl;

	private static List<User> users = new ArrayList<>();
	static {
		users.add(new User("zhangsan", "1223456"));
		users.add(new User("lisi", "666666"));
		users.add(new User("wangwu", "888888"));
		users.add(new User("zhaoliu", "999999"));
	}

	@RequestMapping(value = "/login", method = RequestMethod.GET)
	public String init(@ModelAttribute("model") ModelMap model) {
		model.addAttribute("userList", users);
		return "login";
	}

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	public String login(@ModelAttribute("user") User user) {
		if (isNotNullUser(user)) {
			long sequence = mongoServiceImpl.getNextSequence("User");
			logger.info("sequence:{}", sequence);
			users.add(user);
		}
		return "redirect:/login";

	}

	private boolean isNotNullUser(User user) {
		return null != user && StringUtils.isNotEmpty(user.getUserName())
				&& StringUtils.isNotEmpty(user.getUserPasswd());
	}

}
