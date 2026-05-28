package com.tps.springboot.utils;

import com.tps.springboot.common.Constants;
import com.tps.springboot.entity.User;
import com.tps.springboot.exception.ServiceException;

public final class AuthUtils {

    private AuthUtils() {
    }

    public static User requireLogin() {
        User currentUser = TokenUtils.getCurrentUser();
        if (currentUser == null) {
            throw new ServiceException(Constants.CODE_401, "无token，请重新登录");
        }
        return currentUser;
    }
}
