package com.tps.springboot.service.impl;

import cn.hutool.crypto.SecureUtil;
import com.tps.springboot.entity.User;
import com.tps.springboot.mapper.UserMapper;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

class UserServiceImplTest {

    @Test
    void preparePasswordForSaveIgnoresBlankPassword() {
        UserServiceImpl service = new UserServiceImpl();
        UserMapper userMapper = mock(UserMapper.class);
        ReflectionTestUtils.setField(service, "userMapper", userMapper);
        User user = new User();
        user.setId(1);
        user.setPassword("");

        service.preparePasswordForSave(user);

        assertNull(user.getPassword());
        verify(userMapper, never()).selectById(1);
    }

    @Test
    void preparePasswordForSavePreservesExistingPasswordHash() {
        UserServiceImpl service = new UserServiceImpl();
        UserMapper userMapper = mock(UserMapper.class);
        ReflectionTestUtils.setField(service, "userMapper", userMapper);
        String existingHash = SecureUtil.md5("secret");
        User existing = new User();
        existing.setPassword(existingHash);
        User user = new User();
        user.setId(1);
        user.setPassword(existingHash);
        when(userMapper.selectById(1)).thenReturn(existing);

        service.preparePasswordForSave(user);

        assertNull(user.getPassword());
    }

    @Test
    void preparePasswordForSaveHashesNewPlaintextPassword() {
        UserServiceImpl service = new UserServiceImpl();
        UserMapper userMapper = mock(UserMapper.class);
        ReflectionTestUtils.setField(service, "userMapper", userMapper);
        User existing = new User();
        existing.setPassword(SecureUtil.md5("old-password"));
        User user = new User();
        user.setId(1);
        user.setPassword("new-password");
        when(userMapper.selectById(1)).thenReturn(existing);

        service.preparePasswordForSave(user);

        assertEquals(SecureUtil.md5("new-password"), user.getPassword());
    }
}
