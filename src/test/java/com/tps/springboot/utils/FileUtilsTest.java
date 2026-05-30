package com.tps.springboot.utils;

import com.tps.springboot.exception.ServiceException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.File;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class FileUtilsTest {

    @TempDir
    Path tempDir;

    @Test
    void resolveFileInBaseAcceptsFilesInsideBaseDirectory() throws Exception {
        File resolved = FileUtils.resolveFileInBase(tempDir.toString(), "avatar.png");

        assertEquals(tempDir.resolve("avatar.png").toAbsolutePath().normalize().toFile(), resolved);
        assertTrue(resolved.getAbsolutePath().startsWith(tempDir.toFile().getAbsolutePath()));
    }

    @Test
    void resolveFileInBaseRejectsPathTraversal() {
        assertThrows(ServiceException.class, () -> FileUtils.resolveFileInBase(tempDir.toString(), "../secret.txt"));
    }

    @Test
    void resolveFileInBaseRejectsAbsolutePathsOutsideBaseDirectory() {
        assertThrows(ServiceException.class, () -> FileUtils.resolveFileInBase(tempDir.toString(), "/etc/passwd"));
    }
}
