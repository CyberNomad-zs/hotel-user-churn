package com.tps.springboot.service.impl;

import cn.hutool.crypto.SecureUtil;
import com.tps.springboot.common.Constants;
import com.tps.springboot.entity.User;
import com.tps.springboot.exception.ServiceException;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

class UserServiceImplTest {

    @Test
    void insertHashesPlaintextPassword() {
        User incoming = new User();
        incoming.setPassword("secret");

        UserServiceImpl.preparePasswordForSave(incoming, null);

        assertEquals(SecureUtil.md5("secret"), incoming.getPassword());
    }

    @Test
    void insertRejectsBlankPassword() {
        User incoming = new User();
        incoming.setPassword("");

        ServiceException exception = assertThrows(
                ServiceException.class,
                () -> UserServiceImpl.preparePasswordForSave(incoming, null)
        );

        assertEquals(Constants.CODE_400, exception.getCode());
    }

    @Test
    void updateKeepsPasswordWhenClientEchoesExistingHash() {
        String existingHash = SecureUtil.md5("old-password");
        User existing = new User();
        existing.setPassword(existingHash);
        User incoming = new User();
        incoming.setPassword(existingHash);

        UserServiceImpl.preparePasswordForSave(incoming, existing);

        assertNull(incoming.getPassword());
    }

    @Test
    void updateKeepsPasswordWhenPasswordIsOmitted() {
        User existing = new User();
        existing.setPassword(SecureUtil.md5("old-password"));
        User incoming = new User();

        UserServiceImpl.preparePasswordForSave(incoming, existing);

        assertNull(incoming.getPassword());
    }

    @Test
    void updateHashesNewPlaintextPassword() {
        User existing = new User();
        existing.setPassword(SecureUtil.md5("old-password"));
        User incoming = new User();
        incoming.setPassword("new-password");

        UserServiceImpl.preparePasswordForSave(incoming, existing);

        assertEquals(SecureUtil.md5("new-password"), incoming.getPassword());
    }
}
