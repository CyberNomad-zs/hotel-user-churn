package com.tps.springboot.controller;

import com.tps.springboot.common.Constants;
import com.tps.springboot.exception.ServiceException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.api.io.TempDir;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.util.ReflectionTestUtils;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class FileControllerTest {

    @TempDir
    Path tempDir;

    @Mock
    private StringRedisTemplate stringRedisTemplate;

    private FileController fileController;

    @BeforeEach
    void setUp() {
        fileController = new FileController();
        ReflectionTestUtils.setField(fileController, "fileUploadPath", tempDir.toString() + File.separator);
        ReflectionTestUtils.setField(fileController, "serverIp", "localhost");
        ReflectionTestUtils.setField(fileController, "stringRedisTemplate", stringRedisTemplate);
    }

    @Test
    void uploadStoresSafeFilenameInsideConfiguredDirectory() throws Exception {
        byte[] content = "avatar".getBytes(StandardCharsets.UTF_8);
        MockMultipartFile file = new MockMultipartFile("file", "avatar.png", "image/png", content);

        String url = fileController.upload(file);

        assertEquals("http://localhost:9090/file/avatar.png", url);
        assertArrayEquals(content, Files.readAllBytes(tempDir.resolve("avatar.png")));
        verify(stringRedisTemplate).delete(Constants.FILES_KEY);
    }

    @Test
    void uploadRejectsPathTraversalFilename() {
        MockMultipartFile file = new MockMultipartFile("file", "../application.yml", "text/plain",
                "owned".getBytes(StandardCharsets.UTF_8));

        assertThrows(ServiceException.class, () -> fileController.upload(file));
    }
}
